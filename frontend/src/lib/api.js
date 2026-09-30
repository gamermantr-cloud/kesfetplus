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

// --- Places: comments / check-ins / status --------------------------------

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

export async function getStatusUpdates(placeId) {
  return request(`/places/${encodeURIComponent(placeId)}/status`)
}

export async function postStatusUpdate(placeId, { tag, text }) {
  return request(`/places/${encodeURIComponent(placeId)}/status`, {
    method: 'POST',
    body: { tag, text },
  })
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
