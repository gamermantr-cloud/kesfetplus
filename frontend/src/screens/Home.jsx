import { useEffect, useMemo, useRef, useState } from 'react'
import {
  Bell,
  BedDouble,
  Cloud,
  CloudFog,
  CloudLightning,
  CloudRain,
  CloudSnow,
  Compass,
  Landmark,
  MapPin,
  MessageCircle,
  Plus,
  Search,
  Sparkles,
  Sun,
  Theater,
  Trees,
  User,
  Utensils,
  Wine,
} from 'lucide-react'
import { motion, useReducedMotion } from 'motion/react'
import { useNavigate } from 'react-router-dom'
import FeaturedShowcase from '../components/FeaturedShowcase.jsx'
import SubcategoryChips from '../components/SubcategoryChips.jsx'
import Toast from '../components/Toast.jsx'
import VenueCardSkeleton from '../components/VenueCardSkeleton.jsx'
import VenueThumb from '../components/VenueThumb.jsx'
import { getPopularityScores, getWeather } from '../lib/api.js'
import { getAllVenues } from '../lib/data.js'
import { withSubcategory } from '../lib/gurmeSubcategories.js'
import { nearestDistrict } from '../lib/districts.js'
import { rankVenues } from '../lib/search.js'
import { useRestorableState } from '../lib/useRestorableState.js'
import { getVenueIcon } from '../lib/venueIcon.js'
import { isOutdoorWeatherSensitive } from '../lib/weather.js'

const CATEGORIES = [
  { id: 'dogu', label: 'Doğa', icon: Trees, match: (v) => v.kind === 'place' },
  { id: 'yeme', label: 'Yeme & İçme', icon: Utensils, match: (v) => v.kind === 'gurme' && v.category !== 'bar' },
  { id: 'otel', label: 'Oteller', icon: BedDouble, match: (v) => v.kind === 'hotel' },
  { id: 'bar', label: 'Barlar', icon: Wine, match: (v) => v.kind === 'gurme' && v.category === 'bar' },
  { id: 'sahne', label: 'Konser ve Tiyatro', icon: Theater, match: (v) => v.kind === 'sahne' || v.cross_categories?.includes('sahne') },
  { id: 'kultur', label: 'Kültür ve Tarih', icon: Landmark, match: (v) => v.kind === 'kultur' },
  { id: 'eklenti', label: 'Eklentiler', icon: Plus, match: null },
]

// Card backgrounds cycle through design-token gradients; used as a placeholder/fallback
// for venues that have no real photo (or whose photo fails to load).
const CARD_GRADIENTS = [
  'from-tan to-sand-dark',
  'from-espresso-soft to-tan-dark',
  'from-sand-dark to-tan',
  'from-tan-dark to-espresso-soft',
]

// WMO weather-code group (database/weather_cache.py condition_group) -> icon.
const WEATHER_ICONS = {
  clear: Sun,
  cloudy: Cloud,
  fog: CloudFog,
  rain: CloudRain,
  snow: CloudSnow,
  storm: CloudLightning,
  unknown: Cloud,
}

// "Varsayılan İstanbul merkezi" - kullanıcı konum izni vermediğinde/
// navigator.geolocation yoksa GET /api/weather/{district}'e gönderilen
// değer (backend bilinmeyen bir ilçe adını İstanbul'un genel merkez
// koordinatına düşürüyor, bkz. database/weather_cache.py _resolve_district).
const DEFAULT_WEATHER_DISTRICT = 'İstanbul'

export default function Home() {
  const navigate = useNavigate()
  const shouldReduceMotion = useReducedMotion()
  const [venues, setVenues] = useState([])
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [activeCategory, setActiveCategory] = useRestorableState('home-category', null)
  const [activeSubcategory, setActiveSubcategory] = useRestorableState('home-subcategory', null)
  const [toast, setToast] = useState(null)
  const toastTimer = useRef(null)
  // null = henüz yüklenmedi ya da Open-Meteo'ya ulaşılamadı - asla uydurma
  // bir sıcaklık/durum gösterilmez (CLAUDE.md "sahte veri yasak").
  const [weather, setWeather] = useState(null)
  const [weatherFailed, setWeatherFailed] = useState(false)
  // {} = henüz yüklenmedi ya da istek başarısız oldu - search.js bunu
  // "hiçbir venue için sinyal yok" olarak yorumlar, uydurma bir popülerlik
  // göstermez (bkz. lib/search.js popularityScore).
  const [popularityScores, setPopularityScores] = useState({})

  function showToast(message) {
    setToast(message)
    clearTimeout(toastTimer.current)
    toastTimer.current = setTimeout(() => setToast(null), 1800)
  }

  useEffect(() => () => clearTimeout(toastTimer.current), [])

  // Hava durumu şeridi: konum izni varsa en yakın ilçe, yoksa/GPS
  // desteklenmiyorsa/izin reddedilirse varsayılan İstanbul merkezi (aynı
  // opt-in + zarif düşme deseni PlaceDetail.jsx'in check-in akışında da
  // kullanılıyor). Gerçek Open-Meteo verisi gelmezse weather null kalır ve
  // aşağıda dürüstçe "hava durumu bilgisi şu an yok" gösterilir.
  useEffect(() => {
    let cancelled = false
    function loadWeather(district) {
      getWeather(district)
        .then((data) => {
          if (!cancelled) setWeather(data)
        })
        .catch((err) => {
          console.error('getWeather failed', err)
          if (!cancelled) setWeatherFailed(true)
        })
    }
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => loadWeather(nearestDistrict(pos.coords.latitude, pos.coords.longitude)),
        () => loadWeather(DEFAULT_WEATHER_DISTRICT),
        { timeout: 8000, maximumAge: 300000 },
      )
    } else {
      loadWeather(DEFAULT_WEATHER_DISTRICT)
    }
    return () => {
      cancelled = true
    }
  }, [])

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

  // Popülerlik sinyalleri (checkin/helpful) ayrı, tek seferlik bir istekle
  // gelir - venue listesi gibi render'ı bloklamaz, gelince sıralama
  // otomatik güncellenir (bkz. lib/search.js rankVenues).
  useEffect(() => {
    let cancelled = false
    getPopularityScores().then((data) => {
      if (!cancelled) setPopularityScores(data)
    })
    return () => {
      cancelled = true
    }
  }, [])

  const featured = useMemo(() => {
    if (!venues.length) return null
    return venues.find((v) => v.id === 'emirgan') ?? venues.find((v) => v.tags?.includes('manzara')) ?? venues[0]
  }, [venues])

  const filtered = useMemo(() => {
    const category = CATEGORIES.find((c) => c.id === activeCategory)
    return rankVenues(venues, {
      query,
      category: activeCategory === 'yeme' ? withSubcategory(category, activeSubcategory) : category,
      popularityScores,
      excludeId: featured?.id,
    })
  }, [venues, activeCategory, activeSubcategory, query, featured, popularityScores])

  function handleQuickCheckin() {
    if (!featured) {
      showToast('Mekanlar yükleniyor, birazdan tekrar dene')
      return
    }
    // Sends the user straight into the featured venue's "Anlık Durum" tab,
    // which hosts the existing check-in/durum-paylaşma flow (PlaceDetail.jsx).
    navigate(`/place/${featured.id}?tab=durum`)
  }

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
              onClick={() => {
                setActiveCategory(active ? null : cat.id)
                setActiveSubcategory(null)
              }}
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
      {activeCategory === 'yeme' && (
        <SubcategoryChips active={activeSubcategory} onChange={setActiveSubcategory} />
      )}

      {weather && (
        <div className="px-5 mt-4">
          {(() => {
            const WeatherIcon = WEATHER_ICONS[weather.condition_group] ?? Cloud
            return (
              <div className="flex items-center gap-2 bg-sand/70 rounded-2xl px-4 py-2.5">
                <WeatherIcon size={18} className="text-tan-dark shrink-0" />
                <p className="text-sm text-espresso-soft">
                  <span className="font-medium text-espresso">
                    {Math.round(weather.temperature)}°C
                  </span>{' '}
                  · {weather.district} · {weather.condition}
                  {!weather.is_outdoor_friendly && (
                    <span className="text-taupe">
                      {' '}
                      — bugün açık hava mekanları yerine kapalı mekanlar daha uygun olabilir
                    </span>
                  )}
                </p>
              </div>
            )
          })()}
          <p className="mt-1 text-[10px] text-taupe">Hava durumu verisi: Open-Meteo.com</p>
        </div>
      )}
      {!weather && weatherFailed && (
        <div className="px-5 mt-4">
          <p className="text-xs text-taupe">Hava durumu bilgisi şu an yok.</p>
        </div>
      )}

      <div className="px-5 mt-5">
        {venues.length > 0 && (
          <FeaturedShowcase venues={venues} onOpen={(venue) => navigate(`/place/${venue.id}`)} />
        )}
      </div>

      <div className="flex items-center justify-between px-5 mt-7">
        <h3 className="font-display text-lg text-espresso">Sana Özel Seçimler</h3>
        <button onClick={() => navigate('/explore')} className="text-tan-dark text-sm font-medium">
          Tümünü Gör
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 px-5 mt-3">
        {loading && <VenueCardSkeleton count={6} />}
        {!loading && filtered.length === 0 && (
          <p className="col-span-2 text-taupe text-sm">Bu kritere uyan mekan bulunamadı.</p>
        )}
        {filtered.slice(0, 12).map((venue, i) => {
          const VenueIcon = getVenueIcon(venue)
          // Yağmurlu/karlı/fırtınalı/sisli bir günde açık-hava-duyarlı
          // mekanlara nazik bir rozet - sadece gerçek weather verisi
          // geldiyse (weather null iken hiçbir rozet gösterilmez).
          const showWeatherBadge = Boolean(weather) && !weather.is_outdoor_friendly && isOutdoorWeatherSensitive(venue)
          return (
          <motion.button
            type="button"
            key={venue.id}
            onClick={() => navigate(`/place/${venue.id}`)}
            className="bg-sand rounded-2xl overflow-hidden text-left grain"
            initial={shouldReduceMotion ? false : { opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.22, delay: shouldReduceMotion ? 0 : Math.min(i * 0.03, 0.15) }}
            whileTap={shouldReduceMotion ? undefined : { scale: 0.96, y: 1 }}
          >
            <VenueThumb
              venue={venue}
              gradientClass={CARD_GRADIENTS[i % CARD_GRADIENTS.length]}
              Icon={VenueIcon}
              leftBadge={
                showWeatherBadge && (
                  <div
                    title="Bugün yağmurlu, kapalı mekanlar daha uygun olabilir"
                    className="absolute top-2 left-2 flex items-center gap-1 bg-cream/90 rounded-full px-2 py-0.5 text-[10px] font-medium text-tan-dark"
                  >
                    <CloudRain size={11} />
                    Hava duyarlı
                  </div>
                )
              }
            />
            <div className="p-3">
              <p className="text-sm font-medium text-espresso truncate">{venue.name}</p>
              {venue.area && <p className="text-xs text-taupe truncate mt-0.5">{venue.area}</p>}
            </div>
          </motion.button>
          )
        })}
      </div>

      <nav className="fixed bottom-0 inset-x-0 mx-auto w-full max-w-[430px] bg-cream border-t border-cream-line px-6 py-3 flex items-center justify-between">
        <button aria-label="Keşfet" onClick={() => navigate('/home')} className="text-tan-dark">
          <Compass size={24} />
        </button>
        <button aria-label="Harita" onClick={() => navigate('/map')} className="text-taupe">
          <MapPin size={24} />
        </button>
        <motion.button
          aria-label="Hızlı check-in"
          onClick={handleQuickCheckin}
          whileTap={shouldReduceMotion ? undefined : { scale: 0.96 }}
          className="w-12 h-12 -mt-6 rounded-full bg-tan flex items-center justify-center shadow-lg"
        >
          <Plus size={24} className="text-cream" />
        </motion.button>
        <button aria-label="Mesajlar" onClick={() => navigate('/messages')} className="text-taupe">
          <MessageCircle size={24} />
        </button>
        <button aria-label="Profil" onClick={() => navigate('/profile')} className="text-taupe">
          <User size={24} />
        </button>
      </nav>

      <Toast message={toast} className="bottom-24" />
    </div>
  )
}
