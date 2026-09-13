import { ArrowRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

/**
 * Landing/splash screen. Background is a placeholder gradient standing in
 * for the mockup's stone-arch photo until a real image is supplied.
 */
export default function Splash() {
  const navigate = useNavigate()

  return (
    <div className="relative flex min-h-screen flex-col overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-tan via-tan-dark to-espresso" />
      <div className="absolute inset-0 bg-gradient-to-t from-espresso/90 via-espresso/25 to-transparent" />

      <div className="relative flex flex-1 flex-col items-center justify-center px-6 text-center">
        <h1 className="font-display text-6xl font-medium tracking-tight text-cream">
          Keşfet+
        </h1>
        <p className="mt-3 font-sans text-sm text-sand">
          İyi yerler insanları birleştirir.
        </p>
      </div>

      <button
        type="button"
        onClick={() => navigate('/home')}
        aria-label="Devam et"
        className="absolute bottom-24 right-6 flex h-16 w-16 items-center justify-center rounded-full bg-espresso text-cream shadow-lg transition-colors hover:bg-espresso-soft"
      >
        <ArrowRight size={24} />
      </button>

      <div className="relative flex items-center justify-between px-6 pb-6 font-sans text-[9px] uppercase tracking-[0.2em] text-sand/70">
        <span>Keşfet</span>
        <span>Paylaş</span>
        <span>Sorgula</span>
        <span>Gerçekten Yaşa</span>
      </div>
    </div>
  )
}
