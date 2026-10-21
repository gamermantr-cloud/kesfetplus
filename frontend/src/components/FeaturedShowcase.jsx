import { Fragment, useEffect, useMemo, useRef, useState } from 'react'
import { Star } from 'lucide-react'
import {
  AnimatePresence,
  motion,
  useAnimationFrame,
  useInView,
  useMotionValue,
  useReducedMotion,
} from 'motion/react'
import { photoSrc } from '../lib/api.js'

// Vitrin her açılışta Emirgan Korusu ile başlar, ardından çok yorum almış ve
// yüksek puanlı mekanları rastgele sırayla dolaşır. Sadece gerçek fotoğrafı
// olan mekanlar girer - eksik foto uydurma görselle doldurulmaz.
const OPENING_VENUE_ID = 'emirgan'
const MIN_RATING = 4.5
const MIN_REVIEWS = 1000
const PHOTOS_PER_VENUE = 3
const PHOTO_MS = 3800
const EASE_OUT = [0.22, 1, 0.36, 1]
const EASE_IN_OUT = [0.65, 0, 0.35, 1]
// Yeni mekan, küçük foto şeridinin olduğu köşeden açılan bir daireyle gelir.
const REVEAL_ORIGIN = 'at 86% 84%'

function venuePhotos(venue) {
  return (venue.photos ?? [])
    .map((photo) => photoSrc(photo))
    .filter(Boolean)
    .slice(0, PHOTOS_PER_VENUE)
}

function shuffle(items) {
  const out = [...items]
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[out[i], out[j]] = [out[j], out[i]]
  }
  return out
}

function buildSlides(venues) {
  const withPhotos = venues
    .map((venue) => ({ venue, photos: venuePhotos(venue) }))
    .filter((slide) => slide.photos.length >= PHOTOS_PER_VENUE)
  const opening = withPhotos.find((slide) => slide.venue.id === OPENING_VENUE_ID)
  const loved = withPhotos.filter(
    ({ venue }) =>
      venue.id !== OPENING_VENUE_ID &&
      (venue.rating ?? 0) >= MIN_RATING &&
      (venue.reviewCount ?? 0) >= MIN_REVIEWS,
  )
  return [...(opening ? [opening] : []), ...shuffle(loved)]
}

function hidePhotoOnError(e) {
  e.currentTarget.style.visibility = 'hidden'
}

export default function FeaturedShowcase({ venues, onOpen }) {
  const reduceMotion = useReducedMotion()
  const slides = useMemo(() => buildSlides(venues), [venues])
  const [{ slide, photo }, setPosition] = useState({ slide: 0, photo: 0 })
  const [hovered, setHovered] = useState(false)
  const rootRef = useRef(null)
  const inView = useInView(rootRef)
  const elapsed = useRef(0)
  const progress = useMotionValue(0)

  // Tek bir saat hem ilerleme çubuğunu hem foto/mekan geçişini sürer, böylece
  // üstüne gelince, kart ekrandan çıkınca ya da sekme gizlenince ikisi birlikte durur.
  useAnimationFrame((_, delta) => {
    if (hovered || !inView || document.hidden || slides.length === 0) return
    elapsed.current += Math.min(delta, 100)
    progress.set(Math.min(elapsed.current / PHOTO_MS, 1))
    if (elapsed.current < PHOTO_MS) return
    elapsed.current = 0
    progress.set(0)
    setPosition((pos) =>
      pos.photo + 1 < PHOTOS_PER_VENUE
        ? { slide: pos.slide, photo: pos.photo + 1 }
        : { slide: (pos.slide + 1) % slides.length, photo: 0 },
    )
  })

  // Sıradaki mekanın fotoğrafları önceden yüklenir, geçiş anında boş kare görünmez.
  useEffect(() => {
    if (slides.length === 0) return
    for (const src of [...slides[slide].photos, ...slides[(slide + 1) % slides.length].photos]) {
      new Image().src = src
    }
  }, [slides, slide])

  if (slides.length === 0) return null
  const { venue, photos } = slides[slide]
  const drift = photo % 2 === 0 ? '3%' : '-3%'

  return (
    <motion.button
      ref={rootRef}
      type="button"
      onClick={() => onOpen(venue)}
      onHoverStart={() => setHovered(true)}
      onHoverEnd={() => setHovered(false)}
      whileTap={reduceMotion ? undefined : { scale: 0.985 }}
      aria-label={`Bu hafta keşfet: ${venue.name}`}
      className="relative isolate block h-64 w-full overflow-hidden rounded-3xl bg-espresso text-left grain"
    >
      <AnimatePresence>
        <motion.div
          key={venue.id}
          className="absolute inset-0"
          initial={
            reduceMotion
              ? { opacity: 0, zIndex: 2 }
              : { clipPath: `circle(0% ${REVEAL_ORIGIN})`, filter: 'brightness(1)', zIndex: 2 }
          }
          animate={
            reduceMotion
              ? { opacity: 1, zIndex: 2 }
              : { clipPath: `circle(150% ${REVEAL_ORIGIN})`, filter: 'brightness(1)', zIndex: 2 }
          }
          exit={
            reduceMotion
              ? { opacity: 0, zIndex: 1 }
              : { scale: 1.08, filter: 'brightness(0.45)', zIndex: 1 }
          }
          transition={{ duration: 1.25, ease: EASE_IN_OUT, zIndex: { duration: 0 } }}
        >
          <AnimatePresence>
            <motion.img
              key={photos[photo]}
              src={photos[photo]}
              alt=""
              onError={hidePhotoOnError}
              className="absolute inset-0 h-full w-full object-cover"
              initial={
                photo === 0
                  ? { opacity: 1, scale: 1.04, x: '0%', filter: 'blur(0px)', zIndex: 1 }
                  : { opacity: 0, scale: 1.04, x: '0%', filter: 'blur(14px)', zIndex: 1 }
              }
              animate={
                reduceMotion
                  ? { opacity: 1, filter: 'blur(0px)', zIndex: 1 }
                  : { opacity: 1, scale: 1.16, x: drift, filter: 'blur(0px)', zIndex: 1 }
              }
              // Çıkan foto, yenisi tamamen belirene kadar altta tam görünür kalır.
              exit={{
                opacity: 0,
                zIndex: 0,
                transition: { opacity: { delay: 1.1, duration: 0.01 }, zIndex: { duration: 0 } },
              }}
              transition={{
                opacity: { duration: 1.1, ease: EASE_OUT },
                filter: { duration: 1.1, ease: EASE_OUT },
                scale: { duration: (PHOTO_MS + 1500) / 1000, ease: 'linear' },
                x: { duration: (PHOTO_MS + 1500) / 1000, ease: 'linear' },
                zIndex: { duration: 0 },
              }}
            />
          </AnimatePresence>
        </motion.div>
      </AnimatePresence>

      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 z-10 bg-gradient-to-t from-espresso/85 via-espresso/10 to-espresso/40"
      />

      <div aria-hidden="true" className="absolute inset-x-4 top-3 z-20 flex gap-1.5">
        {Array.from({ length: PHOTOS_PER_VENUE }, (_, i) => (
          <span key={i} className="h-[3px] flex-1 overflow-hidden rounded-full bg-cream/30">
            <motion.span
              className="block h-full origin-left rounded-full bg-cream"
              style={{ scaleX: i < photo ? 1 : i === photo ? progress : 0 }}
            />
          </span>
        ))}
      </div>

      <AnimatePresence mode="wait" initial={false}>
        {venue.rating && (
          <motion.span
            key={venue.id}
            className="absolute right-4 top-7 z-20 flex items-center gap-1 rounded-full bg-cream/90 px-2.5 py-1 text-xs font-semibold text-espresso shadow-md"
            initial={reduceMotion ? false : { opacity: 0, y: -8, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.9, transition: { duration: 0.25 } }}
            transition={{ duration: 0.5, ease: EASE_OUT, delay: 0.6 }}
          >
            <Star size={12} className="fill-gold text-gold" />
            {venue.rating}
            {venue.reviewCount && (
              <span className="font-normal text-taupe">
                · {venue.reviewCount.toLocaleString('tr-TR')} yorum
              </span>
            )}
          </motion.span>
        )}
      </AnimatePresence>

      <div className="absolute bottom-4 left-5 right-40 z-20 [text-shadow:0_1px_14px_rgb(0_0_0/0.45)]">
        <span className="text-xs font-medium uppercase tracking-wide text-cream/80">Bu hafta keşfet</span>
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={venue.id}
            exit={{ opacity: 0, y: -10, filter: 'blur(6px)', transition: { duration: 0.35, ease: EASE_IN_OUT } }}
          >
            <h2 className="mt-1 font-display text-2xl leading-tight text-cream">
              {venue.name.split(' ').map((word, i) => (
                <Fragment key={i}>
                  <span className="-mb-1 inline-block overflow-hidden pb-1 align-bottom">
                    <motion.span
                      className="inline-block"
                      initial={reduceMotion ? false : { y: '110%', rotate: 4 }}
                      animate={{ y: '0%', rotate: 0 }}
                      transition={{ duration: 0.75, ease: EASE_OUT, delay: 0.3 + i * 0.07 }}
                    >
                      {word}
                    </motion.span>
                  </span>{' '}
                </Fragment>
              ))}
            </h2>
            {venue.area && (
              <motion.p
                className="mt-0.5 truncate text-sm text-cream/75"
                initial={reduceMotion ? false : { opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, ease: EASE_OUT, delay: 0.55 }}
              >
                {venue.area}
              </motion.p>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      <div aria-hidden="true" className="absolute bottom-4 right-4 z-20 flex gap-1.5">
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={venue.id}
            className="flex gap-1.5"
            exit={{ opacity: 0, y: -10, scale: 0.9, transition: { duration: 0.3, ease: EASE_IN_OUT } }}
          >
            {photos.map((src, i) => (
              <motion.span
                key={src}
                className="relative block h-11 w-11 overflow-hidden rounded-xl bg-cream/20 shadow-lg"
                initial={reduceMotion ? false : { opacity: 0, y: 14, scale: 0.6 }}
                animate={{ opacity: i === photo ? 1 : 0.6, y: 0, scale: i === photo ? 1.1 : 1 }}
                transition={{ duration: 0.5, ease: EASE_OUT, delay: photo === 0 ? 0.55 + i * 0.08 : 0 }}
              >
                <img src={src} alt="" onError={hidePhotoOnError} className="h-full w-full object-cover" />
                {i === photo && (
                  <motion.span
                    layoutId="showcase-thumb-ring"
                    className="absolute inset-0 rounded-xl ring-2 ring-inset ring-cream"
                    transition={{ duration: 0.45, ease: EASE_OUT }}
                  />
                )}
              </motion.span>
            ))}
          </motion.div>
        </AnimatePresence>
      </div>
    </motion.button>
  )
}
