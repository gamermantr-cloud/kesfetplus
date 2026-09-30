import { useEffect, useMemo, useState } from 'react'
import { BedDouble, ChevronLeft, Search, Star, Trees, Utensils, Wine } from 'lucide-react'
import { motion, useReducedMotion } from 'motion/react'
import Skeleton from 'react-loading-skeleton'
import 'react-loading-skeleton/dist/skeleton.css'
import { useNavigate } from 'react-router-dom'
import VenueCardSkeleton from '../components/VenueCardSkeleton.jsx'
import { getPopularityScores } from '../lib/api.js'
import { getAllVenues } from '../lib/data.js'
import { rankVenues } from '../lib/search.js'
import { getVenueIcon } from '../lib/venueIcon.js'

const CATEGORIES = [
  { id: 'dogu', label: 'Doğa', icon: Trees, match: (v) => v.kind === 'place' },
  { id: 'yeme', label: 'Yeme & İçme', icon: Utensils, match: (v) => v.kind === 'gurme' && v.category !== 'bar' },
  { id: 'otel', label: 'Oteller', icon: BedDouble, match: (v) => v.kind === 'hotel' },
  { id: 'bar', label: 'Barlar', icon: Wine, match: (v) => v.kind === 'gurme' && v.category === 'bar' },
]

// Card backgrounds cycle through design-token gradients; used as a placeholder/fallback
// for venues that have no real photo (or whose photo fails to load).
const CARD_GRADIENTS = [
  'from-tan to-sand-dark',
  'from-espresso-soft to-tan-dark',
  'from-sand-dark to-tan',
  'from-tan-dark to-espresso-soft',
]

export default function ExploreAll() {
  const navigate = useNavigate()
  const shouldReduceMotion = useReducedMotion()
  const [venues, setVenues] = useState([])
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [activeCategory, setActiveCategory] = useState(null)
  // {} = henüz yüklenmedi ya da istek başarısız oldu - search.js bunu
  // "hiçbir venue için sinyal yok" olarak yorumlar, uydurma bir popülerlik
  // göstermez (bkz. lib/search.js popularityScore).
  const [popularityScores, setPopularityScores] = useState({})

  useEffect(() => {
    let cancelled = false
    getAllVenues().then((data) => {
      if (!cancelled) {
        setVenues(data)
        setLoading(false)
      }
    })
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    let cancelled = false
    getPopularityScores().then((data) => {
      if (!cancelled) setPopularityScores(data)
    })
    return () => {
      cancelled = true
    }
  }, [])

  const filtered = useMemo(() => {
    const category = CATEGORIES.find((c) => c.id === activeCategory)
    return rankVenues(venues, { query, category, popularityScores })
  }, [venues, activeCategory, query, popularityScores])

  return (
    <div className="min-h-screen bg-cream pb-10">
      <header className="flex items-center gap-3 px-5 pt-6">
        <button
          type="button"
          aria-label="Geri"
          onClick={() => navigate(-1)}
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-sand text-espresso-soft"
        >
          <ChevronLeft size={20} />
        </button>
        <div>
          <h1 className="font-display text-xl text-espresso">Tüm Mekanlar</h1>
          <p className="text-xs text-taupe">
            {loading ? <Skeleton width={70} height={11} baseColor="var(--color-sand-dark)" highlightColor="var(--color-cream)" /> : `${filtered.length} mekan`}
          </p>
        </div>
      </header>

      <div className="px-5 mt-5">
        <div className="flex items-center gap-2 bg-sand rounded-full px-4 py-3">
          <Search size={18} className="text-taupe shrink-0" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Mekan, şehir, aktivite ara..."
            className="bg-transparent outline-none flex-1 text-sm text-espresso placeholder:text-taupe"
          />
        </div>
      </div>

      <div className="flex gap-2 px-5 mt-4 overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {CATEGORIES.map((cat) => {
          const Icon = cat.icon
          const active = activeCategory === cat.id
          return (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(active ? null : cat.id)}
              className={`flex items-center gap-1.5 shrink-0 rounded-full px-3.5 py-2 text-sm font-medium transition-colors ${
                active ? 'bg-tan text-cream' : 'bg-sand text-espresso-soft'
              }`}
            >
              <Icon size={15} />
              {cat.label}
            </button>
          )
        })}
      </div>

      <div className="grid grid-cols-2 gap-4 px-5 mt-5">
        {loading && <VenueCardSkeleton count={8} />}
        {!loading && filtered.length === 0 && (
          <p className="col-span-2 text-taupe text-sm">Bu kritere uyan mekan bulunamadı.</p>
        )}
        {filtered.map((venue, i) => {
          const VenueIcon = getVenueIcon(venue)
          return (
          <motion.button
            type="button"
            key={venue.id}
            onClick={() => navigate(`/place/${venue.id}`)}
            className="bg-sand rounded-2xl overflow-hidden text-left grain"
            initial={shouldReduceMotion ? false : { opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.22, delay: shouldReduceMotion ? 0 : Math.min(i * 0.03, 0.15) }}
          >
            <div className={`relative h-24 bg-gradient-to-br ${CARD_GRADIENTS[i % CARD_GRADIENTS.length]} flex items-center justify-center`}>
              <VenueIcon size={28} className="text-cream/60" aria-hidden="true" />
              {venue.photos?.[0]?.url && (
                <img
                  src={venue.photos[0].url}
                  alt=""
                  loading="lazy"
                  className="absolute inset-0 h-full w-full object-cover"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none'
                  }}
                />
              )}
              {venue.rating && (
                <div className="absolute top-2 right-2 flex items-center gap-1 bg-cream/90 rounded-full px-2 py-0.5 text-xs font-semibold text-espresso">
                  <Star size={11} className="fill-gold text-gold" />
                  {venue.rating}
                </div>
              )}
            </div>
            <div className="p-3">
              <p className="text-sm font-medium text-espresso truncate">{venue.name}</p>
              {venue.area && <p className="text-xs text-taupe truncate mt-0.5">{venue.area}</p>}
            </div>
          </motion.button>
          )
        })}
      </div>
    </div>
  )
}
