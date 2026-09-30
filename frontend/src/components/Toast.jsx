import { AnimatePresence, motion, useReducedMotion } from 'motion/react'

/**
 * Shared toast pattern used by Home/Profile/Support/Moderation (each screen
 * keeps its own `toast` state + `showToast()` timer, this just renders it).
 * Fades + slides in/out on mount/unmount via AnimatePresence instead of the
 * previous instant `{toast && <div>...}` appear/disappear.
 *
 * Respects prefers-reduced-motion (via useReducedMotion()): when reduced
 * motion is requested the slide offset is skipped and only opacity changes.
 * `className` lets callers override the vertical position (e.g. Home's nav
 * bar needs `bottom-24` instead of the default `bottom-8`).
 */
export default function Toast({ message, className = 'bottom-8' }) {
  const shouldReduceMotion = useReducedMotion()

  return (
    <AnimatePresence>
      {message && (
        <motion.div
          initial={shouldReduceMotion ? { opacity: 0 } : { opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={shouldReduceMotion ? { opacity: 0 } : { opacity: 0, y: 10 }}
          transition={{ duration: 0.18, ease: 'easeOut' }}
          className={`fixed ${className} inset-x-0 z-10 mx-auto w-fit max-w-[430px] rounded-full bg-espresso px-4 py-2 text-xs font-medium text-cream shadow-lg`}
        >
          {message}
        </motion.div>
      )}
    </AnimatePresence>
  )
}
