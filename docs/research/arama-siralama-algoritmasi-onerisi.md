# Keşfet Plus — Arama/Sıralama (Relevance Ranking) Algoritması Önerisi

*Tarih: 2026-09-30 | Hazırlayan: Araştırma ajanı*

**Yöntem:** Bu rapor öncesinde `CLAUDE.md`, `frontend/src/screens/Home.jsx`,
`frontend/src/screens/ExploreAll.jsx`, `frontend/src/lib/data.js`,
`database/trust_scoring.py`, `database/checkins_store.py`, `api/main.py`,
`frontend/package.json` ve `docs/research/sonraki-adimlar-firsat-analizi.md` +
`ikinci-tur-firsat-analizi.md` (tekrar etmemek için — ikisinde de arama/sıralama
konusuna değinilmemiş, doğrulandı) okundu. Ayrıca gerçek seed verisi
(`database/seed/places.json`, `gurme.json`, `hotels.json`) Python ile
doğrudan sayıldı/incelendi (aşağıdaki "veri gerçekleri" bölümü buradan gelir).
2026 pratikleri için üç kütüphanenin resmî sayfaları `WebFetch` ile
doğrudan çekildi (bu oturumda `WebSearch` kotası — 200/200 — daha önceki
işler tarafından tüketilmiş olduğundan genel bir tarama yapılamadı; bunun
yerine adı bilinen, güncel ve yaygın kullanılan üç kütüphanenin resmî
dokümantasyonu tek tek doğrulandı, kaynaklar aşağıda).

---

## 1. Mevcut durum (kod kanıtlı)

**Arama/filtreleme bugün nasıl çalışıyor:** `Home.jsx` (satır 78-87) ve
`ExploreAll.jsx` (satır 48-56) **birebir aynı** mantığı iki kez tekrarlıyor:

```js
const filtered = venues.filter((v) => {
  if (category?.match && !category.match(v)) return false
  if (q && !`${v.name} ${v.area ?? ''}`.toLowerCase().includes(q)) return false
  return true
})
```

Bu, `.includes()` ile düz alt-dize eşleştirmesi — yazım hatasına sıfır
tolerans ("Belgrad" yazılırken "Belgart" hiçbir sonuç döndürmez), sadece
`name` + `area` alanlarına bakıyor (`tags`, gurme'nin `dish`/`category`
alanları aranmıyor), ve **sıralama yok**: sonuç `venues` dizisinin geldiği
sıradadır, yani `getAllVenues()`'ün birleştirdiği ham JSON dosya sırası
(`places.json` → `gurme.json` → `hotels.json`, her biri kendi içinde muhtemelen
ekleniş sırası). `Home.jsx` ekstra olarak `filtered.slice(0, 12)` ile ilk 12'yi
gösteriyor — yani bugün "hangi 12 mekan öne çıkıyor" sorusunun cevabı **tamamen
JSON dosyasındaki fiziksel konum**, alaka/kalite ile hiçbir ilgisi yok.

**Ölçek:** `database/seed/` bugün 182 doğa (`places.json`) + 234 gurme
(`gurme.json`) + 68 otel (`hotels.json`) = **484 mekan**. 32 mekanla bu önemsizdi
(ilk 12'lik ekran zaten yarısını kapsıyordu); 484'te `.slice(0, 12)` artık
mekanların **%2,5**'ini gösteriyor — hangi 12'nin göründüğü artık gerçek bir
ürün kararı.

**Mimari kısıt (kritik):** Arama tamamen **frontend'de, istemci tarafında**
çalışıyor. `frontend/src/lib/data.js`'deki `getAllVenues()` üç statik JSON
dosyasını doğrudan `fetch()` ile çekiyor (`/data/places.json` vb., Vite'ın
`public/` klasöründen servis ediliyor) — backend'in (`api/main.py`) mekan
listesiyle **hiçbir ilgisi yok**, `/places` gibi bir endpoint yok. Yani "arama
sunucusu" diye bir şey mimaride zaten yok ve **kurulması da önerilmiyor** —
Elasticsearch/Algolia/Typesense gibi bir arama motoru bu 484 kayıtlık,
tamamen istemci tarafında zaten çalışan mimariye hem gereksiz hem ters
(yeni bir servis, hesap, senkronizasyon problemi ekler).

**Kullanılmayan sinyaller (kod kanıtlı):**
- `venue.rating` bugün sadece kart üzerinde bir **rozet** olarak gösteriliyor
  (`Home.jsx` satır 212-217, `ExploreAll.jsx` satır 138-143) — sıralamada
  hiç kullanılmıyor.
- `database/checkins_store.py::count_recent_checkins()` sadece tek bir
  mekan için `GET /places/{place_id}/checkin-count` ile anlık hesaplanıyor
  (`api/main.py` satır 386-388) — 484 mekan için bunu tek tek çağırmak 484
  ayrı HTTP isteği demek, listede kullanılamaz haliyle.
- `helpful_count` (`checkins_store.py::toggle_helpful_status`,
  `comments_store.py::toggle_helpful_comment`) **yorum/durum bazında**
  tutuluyor, mekan bazında **toplanmış hiçbir sayaç yok** — "bu mekanın
  toplam helpful sayısı" diye bir alan/endpoint bugün mevcut değil.
- `_district_center()`/`_haversine_km()` (`checkins_store.py` satır 123-169)
  zaten check-in doğrulaması için haversine mesafe hesaplıyor, ama **sadece
  ilçe merkez koordinatına** göre (`_DISTRICT_LATLNG` sabit sözlüğü) — bunu
  doğrudan doğrulamak için üç seed dosyası da tarandı: **`places.json`,
  `gurme.json`, `hotels.json`'da tek bir kayıtta bile gerçek `lat`/`lng`
  alanı yok** (484 kaydın 484'ü de sadece `area` string'i taşıyor). Yani
  bugün "en yakın mekan" sorusunun cevabı en iyi ihtimalle **ilçe** hassasiyetinde
  olabilir, mekan-hassasiyetinde değil — bu, coğrafi sıralama önerisinin en
  önemli ön koşulu/sınırlaması (bkz. §4).
- `venue.rating`/`reviewCount` kapsamı da eşit değil — doğrudan sayıldı:
  `places.json`'da 182'nin 121'inde, `gurme.json`'da 234'ün sadece 93'ünde
  (yani en son eklenen ~141 gurme kaydında **yok**), `hotels.json`'da
  68'in **0'ında** rating var. Bu, "rating'e göre sırala" gibi saf bir
  yaklaşımın bugün mekanların büyük bir kısmını (özellikle tüm oteller ve
  yeni gurme eklentileri) sessizce en dibe iteceği anlamına gelir — CLAUDE.md'nin
  "sahte veri yasak" kuralı gereği eksik rating'i 0 veya uydurma bir
  ortalama ile doldurmak da yasak; aşağıdaki öneri bunu `trust_scoring.py`'nin
  zaten kurduğu "veri yoksa nötr puan" desenini tekrar kullanarak çözüyor.

---

## 2. Mevcut ilham kaynağı: `database/trust_scoring.py`

Proje zaten ilgili bir desen kurmuş durumda — kopyalanabilir, yeniden
icat etmeye gerek yok:

- **Ağırlıklı, toplamı 100 olan çoklu sinyal** (`ACCOUNT_SIGNAL_SCORE=30`,
  `LOCATION_SIGNAL_MAX=30`, `TEXT_SIGNAL_MAX=25`, `VELOCITY_SIGNAL_MAX=15`) —
  sabitler dosyanın en üstünde, tek yerden ayarlanabilir.
- **"Veri yoksa nötr, cezalandırma"** kuralı: GPS izni verilmemişse
  `LOCATION_SIGNAL_NEUTRAL` (tam puanın yarısı) veriliyor, sıfır değil —
  "izin vermeyen kullanıcı cezalandırılmasın" prensibi. Aynı prensip
  rating/reviewCount eksik olan mekanlar için doğrudan uyarlanabilir.
- **`difflib.SequenceMatcher`** (stdlib, ek bağımlılık yok) metin benzerliği
  için zaten kullanılıyor — ama bu **backend'de, Python'da**, yorum
  kopyala-yapıştır tespiti için. Arama istemci tarafında (React/JS) çalıştığı
  için bu kod doğrudan taşınamaz; JS tarafında eşdeğeri aşağıda önerilen
  kütüphanelerdir (§3). Kullanıcı görev tanımında önerilen `difflib`/TF-IDF
  fikri mimari olarak doğru yönde ama yanlış katmanda — bu raporun tashih
  ettiği tek öncül budur.
- **Kullanıcının önerdiği `rapidfuzz`** de aynı nedenle burada doğrudan
  uygulanamaz: resmî PyPI sayfası (`pypi.org/project/RapidFuzz/`, WebFetch ile
  doğrulandı) `rapidfuzz`'un "Python ve C++ için hızlı string eşleştirme
  kütüphanesi" olduğunu, pip/conda ile kurulduğunu belirtiyor — **tarayıcıda
  çalışan bir JS kütüphanesi değil**. Arama bugün tamamen frontend'de
  çalıştığı için `rapidfuzz` ancak arama backend'e taşınırsa anlamlı olur
  (bkz. §5, "neden önerilmiyor").

---

## 3. Öneri 1 — Yazım hatası toleranslı, ağırlıklı metin arama (istemci tarafında)

**Yaklaşım:** Mevcut `.toLowerCase().includes()` mantığını, saf JavaScript ile
çalışan, sunucu/derleme adımı gerektirmeyen hafif bir kütüphaneyle
değiştirmek. Üç aday araştırıldı (resmî sayfaları `WebFetch` ile
doğrudan doğrulandı):

| Kütüphane | Boyut (gzip) | Bağımlılık | Yazım hatası toleransı | Ağırlıklı alan desteği |
|---|---|---|---|---|
| **Fuse.js** | ~6.8–8.6 kB | 0 | Var (Bitap algoritması) | Var (`weighted keys`) |
| **match-sorter** | küçük (npm) | 0 | Yok — deterministik 7 kademeli kural (tam eşleşme → başlar → içerir → kısaltma → sıralı harf) | Var (`keys` sırası önceliği belirler) |
| **MiniSearch** | küçük, "tiny" (proje kendi ifadesi) | 0 | Var ("fuzzy match") | Var ("field boosting") |

Kaynaklar: [Fuse.js](https://www.fusejs.io/), [match-sorter (GitHub)](https://github.com/kentcdodds/match-sorter),
[MiniSearch](https://lucaong.github.io/minisearch/).

**Öneri: Fuse.js.** Gerekçe:
1. Zero-dependency, ~7-9 kB gzip — `frontend/package.json`'daki en küçük
   bağımlılıktan (`lucide-react`) bile küçük, bundle'a önemli bir yük
   getirmiyor.
2. `weighted keys` doğrudan bu projenin karışık şemasına uyuyor — üç seed
   dosyasının alan adları farklı (`places.json`'da `tags` bir dizi;
   `gurme.json`'da `dish`/`category` birer string; `hotels.json`'da ikisi de
   yok, sadece `name`/`area`/`address`). Fuse.js'e verilecek `keys` listesi
   örn. `[{name:'name', weight:0.6}, {name:'area', weight:0.2},
   {name:'tags', weight:0.1}, {name:'dish', weight:0.1},
   {name:'category', weight:0.1}]` gibi — olmayan alan sorun çıkarmaz,
   Fuse.js eksik alanı atlar.
3. Bitap tabanlı fuzzy eşleştirme "Belgrat" → "Belgrad", "Yılmz" → "Yılmaz"
   gibi tek/iki karakterlik yazım hatalarını tolere eder — kullanıcı
   isteğindeki "yazım hatası toleransı" ihtiyacını backend'siz karşılar.
4. Sonuç zaten bir **skor** döndürüyor (0 = mükemmel eşleşme, 1 = alakasız) —
   bu skor, aşağıdaki §5'teki birleşik sıralama formülünün "metin alaka"
   girdisi olarak doğrudan kullanılabilir.

**match-sorter neden ikinci sırada:** Kuralları daha "anlaşılır" (kullanıcı
"neden bu sonuç üstte" sorusuna sezgisel cevap bulur, matematik skor yok) ama
yazım hatası toleransı **yok** — kullanıcı görev tanımının açık isteği olan
"typo tolerance" ihtiyacını karşılamıyor, bu yüzdenFuse.js'e tercih
edilmiyor. MiniSearch daha güçlü (tam bir ters-index arama motoru, prefix +
fuzzy + boosting) ama bu proje ölçeğinde (484 kayıt, tek seferde belleğe
sığan) Fuse.js'in sunduğunun ötesinde bir kapasiteye ihtiyaç yok; MiniSearch
daha çok binlerce/on binlerce kayıtlı, gerçek "tam metin arama" gerektiren
projeler için daha net bir kazanç sağlar.

**Değişecek dosyalar (somut):**
- `frontend/package.json` — `fuse.js` bağımlılığı eklenir (tek npm paketi).
- Yeni bir `frontend/src/lib/search.js` — hem `Home.jsx` hem
  `ExploreAll.jsx`'in bugün **birebir kopyaladığı** `filtered` mantığını
  tek yerde toplayan bir `rankVenues(venues, query, category, opts)`
  fonksiyonu. Bu aynı zamanda mevcut bir kod tekrarını (DRY ihlali) de
  çözer — bugün iki ekran aynı filtre mantığını iki kez tutuyor, bu
  refactor'la tek kaynağa iner.
- `Home.jsx` (satır 78-87) ve `ExploreAll.jsx` (satır 48-56) — kendi
  `useMemo` bloklarını `rankVenues(...)` çağrısına indirger.

---

## 4. Öneri 2 — Popülerlik/etkileşim skoru (gerçek sinyaller, yeni veri uydurmadan)

**Kullanılabilir gerçek sinyaller (öncelik sırasıyla):**
1. `rating`/`reviewCount` — halihazırda seed verisinde var ama **kısmi**
   (yukarıdaki sayım: places 121/182, gurme 93/234, hotels 0/68).
2. `checkin_count` — `checkins_store.py::count_recent_checkins()` zaten
   var, ama sadece tek-mekan endpoint'i (`GET /places/{id}/checkin-count`)
   olarak. Listede kullanmak için **toplu** bir versiyon gerekir.
3. `helpful_count` — yorum/durum bazında tutuluyor, mekan bazında toplanmış
   değil; bir mekanın tüm yorumlarının/durumlarının `helpful_count` toplamı
   alınarak türetilebilir (yeni veri değil, var olan veriden toplama).

**Neden şimdi bir batch endpoint gerekiyor:** 484 mekan için popülerlik
verisini tek tek çekmek (484 ayrı `fetch`) hem yavaş hem gereksiz yük.
Proje zaten bu deseni biliyor: `GET /users/{id}/stats` ve `GET
/moderation/stats` (bkz. `ikinci-tur-firsat-analizi.md` madde 6) **hiçbir
şeyi saklamadan, her çağrıda gerçek veriden anlık hesaplıyor** ("never
stored, so it can't drift from reality" — `api/main.py` docstring'i).
Aynı prensiple, tek bir yeni salt-okunur endpoint önerilir:

```
GET /places/popularity-scores
→ { "<place_id>": { "checkin_count": N, "helpful_count": M }, ... }
```

Bu, `checkins_store.py`'deki `count_all_checkins()`/
`list_place_ids_with_activity()` desenlerinin bir varyasyonu olarak
(place_id'ye göre gruplanmış toplam) kolayca yazılabilir — yeni bir store,
yeni bir tablo, yeni bir hesap gerekmiyor; var olan `checkins.json`/
`status.json`/`comments.json` dosyaları üzerinde tek geçişlik bir toplama.
Frontend bunu liste ekranı açılışında **bir kez** çeker (`data.js`'e
`getPopularityScores()` gibi bir fonksiyon), venue nesnelerine `merge`
eder.

**Eksik veri için puanlama kuralı (trust_scoring.py deseninin tekrarı):**
`rating` yoksa 0 puan **değil**, o sinyal için nötr/ortalama bir değer
verilmeli — tıpkı `trust_scoring.py`'deki `LOCATION_SIGNAL_NEUTRAL`
gibi. Örn. `rating` yoksa o venue'nün popülerlik skorunun rating bileşeni,
rating'i olan venue'lerin **medyanı** (sabit uydurma bir sayı değil, gerçek
veriden türetilmiş bir referans) olarak alınabilir — bu hem "sahte veri
yasak" kuralını ihlal etmez (hiçbir venue'ye "4.2 yıldız" gibi var olmayan
bir değer yazılmaz, sadece sıralama hesabında geçici bir referans noktası
kullanılır) hem de rating'i olmayan ~%40 mekanı listenin dibine
gömülmekten korur.

---

## 5. Öneri 3 — Coğrafi yakınlık (GPS varsa)

**Bugünkü GPS kullanım deseni (kod kanıtlı):** `PlaceDetail.jsx`'te
`navigator.geolocation.getCurrentPosition()` **sadece** check-in ve
yorum-gönderme gibi açık kullanıcı eylemlerinde çağrılıyor (satır 239,
297) — uygulama açılışında veya liste ekranlarında **proaktif olarak
istenmiyor**. Bu tutarlı, iyi bir gizlilik deseni; coğrafi sıralama
eklenirse bu deseni bozmamak (Home/ExploreAll açılışında otomatik izin
istemi göstermemek) önemli.

**Önerilen uygulama:** Liste ekranına **opt-in** bir "yakınıma göre sırala"
seçeneği/anahtarı eklemek — kullanıcı bunu açıkça seçtiğinde GPS izni
istenir (tıpkı check-in akışındaki gibi tek seferlik `getCurrentPosition`
çağrısı), verilen konum `_haversine_km` ile (aynı formül, `checkins_store.py`
satır 163-169'dan frontend'e JS olarak taşınır — basit bir matematik
fonksiyonu, kütüphane gerekmez) her venue'nün `area` alanına karşılık gelen
ilçe merkezine olan mesafeye göre bir yakınlık skoru üretir.

**Önemli sınırlama (dürüstçe belirtilmeli):** §1'de doğrulandığı gibi seed
verisinde **hiçbir venue'nün gerçek `lat`/`lng`'i yok** — bugün mevcut olan
tek coğrafi veri `area` (ilçe adı) string'i. Yani bu öneri en iyi ihtimalle
**ilçe-seviyesi** hassasiyette çalışır ("Beşiktaş'tasın, Beşiktaş'taki
mekanlar öne çıkar" — ama Beşiktaş içindeki iki mekan arasında ayrım
yapamaz). Mekan-seviyesi gerçek yakınlık sıralaması için önce her venue'ye
gerçek koordinat eklenmesi gerekir — bu bir veri-toplama projesidir, kod
değişikliği değil. `agents/scout_agent.py` zaten `GOOGLE_PLACES_API_KEY`
üzerinden Google Places API'ye bağlanabiliyor (opsiyonel, key yoksa
`not_configured` dönüyor) — eğer bu key bir noktada gerçekten kurulursa,
mevcut mekanlara koordinat eklemek için doğal bir kaynak olur, ama bu
**bu raporun kapsamı dışında bir sonraki adım** olarak not ediliyor,
şimdi kurulması önerilmiyor (hesap/kota gerektirir, "API key gerektirmeyen
çözümlere öncelik ver" kısıtıyla çelişir).

**Sonuç:** Faz 1'de ilçe-merkezli kaba yakınlık (ücretsiz, mevcut koda
dayanır) makul bir ilk adım; gerçek mekan-hassasiyetinde sıralama, gerçek
koordinat verisi eklenene kadar ertelenmeli.

---

## 6. Birleşik sıralama formülü (öneri, kod değil)

`trust_scoring.py`'nin ağırlıklı-toplam desenine paralel, basit ve
açıklanabilir bir formül (makine öğrenmesi/karmaşık model **önerilmiyor** —
484 kayıt ve sıfır gerçek kullanıcı-davranış geçmişiyle bir ML modelini
eğitecek veri yok, over-engineering olur):

```
score = W_text   * textMatchScore     (Fuse.js skoru, 0=mükemmel → 1'e çevrilir: 1 - fuseScore)
      + W_pop     * popularityScore   (rating/reviewCount + checkin/helpful, normalize 0-1)
      + W_geo     * proximityScore    (opt-in GPS varsa; yoksa bu terim 0 ağırlıkla devre dışı)
```

- Arama kutusu **boşken** (kategori taraması / ana sayfa "Sana Özel
  Seçimler"): `W_text = 0`, sıralama tamamen popülerlik + (varsa) yakınlık.
- Arama kutusu **doluyken**: `W_text` baskın, popülerlik sadece eşit
  alaka düzeyindeki sonuçlar arasında ayırt edici (tie-breaker) olarak
  küçük ağırlıkla katkı verir — kullanıcı "Belgrad" yazdığında en popüler
  ama alakasız bir mekanın üste çıkmaması için.
- Ağırlıklar `trust_scoring.py`'deki gibi dosyanın en üstünde adlandırılmış
  sabitler olarak tutulmalı (`frontend/src/lib/search.js` içinde), tek
  yerden ayarlanabilir.

---

## 7. Somut değişiklik özeti

| Dosya | Değişiklik | Yeni bağımlılık |
|---|---|---|
| `frontend/package.json` | `fuse.js` eklenir | npm paketi, ~7-9 kB gzip |
| `frontend/src/lib/search.js` (yeni) | `rankVenues()` — metin + popülerlik + (opsiyonel) yakınlık birleşik skoru; iki ekranın tekrar eden filtre mantığını da birleştirir | — |
| `frontend/src/lib/data.js` | `getPopularityScores()` eklenir (yeni endpoint'i çeker) | — |
| `frontend/src/screens/Home.jsx` | `filtered` → `rankVenues(...)` çağrısı | — |
| `frontend/src/screens/ExploreAll.jsx` | Aynı | — |
| `database/checkins_store.py` | `count_checkins_by_place()` gibi toplu (tüm place_id'ler için tek geçiş) bir fonksiyon — mevcut `count_all_checkins()`'in varyasyonu | — |
| `database/comments_store.py` | Mekan bazlı toplam `helpful_count` toplayan bir fonksiyon | — |
| `api/main.py` | `GET /places/popularity-scores` (yeni, salt-okunur, auth gerekmez — mevcut public `GET /places/{id}/checkin-count` ile aynı görünürlük seviyesi) | — |
| (opsiyonel, Faz 3) `PlaceDetail.jsx` deseni referans alınarak liste ekranına opt-in "yakınıma göre" anahtarı | GPS izni sadece kullanıcı açıkça isterse | — |

**Hesap/API key gerektiren hiçbir öneri yok** — Fuse.js, MiniSearch,
match-sorter üçü de npm paketleri (ücretsiz, hesapsız); popülerlik endpoint'i
var olan JSON store'ları okuyor; ilçe-merkezli yakınlık var olan
`_DISTRICT_LATLNG` sözlüğünü kullanıyor. Gerçek mekan-koordinatı (Faz 3,
şimdi önerilmiyor) tek olası "hesap gerektirebilir" adım.

---

## 8. Aşamalandırma önerisi

1. **Faz 1 (en ucuz, hemen yapılabilir):** Fuse.js ile istemci-taraflı
   yazım-hatası-toleranslı, ağırlıklı metin araması + iki ekranın tekrar
   eden filtre kodunun `search.js`'e taşınması. Sıfır backend değişikliği,
   sıfır hesap.
2. **Faz 2:** `GET /places/popularity-scores` batch endpoint'i + mevcut
   `rating`/`reviewCount`'u eksik-veri-nötr kuralıyla birleştiren popülerlik
   skoru. Var olan "never stored, always recomputed" deseninin (moderasyon/
   kullanıcı istatistikleri) doğrudan devamı.
3. **Faz 3 (veri kalitesi önkoşullu, şimdi önerilmiyor):** Gerçek
   mekan-koordinatı toplanması (manuel veya Google Places API ile) + opt-in
   GPS'e dayalı mekan-hassasiyetinde yakınlık sıralaması. İlçe-merkezli kaba
   versiyon (Faz 1-2 ile birlikte, ücretsiz) bu fazın öncesinde bir ara adım
   olarak eklenebilir.

---

## Kaynaklar

- [Fuse.js — resmî site](https://www.fusejs.io/) — bundle boyutu, Bitap
  fuzzy algoritması, ağırlıklı anahtar (`weighted keys`) desteği.
- [match-sorter — GitHub](https://github.com/kentcdodds/match-sorter) —
  7 kademeli deterministik sıralama kuralı, fuzzy skor **yok**.
- [MiniSearch — resmî site](https://lucaong.github.io/minisearch/) —
  sıfır bağımlılıklı, tarayıcı-içi tam metin arama motoru, prefix + fuzzy +
  field boosting.
- [RapidFuzz — PyPI](https://pypi.org/project/RapidFuzz/) — Python/C++
  kütüphanesi olduğu, tarayıcıda çalışan bir JS kütüphanesi olmadığı
  doğrulandı (bu raporun kullanıcı-görev-tanımındaki öncülü düzelttiği
  nokta).
- Repo-içi: `database/trust_scoring.py` (ağırlıklı çoklu-sinyal + "veri
  yoksa nötr" deseni), `database/checkins_store.py` (`_haversine_km`,
  `_district_center`, `count_all_checkins` — yeniden kullanılabilir
  desenler), `api/main.py` (`GET /users/{id}/stats`, `GET
  /moderation/stats` — "never stored, always recomputed" deseni).
