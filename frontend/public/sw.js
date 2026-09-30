/**
 * Web Push service worker. Handles two real browser events:
 *
 * - `push`: a message actually arrived from the browser vendor's push
 *   service (Chrome/Firefox/Edge's own infrastructure) after the backend
 *   called pywebpush.webpush() - see database/push_notify.py. The payload
 *   is JSON: {title, body, url} (see push_notify.notify_new_status).
 * - `notificationclick`: the user tapped the shown notification - focuses
 *   an already-open tab on that place if there is one, otherwise opens a
 *   new one.
 *
 * This file is served as-is from frontend/public/sw.js (Vite copies public/
 * verbatim, no bundling) - see frontend/src/lib/push.js for the
 * `navigator.serviceWorker.register('/sw.js')` call.
 */

self.addEventListener('push', (event) => {
  let payload = { title: 'Keşfet Plus', body: 'Yeni bir bildirim var.', url: '/' }
  if (event.data) {
    try {
      payload = { ...payload, ...event.data.json() }
    } catch {
      // Not JSON (shouldn't happen - backend always sends JSON) - fall back
      // to the plain-text body rather than dropping the notification.
      payload.body = event.data.text()
    }
  }

  event.waitUntil(
    self.registration.showNotification(payload.title, {
      body: payload.body,
      icon: '/favicon.svg',
      badge: '/favicon.svg',
      data: { url: payload.url },
    }),
  )
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  const targetUrl = event.notification.data?.url ?? '/'

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
      for (const client of windowClients) {
        const clientUrl = new URL(client.url)
        if (clientUrl.pathname === targetUrl && 'focus' in client) {
          return client.focus()
        }
      }
      if (clients.openWindow) {
        return clients.openWindow(targetUrl)
      }
      return undefined
    }),
  )
})
