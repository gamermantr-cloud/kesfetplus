/**
 * Approximate Istanbul district centers (from the original design reference).
 * Seed data only has an "area" string, not per-venue coordinates, so venues
 * are plotted at their district's approximate center with a small
 * deterministic offset - NOT a precise address location.
 */
export const DISTRICT_LATLNG = {
  Sarıyer: { lat: 41.167, lng: 29.058 },
  Beşiktaş: { lat: 41.043, lng: 29.009 },
  Şişli: { lat: 41.06, lng: 28.988 },
  Beyoğlu: { lat: 41.037, lng: 28.977 },
  Eyüpsultan: { lat: 41.048, lng: 28.934 },
  Kağıthane: { lat: 41.079, lng: 28.972 },
  Fatih: { lat: 41.019, lng: 28.949 },
  Zeytinburnu: { lat: 40.995, lng: 28.902 },
  Bakırköy: { lat: 40.982, lng: 28.872 },
  Bahçelievler: { lat: 41.0, lng: 28.859 },
  Bağcılar: { lat: 41.039, lng: 28.856 },
  Esenler: { lat: 41.045, lng: 28.879 },
  Bayrampaşa: { lat: 41.047, lng: 28.907 },
  Gaziosmanpaşa: { lat: 41.065, lng: 28.915 },
  Sultangazi: { lat: 41.106, lng: 28.867 },
  Arnavutköy: { lat: 41.185, lng: 28.74 },
  Başakşehir: { lat: 41.093, lng: 28.802 },
  Küçükçekmece: { lat: 41.0, lng: 28.775 },
  Avcılar: { lat: 40.98, lng: 28.721 },
  Esenyurt: { lat: 41.033, lng: 28.674 },
  Beylikdüzü: { lat: 41.0, lng: 28.64 },
  Büyükçekmece: { lat: 41.02, lng: 28.585 },
  Çatalca: { lat: 41.143, lng: 28.461 },
  Silivri: { lat: 41.073, lng: 28.247 },
  Beykoz: { lat: 41.124, lng: 29.1 },
  Üsküdar: { lat: 41.027, lng: 29.015 },
  Kadıköy: { lat: 40.99, lng: 29.028 },
  Ataşehir: { lat: 40.992, lng: 29.125 },
  Ümraniye: { lat: 41.016, lng: 29.124 },
  Çekmeköy: { lat: 41.035, lng: 29.198 },
  Sancaktepe: { lat: 41.0, lng: 29.228 },
  Sultanbeyli: { lat: 40.962, lng: 29.266 },
  Kartal: { lat: 40.907, lng: 29.188 },
  Maltepe: { lat: 40.935, lng: 29.156 },
  Pendik: { lat: 40.877, lng: 29.253 },
  Tuzla: { lat: 40.816, lng: 29.301 },
  Şile: { lat: 41.174, lng: 29.612 },
  Adalar: { lat: 40.877, lng: 29.125 },
}

function hashString(str) {
  let h = 0
  for (let i = 0; i < str.length; i++) {
    h = (h << 5) - h + str.charCodeAt(i)
    h |= 0
  }
  return h
}

/** Finds the district center for a venue's "area" string (e.g. "Sarıyer (Emirgan)"). */
export function findDistrictLatLng(area) {
  if (!area) return null
  const match = Object.keys(DISTRICT_LATLNG).find((district) => area.includes(district))
  return match ? DISTRICT_LATLNG[match] : null
}

/**
 * Approximate marker position: district center plus a small deterministic
 * jitter (derived from the venue id) so venues in the same district don't
 * all stack on one point.
 */
export function approxLatLng(venue) {
  const center = findDistrictLatLng(venue.area) ?? { lat: 41.02, lng: 28.965 }
  const h = hashString(venue.id)
  const jitterLat = ((h % 1000) / 1000 - 0.5) * 0.02
  const jitterLng = (((h >> 10) % 1000) / 1000 - 0.5) * 0.02
  return { lat: center.lat + jitterLat, lng: center.lng + jitterLng }
}
