/**
 * Thin client for the FastAPI backend. Vite proxies /api -> 127.0.0.1:8000
 * (see vite.config.js) so this works in dev without CORS setup.
 */
const BASE = '/api'
const TOKEN_KEY = 'kesfetplus_token'

export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

export function setToken(token) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token)
    else localStorage.removeItem(TOKEN_KEY)
  } catch {
    // localStorage unavailable (private mode etc.) - session just won't persist
  }
}

export function isLoggedIn() {
  return Boolean(getToken())
}

function authHeaders() {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function request(path, { method = 'GET', body } = {}) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: {
      ...(body ? { 'Content-Type': 'application/json' } : {}),
      ...authHeaders(),
    },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    let detail = `${method} ${path} failed: ${res.status}`
    try {
      const data = await res.json()
      if (data?.detail) detail = data.detail
    } catch {
      // response body wasn't JSON - keep the generic message
    }
    const error = new Error(detail)
    error.status = res.status
    throw error
  }
  if (res.status === 204) return null
  return res.json()
}

// --- Auth ---------------------------------------------------------------

export async function register({ email, password, displayName }) {
  const data = await request('/auth/register', {
    method: 'POST',
    body: { email, password, display_name: displayName },
  })
  setToken(data.token)
  return data.user
}

export async function login({ email, password }) {
  const data = await request('/auth/login', {
    method: 'POST',
    body: { email, password },
  })
  setToken(data.token)
  return data.user
}

export async function logout() {
  try {
    await request('/auth/logout', { method: 'POST' })
  } catch {
    // token already invalid/expired server-side - fine, we're clearing it locally anyway
  } finally {
    setToken(null)
  }
}

export async function getMe() {
  return request('/auth/me')
}

export async function getUserProfile(userId) {
  return request(`/users/${encodeURIComponent(userId)}`)
}

/**
 * Real-time computed stats (never a stored/fabricated number) for the
 * "Teşvik Katmanı" - see docs/research/anlik-bilgi-akisi.md and
 * database/checkins_store.count_user_statuses. { status_count, badges,
 * gozcu_threshold }.
 */
export async function getUserStats(userId) {
  return request(`/users/${encodeURIComponent(userId)}/stats`)
}

// --- Blocking -------------------------------------------------------------

export async function blockUser(userId) {
  return request(`/users/${encodeURIComponent(userId)}/block`, { method: 'POST' })
}

export async function unblockUser(userId) {
  return request(`/users/${encodeURIComponent(userId)}/unblock`, { method: 'POST' })
}

// --- Reports ----------------------------------------------------------------

export async function reportContent({ targetType, targetId, placeId, reason }) {
  return request('/reports', {
    method: 'POST',
    body: { target_type: targetType, target_id: targetId, place_id: placeId, reason },
  })
}

// --- Moderation (moderator-only, see database/users_store.py) -------------

export async function getModerationReports() {
  return request('/moderation/reports')
}

export async function resolveReport(reportId) {
  return request(`/moderation/reports/${encodeURIComponent(reportId)}/resolve`, {
    method: 'POST',
  })
}

export async function getHiddenContent() {
  return request('/moderation/hidden-content')
}

export async function restoreContent(contentType, contentId) {
  return request(
    `/moderation/content/${encodeURIComponent(contentType)}/${encodeURIComponent(contentId)}/restore`,
    { method: 'POST' },
  )
}

/**
 * Basit istatistik görünümü - her sayı backend'de ilgili JSON deposundan
 * anlık hesaplanır, hiçbiri uydurulmaz/önbelleğe alınmaz (bkz.
 * api/main.py GET /moderation/stats).
 */
export async function getModerationStats() {
  return request('/moderation/stats')
}

// --- Places: comments / check-ins / status --------------------------------

// --- Weather ("hava durumuna duyarlı mekan önerileri" MVP) --------------
// Public/no-auth endpoint - see database/weather_cache.py. Real Open-Meteo
// data only; if it can't be reached this throws (502), and callers must
// show an honest "hava durumu bilgisi şu an yok" state, never a fabricated
// temperature/condition (CLAUDE.md "sahte veri yasak").

export async function getWeather(district) {
  return request(`/weather/${encodeURIComponent(district)}`)
}

export async function getComments(placeId) {
  return request(`/places/${encodeURIComponent(placeId)}/comments`)
}

export async function postComment(placeId, { text, lat, lng, accuracy }) {
  return request(`/places/${encodeURIComponent(placeId)}/comments`, {
    method: 'POST',
    body: { text, lat, lng, accuracy },
  })
}

export async function postCheckin(placeId, { lat, lng, accuracy }) {
  return request(`/places/${encodeURIComponent(placeId)}/checkins`, {
    method: 'POST',
    body: { lat, lng, accuracy },
  })
}

export async function getCheckinCount(placeId) {
  return request(`/places/${encodeURIComponent(placeId)}/checkin-count`)
}

/**
 * Tüm mekanlar için tek istekte checkin_count + helpful_count (bkz.
 * GET /places/popularity-scores, api/main.py) - frontend/src/lib/search.js
 * bunu sıralama sinyali olarak kullanır. Liste ekranı açılışında bir kez
 * çekilir (Home.jsx/ExploreAll.jsx), 484 mekan için ayrı ayrı istek
 * gerektirmez. İstek başarısız olursa {} döner - search.js bunu "hiçbir
 * venue için sinyal yok" olarak yorumlar, uydurma bir popülerlik göstermez.
 */
export async function getPopularityScores() {
  try {
    return await request('/places/popularity-scores')
  } catch (err) {
    console.error('getPopularityScores failed', err)
    return {}
  }
}

export async function getStatusUpdates(placeId) {
  return request(`/places/${encodeURIComponent(placeId)}/status`)
}

export async function postStatusUpdate(placeId, { tag, text }) {
  return request(`/places/${encodeURIComponent(placeId)}/status`, {
    method: 'POST',
    body: { tag, text },
  })
}

// --- "Faydalı oldu" (helpful) - see docs/research/anlik-bilgi-akisi.md
// "Teşvik Katmanı". Toggle: calling again on the same content un-marks it.

export async function markCommentHelpful(placeId, commentId) {
  return request(
    `/places/${encodeURIComponent(placeId)}/comments/${encodeURIComponent(commentId)}/helpful`,
    { method: 'POST' },
  )
}

export async function markStatusHelpful(placeId, statusId) {
  return request(
    `/places/${encodeURIComponent(placeId)}/status/${encodeURIComponent(statusId)}/helpful`,
    { method: 'POST' },
  )
}

// --- Web Push (VAPID) -------------------------------------------------------

/**
 * The public VAPID key the browser needs for PushManager.subscribe(). See
 * database/push_notify.py / scripts/generate_vapid_keys.py - throws (with
 * an honest server-provided message) if no real key pair has been
 * generated yet, rather than returning a fake one.
 */
export async function getVapidPublicKey() {
  return request('/push/vapid-public-key')
}

export async function subscribePush(subscription) {
  return request('/push/subscribe', { method: 'POST', body: subscription })
}

export async function unsubscribePush(endpoint) {
  return request('/push/unsubscribe', { method: 'POST', body: { endpoint } })
}

// --- Places: photo comparison ----------------------------------------------

/**
 * Uploads a photo for real perceptual-hash comparison against the venue's
 * reference photo (see database/photo_compare.py - no fabricated
 * similarity, an actually-computed pHash Hamming distance).
 *
 * Multipart/form-data, so this can't go through request() above (that
 * helper always JSON-encodes the body). The browser sets the multipart
 * Content-Type boundary itself - never set it manually on a FormData body.
 */
export async function comparePhoto(placeId, file) {
  const formData = new FormData()
  formData.append('photo', file)
  const res = await fetch(`${BASE}/places/${encodeURIComponent(placeId)}/compare-photo`, {
    method: 'POST',
    headers: authHeaders(),
    body: formData,
  })
  if (!res.ok) {
    let detail = `compare-photo failed: ${res.status}`
    try {
      const data = await res.json()
      if (data?.detail) detail = data.detail
    } catch {
      // response body wasn't JSON - keep the generic message
    }
    const error = new Error(detail)
    error.status = res.status
    throw error
  }
  return res.json()
}
