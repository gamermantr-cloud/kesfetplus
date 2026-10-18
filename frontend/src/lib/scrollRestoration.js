/**
 * Rota başına scroll pozisyonunu sessionStorage'da tutar. useScrollRestoration
 * hook'u (lib/useScrollRestoration.js) bunu kullanarak geri (POP) navigasyonda
 * kullanıcının kaldığı yere döner.
 */
const STORAGE_KEY = 'kp-scroll-positions'

function readStore() {
  try {
    return JSON.parse(sessionStorage.getItem(STORAGE_KEY)) ?? {}
  } catch {
    return {}
  }
}

function writeStore(store) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(store))
  } catch {
    // sessionStorage kullanılamıyor (gizli pencere vb.) - sessizce yoksay,
    // bu özellik olmadan da uygulama normal çalışır.
  }
}

export function saveScrollPosition(key, y) {
  const store = readStore()
  store[key] = y
  writeStore(store)
}

export function getScrollPosition(key) {
  const store = readStore()
  return store[key] ?? 0
}
