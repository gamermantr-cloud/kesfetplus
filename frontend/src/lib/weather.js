/**
 * "Hava durumuna duyarlı mekan önerileri" MVP - venue classification.
 * See docs/research/yeni-ozellik-onerisi-hava-durumu-onerileri.md Bölüm 4.3.
 *
 * OUTDOOR_WEATHER_SENSITIVE_TAGS is a rule-based derivation from each
 * venue's real, already-existing `tags` array - not a new/guessed data
 * field (CLAUDE.md "sahte veri yasak"). It's a heuristic starting point
 * (a "piknik"-tagged venue might still have a covered pavilion), not a
 * verified "indoor/outdoor" fact.
 */
export const OUTDOOR_WEATHER_SENSITIVE_TAGS = new Set([
  'piknik',
  'sahil',
  'park',
  'orman',
  'plaj',
  'millet bahçesi',
  'kamp',
  'yürüyüş',
  'bisiklet',
  'koşu',
  'gün batımı',
  'mangal',
])

/** True if a venue's tags intersect OUTDOOR_WEATHER_SENSITIVE_TAGS. */
export function isOutdoorWeatherSensitive(venue) {
  if (!venue?.tags?.length) return false
  return venue.tags.some((tag) => OUTDOOR_WEATHER_SENSITIVE_TAGS.has(tag))
}
