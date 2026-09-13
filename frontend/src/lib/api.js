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

export async function postComment(placeId, { author, text }) {
  const res = await fetch(`${BASE}/places/${encodeURIComponent(placeId)}/comments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ author, text }),
  })
  if (!res.ok) throw new Error(`postComment failed: ${res.status}`)
  return res.json()
}
