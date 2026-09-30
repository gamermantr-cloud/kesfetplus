/**
 * Shared arama + sıralama mantığı - önceden Home.jsx (satır ~78-87) ve
 * ExploreAll.jsx (satır ~48-56) birebir aynı basit `.includes()` filtresini
 * iki kez tutuyordu (yazım hatasına sıfır tolerans, sadece name+area
 * aranıyordu, sıralama yoktu - sonuç JSON dosya sırasıydı). Bkz.
 * docs/research/arama-siralama-algoritmasi-onerisi.md - bu dosya o raporun
 * Faz 1 + Faz 2 önerisinin uygulanması.
 *
 * Fuse.js (zero-dependency, ~7-9 kB gzip, Bitap fuzzy algoritması) yazım
 * hatası toleransı sağlıyor - "Belgart" yazınca "Belgrad" hâlâ bulunuyor.
 */
import Fuse from 'fuse.js'

// Ağırlıklı alanlar - üç seed dosyasının şeması farklı (places.json'da
// `tags` bir dizi; gurme.json'da `dish`/`category` birer string;
// hotels.json'da ikisi de yok). Fuse.js eksik alanı sorunsuz atlar.
const FUSE_KEYS = [
  { name: 'name', weight: 0.5 },
  { name: 'area', weight: 0.2 },
  { name: 'tags', weight: 0.1 },
  { name: 'dish', weight: 0.1 },
  { name: 'category', weight: 0.1 },
]

const FUSE_OPTIONS = {
  keys: FUSE_KEYS,
  includeScore: true,
  threshold: 0.4, // ne kadar büyükse o kadar toleranslı (0 = tam eşleşme şart)
  distance: 100,
  ignoreLocation: true, // eşleşme alan içinde herhangi bir yerde olabilir
  minMatchCharLength: 2,
}

// Birleşik sıralama formülü ağırlıkları (rapor §6):
// score = W_text * textMatchScore + W_pop * popularityScore
// Arama kutusu boşken tamamen popülerliğe, doluyken ağırlıklı olarak metin
// alakasına göre sıralanır (popülerlik sadece eşit alaka düzeyinde
// tie-breaker).
const WEIGHT_TEXT_WITH_QUERY = 0.8
const WEIGHT_POPULARITY_WITH_QUERY = 0.2

// Popülerlik skorunun alt bileşenleri (toplamı 1) - trust_scoring.py'deki
// "adlandırılmış sabit, tek yerden ayarlanabilir ağırlık" deseninin aynısı.
const POPULARITY_WEIGHT_RATING = 0.5
const POPULARITY_WEIGHT_CHECKIN = 0.3
const POPULARITY_WEIGHT_HELPFUL = 0.2

function popularityMaxes(venues, popularityScores) {
  let maxCheckin = 0
  let maxHelpful = 0
  if (popularityScores) {
    for (const v of venues) {
      const stats = popularityScores[v.id]
      if (!stats) continue
      if (stats.checkin_count > maxCheckin) maxCheckin = stats.checkin_count
      if (stats.helpful_count > maxHelpful) maxHelpful = stats.helpful_count
    }
  }
  return { maxCheckin, maxHelpful }
}

/**
 * MUTLAK KURAL (CLAUDE.md "sahte veri yasak"): bir venue için hiçbir gerçek
 * sinyal yoksa (rating de yok, checkin de yok, helpful de yok) bu fonksiyon
 * 0 döner - "popüler" diye uydurma bir puan verilmez. 0 puanlı venue'ler
 * birbirine göre Array.prototype.sort'un stabil olması sayesinde JSON'daki
 * orijinal göreli sırasını korur, yani gerçek sinyali olmayan bir mekan ne
 * yapay olarak öne çıkar ne de cezalandırılır - nötr kalır.
 */
function popularityScore(venue, popularityScores, maxCheckin, maxHelpful) {
  const stats = popularityScores?.[venue.id]
  const ratingComponent = typeof venue.rating === 'number' ? venue.rating / 5 : 0
  const checkinComponent = stats && maxCheckin > 0 ? (stats.checkin_count ?? 0) / maxCheckin : 0
  const helpfulComponent = stats && maxHelpful > 0 ? (stats.helpful_count ?? 0) / maxHelpful : 0
  return (
    POPULARITY_WEIGHT_RATING * ratingComponent +
    POPULARITY_WEIGHT_CHECKIN * checkinComponent +
    POPULARITY_WEIGHT_HELPFUL * helpfulComponent
  )
}

/**
 * Venue listesini kategori + yazım-hatası-toleranslı metin sorgusuna göre
 * filtreler, gerçek sinyallere göre sıralar.
 *
 * @param {Array} venues - getAllVenues() çıktısı.
 * @param {Object} opts
 * @param {string} [opts.query] - arama kutusu metni.
 * @param {{match:(v:object)=>boolean}} [opts.category] - CATEGORIES'ten seçili kategori.
 * @param {Object} [opts.popularityScores] - getPopularityScores() çıktısı: { [place_id]: {checkin_count, helpful_count} }.
 * @param {string} [opts.excludeId] - örn. Home.jsx'in öne çıkan kartı - sonuçtan çıkarılır.
 * @returns {Array} sıralanmış, filtrelenmiş venue listesi.
 */
export function rankVenues(venues, { query = '', category, popularityScores, excludeId } = {}) {
  const trimmed = query.trim()
  const pool = venues.filter((v) => {
    if (category?.match && !category.match(v)) return false
    if (excludeId && v.id === excludeId) return false
    return true
  })

  const { maxCheckin, maxHelpful } = popularityMaxes(pool, popularityScores)
  const scoreOf = (v) => popularityScore(v, popularityScores, maxCheckin, maxHelpful)

  if (!trimmed) {
    // Arama yok - tamamen popülerlik sinyaline göre sırala (sinyali olmayan
    // mekanlar 0 puanla JSON'daki göreli sırasını korur, bkz. popularityScore).
    return pool
      .map((v, i) => ({ v, score: scoreOf(v), i }))
      .sort((a, b) => b.score - a.score || a.i - b.i)
      .map((e) => e.v)
  }

  const fuse = new Fuse(pool, FUSE_OPTIONS)
  return fuse
    .search(trimmed)
    .map(({ item, score: fuseScore }, i) => {
      const textScore = 1 - fuseScore // Fuse: 0=mükemmel eşleşme, 1=alakasız -> burada tersine çevrilir
      const combined =
        WEIGHT_TEXT_WITH_QUERY * textScore + WEIGHT_POPULARITY_WITH_QUERY * scoreOf(item)
      return { item, combined, i }
    })
    .sort((a, b) => b.combined - a.combined || a.i - b.i)
    .map((e) => e.item)
}
