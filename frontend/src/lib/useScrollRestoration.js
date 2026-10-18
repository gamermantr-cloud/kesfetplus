import { useEffect } from 'react'
import { useLocation, useNavigationType } from 'react-router-dom'
import { getScrollPosition, saveScrollPosition } from './scrollRestoration.js'

/**
 * Geri/ileri (POP) navigasyonda sayfanın en son kaldığı scroll pozisyonuna
 * döner; normal (PUSH) navigasyonda ise her zamanki gibi en üstten başlar.
 * App.jsx'te bir kere çağrılır - her ekranın kendi başına uygulaması
 * gerekmez.
 */
export function useScrollRestoration() {
  const location = useLocation()
  const navigationType = useNavigationType()

  // Mevcut sayfadaki scroll pozisyonunu sürekli kaydeder, böylece kullanıcı
  // ne zaman başka bir sayfaya geçerse geçsin kayıt her zaman güncel olur.
  useEffect(() => {
    const key = location.pathname
    let ticking = false
    function onScroll() {
      if (ticking) return
      ticking = true
      requestAnimationFrame(() => {
        saveScrollPosition(key, window.scrollY)
        ticking = false
      })
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [location.pathname])

  // Sayfa değiştiğinde: POP (geri/ileri) ise kayıtlı pozisyona dön, değilse
  // (normal tıklama ile gidiş) en üstten başla - mevcut davranış korunur.
  useEffect(() => {
    if (navigationType !== 'POP') {
      window.scrollTo(0, 0)
      return
    }
    const target = getScrollPosition(location.pathname)
    if (target <= 0) return

    // İçerik (ör. async venue listesi) henüz render olmamış olabilir -
    // sayfa hedef pozisyona kaydırılabilecek kadar uzun olana kadar birkaç
    // frame bekler, en fazla ~0.6 saniye dener.
    let cancelled = false
    let frame = 0
    function tryScroll() {
      if (cancelled) return
      frame += 1
      if (document.body.scrollHeight >= target + window.innerHeight || frame > 40) {
        window.scrollTo(0, target)
        return
      }
      requestAnimationFrame(tryScroll)
    }
    requestAnimationFrame(tryScroll)
    return () => {
      cancelled = true
    }
  }, [location.pathname, navigationType])
}
