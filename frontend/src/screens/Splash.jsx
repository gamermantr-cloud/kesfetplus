import { ArrowRight } from 'lucide-react'
import { motion, useReducedMotion } from 'motion/react'
import { useNavigate } from 'react-router-dom'

/**
 * Landing/splash screen. Background is a placeholder gradient standing in
 * for the mockup's stone-arch photo until a real image is supplied.
 *
 * Entrance sequence (same `useReducedMotion` pattern as App.jsx/Home.jsx/
 * PlaceDetail.jsx - collapses to the final state instantly when the user
 * prefers reduced motion): the background settles first with a slow
 * ease-out zoom, then the wordmark and slogan stagger in, the footer labels
 * fade in alongside, and the forward button arrives last with a soft
 * looping ring pulse behind it to draw the eye. Whole reveal lands well
 * under ~1.5s; the ring pulse continues as a subtle idle cue afterward.
 */
export default function Splash() {
  const navigate = useNavigate()
  const shouldReduceMotion = useReducedMotion()

  return (
    <div className="relative flex min-h-screen flex-col overflow-hidden">
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-tan via-tan-dark to-espresso"
        initial={shouldReduceMotion ? false : { opacity: 0.6, scale: 1.06 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1.1, ease: 'easeOut' }}
      />
      <div className="absolute inset-0 bg-gradient-to-t from-espresso/90 via-espresso/25 to-transparent" />

      <div className="relative flex flex-1 flex-col items-center justify-center px-6 text-center">
        <motion.h1
          className="font-display text-6xl font-medium tracking-tight text-cream"
          initial={shouldReduceMotion ? false : { opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: shouldReduceMotion ? 0 : 0.1, ease: 'easeOut' }}
        >
          Keşfet+
        </motion.h1>
        <motion.p
          className="mt-3 font-sans text-sm text-sand"
          initial={shouldReduceMotion ? false : { opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: shouldReduceMotion ? 0 : 0.32, ease: 'easeOut' }}
        >
          İyi yerler insanları birleştirir.
        </motion.p>
      </div>

      <div className="absolute bottom-24 right-6 h-16 w-16">
        {!shouldReduceMotion && (
          <motion.span
            aria-hidden="true"
            className="absolute inset-0 rounded-full bg-tan"
            initial={{ opacity: 0.45, scale: 1 }}
            animate={{ opacity: [0.45, 0, 0.45], scale: [1, 1.35, 1] }}
            transition={{ duration: 1.8, delay: 1, repeat: Infinity, ease: 'easeInOut' }}
          />
        )}
        <motion.button
          type="button"
          onClick={() => navigate('/home')}
          aria-label="Devam et"
          className="relative flex h-16 w-16 items-center justify-center rounded-full bg-espresso text-cream shadow-lg transition-colors hover:bg-espresso-soft"
          initial={shouldReduceMotion ? false : { opacity: 0, scale: 0.7 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.35, delay: shouldReduceMotion ? 0 : 0.62, ease: 'easeOut' }}
          whileTap={shouldReduceMotion ? undefined : { scale: 0.94 }}
        >
          <ArrowRight size={24} />
        </motion.button>
      </div>

      <motion.div
        className="relative flex items-center justify-between px-6 pb-6 font-sans text-[9px] uppercase tracking-[0.2em] text-sand/70"
        initial={shouldReduceMotion ? false : { opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4, delay: shouldReduceMotion ? 0 : 0.5, ease: 'easeOut' }}
      >
        <span>Keşfet</span>
        <span>Paylaş</span>
        <span>Sorgula</span>
        <span>Gerçekten Yaşa</span>
      </motion.div>
    </div>
  )
}
