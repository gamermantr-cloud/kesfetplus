/**
 * Real Web Push subscribe/unsubscribe flow (RFC 8030 + VAPID/RFC 8292).
 *
 * Honesty notes (see CLAUDE.md "sahte veri yasak" rule, applied here to
 * behavior): every function here either does the real browser API call
 * (service worker registration, Notification.requestPermission,
 * PushManager.subscribe against the backend's real VAPID public key) or
 * throws/returns a clear reason it couldn't - there is no fake "subscribed!"
 * state. Web Push itself requires a secure context (HTTPS) - the one
 * exception the spec/browsers carve out is `http://localhost` for local
 * dev, which is why this still works with `npm run dev`.
 */
import { getVapidPublicKey, subscribePush, unsubscribePush } from './api.js'

export function isPushSupported() {
  return (
    typeof window !== 'undefined' &&
    'serviceWorker' in navigator &&
    'PushManager' in window &&
    'Notification' in window
  )
}

/**
 * "granted" | "denied" | "default" (never asked yet). Mirrors
 * Notification.permission directly - no invented in-between state.
 */
export function getPermissionState() {
  if (typeof Notification === 'undefined') return 'unsupported'
  return Notification.permission
}

// Converts the backend's URL-safe base64 VAPID public key (see
// scripts/generate_vapid_keys.py) into the Uint8Array PushManager.subscribe
// requires for applicationServerKey - the standard conversion recommended
// by the Web Push spec/MDN, no library needed for this one step.
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = atob(base64)
  return Uint8Array.from(rawData, (char) => char.charCodeAt(0))
}

async function registerServiceWorker() {
  return navigator.serviceWorker.register('/sw.js')
}

/**
 * Full subscribe flow: register the service worker, ask for notification
 * permission, fetch the backend's real VAPID public key, subscribe with the
 * browser's PushManager, then persist the subscription server-side (POST
 * /push/subscribe). Throws with a specific, honest message at whichever
 * step actually fails - callers should show that message, not a generic
 * "something went wrong".
 */
export async function enablePushNotifications() {
  if (!isPushSupported()) {
    throw new Error('Bu tarayıcı push bildirimlerini desteklemiyor.')
  }
  if (!window.isSecureContext) {
    throw new Error(
      'Push bildirimleri sadece HTTPS (veya localhost) üzerinde çalışır.',
    )
  }

  const permission = await Notification.requestPermission()
  if (permission !== 'granted') {
    throw new Error('Bildirim izni verilmedi.')
  }

  const registration = await registerServiceWorker()
  const { public_key: publicKey } = await getVapidPublicKey()

  let subscription = await registration.pushManager.getSubscription()
  if (!subscription) {
    subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(publicKey),
    })
  }

  const subscriptionJson = subscription.toJSON()
  await subscribePush({
    endpoint: subscriptionJson.endpoint,
    keys: subscriptionJson.keys,
  })
  return subscription
}

/**
 * Unsubscribes both locally (browser) and server-side (so a dead
 * subscription doesn't linger in push_subscriptions.json). Safe to call
 * even if there was never a subscription - it just becomes a no-op.
 */
export async function disablePushNotifications() {
  if (!isPushSupported()) return
  const registration = await navigator.serviceWorker.getRegistration()
  const subscription = await registration?.pushManager.getSubscription()
  if (!subscription) return

  const endpoint = subscription.endpoint
  await subscription.unsubscribe()
  await unsubscribePush(endpoint)
}
