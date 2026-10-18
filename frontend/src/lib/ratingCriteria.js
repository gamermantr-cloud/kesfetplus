/**
 * Yorum öncesi kategoriye-özel puanlama kriterleri. venue.kind'e göre
 * değişir (bkz. frontend/src/lib/data.js - 'place' | 'gurme' | 'hotel').
 * Puanlama isteğe bağlı; ortalamalar sadece gerçek kullanıcı yorumlarından
 * hesaplanır (bkz. ratingAverages aşağıda) - hiçbir sayı uydurulmaz.
 */
export const RATING_CRITERIA = {
  gurme: [
    { id: 'hijyen', label: 'Hijyen' },
    { id: 'lezzet', label: 'Lezzet' },
    { id: 'servis', label: 'Servis / garson iletişimi' },
    { id: 'fiyat_performans', label: 'Fiyat/performans' },
  ],
  hotel: [
    { id: 'temizlik', label: 'Temizlik' },
    { id: 'personel_ilgisi', label: 'Personel ilgisi' },
    { id: 'konfor', label: 'Konfor' },
    { id: 'lokasyon', label: 'Lokasyon' },
  ],
  place: [
    { id: 'temizlik', label: 'Temizlik' },
    { id: 'atmosfer', label: 'Atmosfer' },
    { id: 'guvenlik', label: 'Güvenlik' },
    { id: 'erisilebilirlik', label: 'Erişilebilirlik' },
  ],
  sahne: [
    { id: 'ses_gorus_kalitesi', label: 'Ses/Görüş kalitesi' },
    { id: 'atmosfer', label: 'Atmosfer' },
    { id: 'fiyat_performans', label: 'Fiyat/performans' },
    { id: 'erisilebilirlik', label: 'Erişilebilirlik' },
  ],
}

export function criteriaFor(venue) {
  return RATING_CRITERIA[venue?.kind] ?? []
}

/**
 * Gerçek yorumlardaki comment.ratings alanlarından kriter başına ortalama
 * hesaplar. En az 1 gerçek puan olmayan kriterler sonuca hiç girmez (0/boş
 * gösterip "sahte sıfır" izlenimi vermemek için).
 */
export function ratingAverages(comments, venue) {
  const criteria = criteriaFor(venue)
  return criteria
    .map(({ id, label }) => {
      const scores = comments
        .map((c) => c.ratings?.[id])
        .filter((v) => typeof v === 'number')
      if (scores.length === 0) return null
      const avg = scores.reduce((sum, v) => sum + v, 0) / scores.length
      return { id, label, average: avg, count: scores.length }
    })
    .filter(Boolean)
}
