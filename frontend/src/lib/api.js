/**
 * Thin client for the FastAPI backend. Vite proxies /api -> 127.0.0.1:8000
 * (see vite.config.js) so this works in dev without CORS setup.
 */
const BASE = '/api'

export async function getComments(placeId) {
  const res = await fetch(`${BASE}/places/${encodeURIComponent(placeId)}/comments`)
  if (!res.ok) throw new Error(`getComments failed: ${res.status}`)
  return res.json()
}

export async function postComment(placeId, { author, text, lat, lng, accuracy }) {
  const res = await fetch(`${BASE}/places/${encodeURIComponent(placeId)}/comments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ author, text, lat, lng, accuracy }),
  })
  if (!res.ok) throw new Error(`postComment failed: ${res.status}`)
  return res.json()
}

export async function postCheckin(placeId, { author, lat, lng, accuracy }) {
  const res = await fetch(`${BASE}/places/${encodeURIComponent(placeId)}/checkins`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ author, lat, lng, accuracy }),
  })
  if (!res.ok) throw new Error(`postCheckin failed: ${res.status}`)
  return res.json()
}

export async function getCheckinCount(placeId) {
  const res = await fetch(`${BASE}/places/${encodeURIComponent(placeId)}/checkin-count`)
  if (!res.ok) throw new Error(`getCheckinCount failed: ${res.status}`)
  return res.json()
}

export async function getStatusUpdates(placeId) {
  const res = await fetch(`${BASE}/places/${encodeURIComponent(placeId)}/status`)
  if (!res.ok) throw new Error(`getStatusUpdates failed: ${res.status}`)
  return res.json()
}

export async function postStatusUpdate(placeId, { author, tag, text }) {
  const res = await fetch(`${BASE}/places/${encodeURIComponent(placeId)}/status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ author, tag, text }),
  })
  if (!res.ok) throw new Error(`postStatusUpdate failed: ${res.status}`)
  return res.json()
}
