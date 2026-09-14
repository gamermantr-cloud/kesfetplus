import { useEffect, useMemo, useRef, useState } from 'react'
import {
  ArrowRight,
  Bell,
  BedDouble,
  Compass,
  MapPin,
  MessageCircle,
  Plus,
  Search,
  Sparkles,
  Star,
  Trees,
  User,
  Utensils,
  Wine,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { getAllVenues } from '../lib/data.js'

const CATEGORIES = [
  { id: 'dogu', label: 'Doğa', icon: Trees, match: (v) => v.kind === 'place' },
  { id: 'yeme', label: 'Yeme & İçme', icon: Utensils, match: (v) => v.kind === 'gurme' && v.category !== 'bar' },
  { id: 'otel', label: 'Oteller', icon: BedDouble, match: (v) => v.kind === 'hotel' },
  { id: 'bar', label: 'Barlar', icon: Wine, match: (v) => v.kind === 'gurme' && v.category === 'bar' },
  { id: 'eklenti', label: 'Eklentiler', icon: Plus, match: null },
]

// Card backgrounds cycle through design-token gradients since the seed data has no photos yet.
const CARD_GRADIENTS = [
  'from-tan to-sand-dark',
  'from-espresso-soft to-tan-dark',
  'from-sand-dark to-tan',
  'from-tan-dark to-espresso-soft',
]

export default function Home() {
  const navigate = useNavigate()
  const [venues, setVenues] = useState([])
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [activeCategory, setActiveCategory] = useState(null)
  const [toast, setToast] = useState(null)
  const toastTimer = useRef(null)

  function showComingSoon(label) {
    setToast(`${label} yakında geliyor`)
    clearTimeout(toastTimer.current)
    toastTimer.current = setTimeout(() => setToast(null), 1800)
  }

  useEffect(() => () => clearTimeout(toastTimer.current), [])

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

  const featured = useMemo(() => {
    if (!venues.length) return null
    return venues.find((v) => v.tags?.includes('manzara')) ?? venues[0]
  }, [venues])

  const filtered = useMemo(() => {
    const category = CATEGORIES.find((c) => c.id === activeCategory)
    const q = query.trim().toLowerCase()
    return venues.filter((v) => {
      if (category?.match && !category.match(v)) return false
      if (v.id === featured?.id) return false
      if (q && !`${v.name} ${v.area ?? ''}`.toLowerCase().includes(q)) return false
      return true
    })
  }, [venues, activeCategory, query, featured])

  return (
    <div className="relative min-h-screen bg-cream pb-28">
      <header className="flex items-center justify-between px-5 pt-6">
        <span className="font-display text-xl text-espresso">Keşfet+</span>
        <div className="flex items-center gap-3">
          <button
            aria-label="Keşfet+ AI"
            onClick={() => navigate('/ai')}
            className="w-9 h-9 rounded-full bg-tan/20 flex items-center justify-center text-tan-dark"
          >
            <Sparkles size={18} />
          </button>
          <button aria-label="Bildirimler" onClick={() => navigate('/notifications')} className="text-espresso-soft">
            <Bell size={22} />
          </button>
          <button
            aria-label="Profil"
            onClick={() => navigate('/profile')}
            className="w-9 h-9 rounded-full bg-sand-dark flex items-center justify-center text-espresso-soft"
          >
            <User size={18} />
          </button>
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

      <div className="px-5 mt-5">
        {featured && (
          <button
            type="button"
            onClick={() => navigate(`/place/${featured.id}`)}
            className={`relative h-48 w-full rounded-3xl overflow-hidden bg-gradient-to-br ${CARD_GRADIENTS[0]} p-5 flex flex-col justify-end text-left`}
          >
            <span className="text-cream/80 text-xs font-medium uppercase tracking-wide">Bu hafta keşfet</span>
            <h2 className="font-display text-3xl text-cream mt-1 leading-tight">{featured.name}</h2>
            {featured.area && <p className="text-cream/70 text-sm mt-0.5">{featured.area}</p>}
            <span
              aria-hidden="true"
              className="absolute bottom-5 right-5 w-11 h-11 rounded-full bg-cream flex items-center justify-center shadow-md"
            >
              <ArrowRight size={20} className="text-espresso" />
            </span>
          </button>
        )}
      </div>

      <div className="flex items-center justify-between px-5 mt-7">
        <h3 className="font-display text-lg text-espresso">Sana Özel Seçimler</h3>
        <button onClick={() => navigate('/explore')} className="text-tan-dark text-sm font-medium">
          Tümünü Gör
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 px-5 mt-3">
        {loading && <p className="col-span-2 text-taupe text-sm">Yükleniyor...</p>}
        {!loading && filtered.length === 0 && (
          <p className="col-span-2 text-taupe text-sm">Bu kritere uyan mekan bulunamadı.</p>
        )}
        {filtered.slice(0, 12).map((venue, i) => (
          <button
            type="button"
            key={venue.id}
            onClick={() => navigate(`/place/${venue.id}`)}
            className="bg-sand rounded-2xl overflow-hidden text-left"
          >
            <div className={`relative h-24 bg-gradient-to-br ${CARD_GRADIENTS[i % CARD_GRADIENTS.length]}`}>
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
          </button>
        ))}
      </div>

      <nav className="fixed bottom-0 inset-x-0 mx-auto w-full max-w-[430px] bg-cream border-t border-cream-line px-6 py-3 flex items-center justify-between">
        <button aria-label="Keşfet" onClick={() => navigate('/home')} className="text-tan-dark">
          <Compass size={24} />
        </button>
        <button aria-label="Harita" onClick={() => navigate('/map')} className="text-taupe">
          <MapPin size={24} />
        </button>
        <button
          aria-label="Ekle"
          onClick={() => showComingSoon('Mekan ekleme')}
          className="w-12 h-12 -mt-6 rounded-full bg-tan flex items-center justify-center shadow-lg"
        >
          <Plus size={24} className="text-cream" />
        </button>
        <button aria-label="Mesajlar" onClick={() => navigate('/messages')} className="text-taupe">
          <MessageCircle size={24} />
        </button>
        <button aria-label="Profil" onClick={() => navigate('/profile')} className="text-taupe">
          <User size={24} />
        </button>
      </nav>

      {toast && (
        <div className="fixed bottom-24 inset-x-0 mx-auto w-fit max-w-[430px] z-10 rounded-full bg-espresso px-4 py-2 text-xs font-medium text-cream shadow-lg">
          {toast}
        </div>
      )}
    </div>
  )
}
