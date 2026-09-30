import {
  AlertTriangle,
  Bug,
  Camera,
  ChevronDown,
  ChevronLeft,
  Cloud,
  CloudFog,
  CloudLightning,
  CloudRain,
  CloudSnow,
  Flag,
  Loader2,
  MapPin,
  Navigation,
  Send,
  ShieldQuestion,
  Star,
  Sun,
  Telescope,
  ThumbsUp,
  UserX,
  Users,
  Video,
  Wallet,
  X,
} from 'lucide-react'
import { AnimatePresence, motion, useReducedMotion } from 'motion/react'
import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import {
  comparePhoto,
  getCheckinCount,
  getComments,
  getStatusUpdates,
  getUserStats,
  getWeather,
  markCommentHelpful,
  markStatusHelpful,
  postCheckin,
  postComment,
  postStatusUpdate,
  reportContent,
} from '../lib/api.js'
import { useAuth } from '../lib/AuthContext.jsx'
import { getAllVenues } from '../lib/data.js'
import { isOutdoorWeatherSensitive } from '../lib/weather.js'

const TABS = ['Genel Bakış', 'Anlık Durum', 'Fotoğraflar', 'Yorumlar']
const STATUS_TAGS = ['Kalabalık', 'Orta', 'Sakin']

// "Kene Bilgisi" rozeti sadece çim/yeşillik temalı doğa mekanlarında
// gösterilir - venue.tags üzerinden basit bir kesişim kontrolü (yeni bir
// veri alanı/dosya YOK, mevcut tags'a göre türetilmiş bir UI kararı,
// isOutdoorWeatherSensitive'deki desenle aynı fikir - bkz. lib/weather.js).
const TICK_INFO_TAGS = new Set([
  'orman',
  'orman yürüyüşü',
  'kent ormanı',
  'koru',
  'çayır',
  'otlak',
  'piknik',
  'mesire',
  'yürüyüş',
  'doğa yürüyüşü',
  'kamp',
  'kamp ateşi',
  'bisiklet',
  'tabiat parkı',
  'doğa koruma alanı',
])

// Tüm doğa mekanları için TEK, sabit ve genel bir bilgi metni - mekana özel
// değil, bu yüzden places.json'a eklenmiyor (CLAUDE.md "sahte veri yasak" -
// bu zaten gerçek bir veri değil, genel bir güvenlik hatırlatması).
const TICK_INFO_INTRO =
  'KKKA (Kırım Kongo Kanamalı Ateşi) için bilinen hiperendemik bölgeler Orta ve ' +
  'Doğu Karadeniz, İç Anadolu\'nun kuzeyi ve Doğu Anadolu\'daki yaklaşık 30 il ' +
  '(örn. Tokat, Sivas, Çorum, Erzurum, Gümüşhane, Bayburt). İstanbul bu ' +
  'hiperendemik bölgeler arasında yer almıyor, ancak keneler ağaçlardan değil ' +
  'ot/çalı/çimenlik alanlardan bulaşır — bu yüzden ormanlık alanlarla sınırlı ' +
  'olmayan genel bir mevsimsel dikkat (Mayıs-Ekim) her bölge için geçerlidir.'

const TICK_INFO_SPECIES = [
  {
    name: 'Hyalomma cinsi',
    desc: "Kırım Kongo Kanamalı Ateşi'nin (KKKA) başlıca taşıyıcısı. Kurak/yarı kurak, açık ve çalılık arazilerde yaygın.",
    regions: "İç Anadolu, Karadeniz'in iç kesimleri, Doğu Anadolu; kıyı bölgelerinde de bildirilmiştir.",
  },
  {
    name: 'Rhipicephalus cinsi',
    desc: 'İlkbahar, yaz ve sonbaharda aktif; çiftlik hayvanları ve otlaklarla ilişkili.',
    regions: 'Ülke genelinde yaygın.',
  },
  {
    name: 'Dermacentor marginatus',
    desc: 'Özellikle sonbaharda yoğunluğu artar.',
    regions: 'Ülke genelinde, özellikle orman kenarı ve çayırlık alanlar.',
  },
  {
    name: 'Haemaphysalis cinsi',
    desc: 'Sonbahar ve kışın yoğunluğu artabilir. Bu cinse ait, ülkeye yeni yerleşen istilacı bir tür de bildirilmiştir.',
    regions: 'Ülke genelinde.',
  },
]

const TICK_INFO_FOOTER =
  'Bu bilgiler genel farkındalık amaçlıdır, belirli bir mekân için ölçülmüş veri ' +
  'değildir. Kene ısırığı sonrası ateş, halsizlik veya kas ağrısı gibi belirtiler ' +
  'görülürse vakit kaybetmeden bir sağlık kuruluşuna başvurun.'

function hasTickInfoTag(venue) {
  if (!venue?.tags?.length) return false
  return venue.tags.some((tag) => TICK_INFO_TAGS.has(tag))
}

// WMO weather-code group (database/weather_cache.py condition_group) -> icon.
// Aynı eşleme Home.jsx'te de kullanılıyor - kasıtlı olarak tutarlı tutuldu.
const WEATHER_ICONS = {
  clear: Sun,
  cloudy: Cloud,
  fog: CloudFog,
  rain: CloudRain,
  snow: CloudSnow,
  storm: CloudLightning,
  unknown: Cloud,
}

// Shown when the caller's own just-submitted comment/status came back with
// flagged_reason === "objectionable_content" (see database/content_filter.py).
// The content IS saved (never silently dropped, see comments_store.py /
// checkins_store.py) but forced to review_status="hidden" - so it's honest,
// not accusatory, and doesn't claim the content is still visible anywhere.
const OBJECTIONABLE_CONTENT_MESSAGE =
  'İçeriğin topluluk kurallarına aykırı bulundu, bu yüzden şu an yayınlanmadı. ' +
  'Bunun bir hata olduğunu düşünüyorsan bizimle iletişime geçebilirsin.'

// "Açıklanabilir güven skoru" - flagged_reason -> author-only explanation
// (see docs/research/rakip-analizi-guncelleme-2026-09-30.md Bolum 3 and
// database/trust_scoring.py). Each message names only which *signal* came
// back low ("konumun uzak görünüyor", "çok benzer bir yorum"), never the
// numeric score or the signals' weights/thresholds (those stay entirely
// server-side, see trust_scoring.py's ACCOUNT/LOCATION/TEXT/VELOCITY
// *_SIGNAL_MAX constants - nothing like them is ever sent to the frontend).
// The backend (database/comments_store.list_comments /
// checkins_store.list_status) already strips flagged_reason down to null
// for every comment/status that isn't the requesting viewer's own, so this
// map is never even reachable with someone else's reason - this is a
// second, defense-in-depth check, not the only one.
const FLAGGED_REASON_MESSAGES = {
  duplicate_text: 'Yorumun, daha önce paylaşılan bir yoruma çok benziyor gibi görünüyor.',
  velocity_spike: 'Kısa sürede çok fazla paylaşım yaptığın için yorumun inceleniyor.',
  unverified_location: 'Konumun mekana biraz uzak görünüyor, bu yüzden yorumun inceleniyor.',
  objectionable_content: OBJECTIONABLE_CONTENT_MESSAGE,
}

/**
 * The author-only "why is my comment/status pending or hidden" explanation
 * for `item`, or null when none applies - either it isn't flagged, its
 * review_status isn't pending/hidden, or (most importantly) `item` isn't
 * `currentUserId`'s own content. flagged_reason can be a comma-joined list
 * (database/trust_scoring.py score_comment can fire more than one signal at
 * once) - the first recognized reason is shown rather than stacking all of
 * them, so this reads as a simple explanation, not a lecture.
 */
function ownFlaggedMessage(item, currentUserId) {
  if (!currentUserId || !item.author_user_id || item.author_user_id !== currentUserId) {
    return null
  }
  if (item.review_status !== 'pending_review' && item.review_status !== 'hidden') return null
  const reasons = (item.flagged_reason ?? '').split(',').map((r) => r.trim())
  for (const reason of reasons) {
    if (FLAGGED_REASON_MESSAGES[reason]) return FLAGGED_REASON_MESSAGES[reason]
  }
  return null
}

function timeAgo(isoString) {
  const then = new Date(isoString).getTime()
  const diffMs = Date.now() - then
  const minutes = Math.floor(diffMs / 60000)
  if (minutes < 1) return 'az önce'
  if (minutes < 60) return `${minutes} dakika önce`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours} saat önce`
  const days = Math.floor(hours / 24)
  return `${days} gün önce`
}

function priceLevelLabel(priceLevel) {
  if (!priceLevel) return 'Veri yok'
  return '₺'.repeat(priceLevel)
}

function crowdLabel(venue) {
  return venue.crowdNow ?? venue.crowdToday ?? 'Veri yok'
}

export default function PlaceDetail() {
  const { placeId } = useParams()
  const navigate = useNavigate()
  const shouldReduceMotion = useReducedMotion()
  const { user, isLoggedIn, block } = useAuth()
  const loginState = { state: { from: `/place/${placeId}` } }
  const [searchParams] = useSearchParams()

  const [venue, setVenue] = useState(undefined) // undefined = loading, null = not found
  // Lets callers (e.g. Home's quick check-in shortcut) deep-link straight
  // into a tab via ?tab=durum instead of always landing on "Genel Bakış".
  const [activeTab, setActiveTab] = useState(
    searchParams.get('tab') === 'durum' ? 'Anlık Durum' : TABS[0],
  )

  const [comments, setComments] = useState([])
  const [commentsLoading, setCommentsLoading] = useState(true)
  const [commentsError, setCommentsError] = useState(null)

  const [showForm, setShowForm] = useState(false)
  const [text, setText] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [contentNotice, setContentNotice] = useState(null)

  const [checkedIn, setCheckedIn] = useState(false)
  const [checkinLoading, setCheckinLoading] = useState(false)
  const [checkinNote, setCheckinNote] = useState(null)
  const [checkinCount, setCheckinCount] = useState(null)
  const [statusUpdates, setStatusUpdates] = useState([])
  const [statusLoading, setStatusLoading] = useState(true)
  const [statusError, setStatusError] = useState(null)
  const [selectedTag, setSelectedTag] = useState(null)
  const [statusText, setStatusText] = useState('')
  const [statusSubmitting, setStatusSubmitting] = useState(false)
  const [statusContentNotice, setStatusContentNotice] = useState(null)

  const [tickInfoOpen, setTickInfoOpen] = useState(false)

  const [comparePanelOpen, setComparePanelOpen] = useState(false)
  const [compareLoading, setCompareLoading] = useState(false)
  const [compareResult, setCompareResult] = useState(null)
  const [compareError, setCompareError] = useState(null)

  // author_user_id -> badges[] (e.g. ["gozcu"]) - fetched lazily per unique
  // status author, see the effect below. Not fetched for comment authors
  // (task marks the "Gözcü" tag on status updates as the important spot,
  // comments optional/out of scope).
  const [authorBadges, setAuthorBadges] = useState({})

  useEffect(() => {
    let cancelled = false
    getAllVenues().then((venues) => {
      if (cancelled) return
      setVenue(venues.find((v) => v.id === placeId) ?? null)
    })
    return () => {
      cancelled = true
    }
  }, [placeId])

  // Mekanın bulunduğu ilçenin gerçek anlık hava durumu (Genel Bakış
  // sekmesindeki her zaman görünen WeatherCard İÇİN, ayrıca aşağıdaki
  // koşullu açık-hava uyarısı da aynı veriyi kullanıyor - iki ayrı istek
  // atılmıyor). venue.area backend'e olduğu gibi gönderiliyor;
  // database/weather_cache.py._resolve_district "Sarıyer (Emirgan)" gibi
  // tam area string'lerinden de ilk bilinen ilçe adını substring olarak
  // buluyor, ayrıca bir formatlama/encode işi frontend'de gerekmiyor
  // (getWeather zaten encodeURIComponent kullanıyor, bkz. lib/api.js).
  // weather null kalırsa (Open-Meteo'ya ulaşılamazsa) weatherFailed true
  // olur ve dürüstçe "hava durumu bilgisi şu an yok" gösterilir - uydurma
  // sıcaklık/son-bilinen değer YOK (CLAUDE.md "sahte veri yasak").
  const [weather, setWeather] = useState(null)
  const [weatherLoading, setWeatherLoading] = useState(true)
  const [weatherFailed, setWeatherFailed] = useState(false)
  useEffect(() => {
    if (!venue?.area) {
      setWeatherLoading(false)
      return undefined
    }
    let cancelled = false
    setWeatherLoading(true)
    setWeatherFailed(false)
    getWeather(venue.area)
      .then((data) => {
        if (!cancelled) setWeather(data)
      })
      .catch((err) => {
        console.error('getWeather failed', err)
        if (!cancelled) setWeatherFailed(true)
      })
      .finally(() => {
        if (!cancelled) setWeatherLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [venue?.area])

  const loadComments = useMemo(
    () => async () => {
      setCommentsLoading(true)
      setCommentsError(null)
      try {
        const data = await getComments(placeId)
        setComments(data)
      } catch (err) {
        console.error('getComments failed', err)
        setCommentsError('Yorumlar şu an yüklenemedi. Birazdan tekrar dener misin?')
      } finally {
        setCommentsLoading(false)
      }
    },
    [placeId],
  )

  useEffect(() => {
    loadComments()
  }, [loadComments])

  const loadStatus = useMemo(
    () => async () => {
      setStatusLoading(true)
      try {
        const data = await getStatusUpdates(placeId)
        setStatusUpdates(data)
      } catch (err) {
        console.error('getStatusUpdates failed', err)
        setStatusError('Anlık durumlar şu an yüklenemedi. Birazdan tekrar dener misin?')
      } finally {
        setStatusLoading(false)
      }
    },
    [placeId],
  )

  const loadCheckinCount = useMemo(
    () => async () => {
      try {
        const data = await getCheckinCount(placeId)
        setCheckinCount(data.count)
      } catch {
        setCheckinCount(null)
      }
    },
    [placeId],
  )

  useEffect(() => {
    loadStatus()
    loadCheckinCount()
  }, [loadStatus, loadCheckinCount])

  // Lazily fetch "Gözcü" badge info for status authors not yet looked up.
  // Guarded so it only ever fetches ids missing from authorBadges - once an
  // id has an entry (even []), it's never re-fetched for this mount.
  useEffect(() => {
    let cancelled = false
    const ids = [...new Set(statusUpdates.map((s) => s.author_user_id).filter(Boolean))]
    const toFetch = ids.filter((id) => authorBadges[id] === undefined)
    if (toFetch.length === 0) return undefined
    Promise.all(
      toFetch.map((id) =>
        getUserStats(id)
          .then((stats) => [id, stats.badges ?? []])
          .catch(() => [id, []]),
      ),
    ).then((pairs) => {
      if (cancelled) return
      setAuthorBadges((prev) => {
        const next = { ...prev }
        for (const [id, badges] of pairs) next[id] = badges
        return next
      })
    })
    return () => {
      cancelled = true
    }
  }, [statusUpdates, authorBadges])

  async function handleCheckin() {
    if (!isLoggedIn) {
      navigate('/login', loginState)
      return
    }
    setCheckinLoading(true)
    setCheckinNote(null)
    setStatusError(null)

    const submit = async (lat, lng, accuracy, note) => {
      try {
        await postCheckin(placeId, { lat, lng, accuracy })
        setCheckedIn(true)
        setCheckinNote(note)
        await Promise.all([loadStatus(), loadCheckinCount()])
      } catch (err) {
        console.error('postCheckin failed', err)
        setStatusError('Check-in şu an gönderilemedi. Birazdan tekrar dener misin?')
      } finally {
        setCheckinLoading(false)
      }
    }

    if (!navigator.geolocation) {
      await submit(null, null, null, 'Bu tarayıcı konum servisini desteklemiyor, konum olmadan paylaşıldı.')
      return
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        submit(pos.coords.latitude, pos.coords.longitude, pos.coords.accuracy, null)
      },
      () => {
        submit(null, null, null, 'Konum izni olmadan da durum paylaşabilirsin.')
      },
      { timeout: 8000, maximumAge: 60000 },
    )
  }

  async function handleStatusSubmit() {
    if (!isLoggedIn || !selectedTag) return
    setStatusSubmitting(true)
    setStatusError(null)
    try {
      const created = await postStatusUpdate(placeId, { tag: selectedTag, text: statusText.trim() })
      setStatusContentNotice(
        created?.flagged_reason === 'objectionable_content' ? OBJECTIONABLE_CONTENT_MESSAGE : null,
      )
      setSelectedTag(null)
      setStatusText('')
      await loadStatus()
    } catch (err) {
      console.error('postStatusUpdate failed', err)
      setStatusError('Durumun şu an paylaşılamadı. Birazdan tekrar dener misin?')
    } finally {
      setStatusSubmitting(false)
    }
  }

  async function handleCommentHelpful(commentId) {
    try {
      await markCommentHelpful(placeId, commentId)
      await loadComments()
    } catch {
      setCommentsError('İşlem gerçekleştirilemedi.')
    }
  }

  async function handleStatusHelpful(statusId) {
    try {
      await markStatusHelpful(placeId, statusId)
      await loadStatus()
    } catch {
      setStatusError('İşlem gerçekleştirilemedi.')
    }
  }

  function getCommentLocation() {
    // Optional/rejectable, same pattern as check-in: declining location
    // permission never blocks or penalizes the comment (see
    // database/trust_scoring.py signal 2 - "neutral" without GPS).
    return new Promise((resolve) => {
      if (!navigator.geolocation) {
        resolve({ lat: null, lng: null, accuracy: null })
        return
      }
      navigator.geolocation.getCurrentPosition(
        (pos) => resolve({ lat: pos.coords.latitude, lng: pos.coords.longitude, accuracy: pos.coords.accuracy }),
        () => resolve({ lat: null, lng: null, accuracy: null }),
        { timeout: 8000, maximumAge: 60000 },
      )
    })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!text.trim()) return
    setSubmitting(true)
    try {
      const { lat, lng, accuracy } = await getCommentLocation()
      const created = await postComment(placeId, { text: text.trim(), lat, lng, accuracy })
      setContentNotice(
        created?.flagged_reason === 'objectionable_content' ? OBJECTIONABLE_CONTENT_MESSAGE : null,
      )
      setText('')
      setShowForm(false)
      await loadComments()
    } catch (err) {
      console.error('postComment failed', err)
      setCommentsError('Yorumun şu an gönderilemedi. Birazdan tekrar dener misin?')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleBlock(authorUserId) {
    try {
      await block(authorUserId)
      await Promise.all([loadComments(), loadStatus()])
    } catch {
      setCommentsError('Kullanıcı engellenemedi.')
    }
  }

  async function handleComparePhoto(file) {
    if (!file) return
    setCompareLoading(true)
    setCompareError(null)
    setCompareResult(null)
    try {
      const result = await comparePhoto(placeId, file)
      setCompareResult(result)
    } catch (err) {
      console.error('comparePhoto failed', err)
      setCompareError('Karşılaştırma şu an yapılamadı. Birazdan tekrar dener misin?')
    } finally {
      setCompareLoading(false)
    }
  }

  function closeComparePanel() {
    setComparePanelOpen(false)
    setCompareLoading(false)
    setCompareResult(null)
    setCompareError(null)
  }

  function openMap() {
    const query = encodeURIComponent(`${venue.name} ${venue.address ?? venue.area ?? ''}`)
    window.open(`https://www.google.com/maps/search/?api=1&query=${query}`, '_blank', 'noopener,noreferrer')
  }

  if (venue === undefined) {
    return (
      <div className="flex min-h-screen items-center justify-center text-taupe">
        <Loader2 className="animate-spin" size={20} />
      </div>
    )
  }

  if (venue === null) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-3 p-6 text-center">
        <p className="font-display text-xl text-espresso">Mekan bulunamadı</p>
        <p className="text-sm text-taupe">"{placeId}" için kayıt yok.</p>
        <button
          type="button"
          onClick={() => navigate('/home')}
          className="mt-2 rounded-full bg-tan px-5 py-2 text-sm font-medium text-cream"
        >
          Ana sayfaya dön
        </button>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen flex-col pb-28">
      {/* Photo header */}
      <div className="relative h-64 w-full shrink-0 overflow-hidden">
        {venue.photos && venue.photos.length > 0 ? (
          <img
            src={venue.photos[0].url}
            alt={`${venue.name} fotoğrafı`}
            className="absolute inset-0 h-full w-full object-cover"
          />
        ) : (
          <div className="absolute inset-0 bg-gradient-to-br from-tan via-tan-dark to-espresso" />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-espresso/80 via-espresso/10 to-transparent" />
        <button
          type="button"
          onClick={() => navigate(-1)}
          aria-label="Geri"
          className="absolute left-4 top-4 flex h-10 w-10 items-center justify-center rounded-full bg-espresso/40 text-cream backdrop-blur-sm"
        >
          <ChevronLeft size={22} />
        </button>
      </div>

      {/* Title block */}
      <div className="border-b border-cream-line px-6 py-5">
        <h1 className="font-display text-2xl font-medium text-espresso">{venue.name}</h1>
        <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1">
          {venue.rating ? (
            <span className="flex items-center gap-1 text-sm font-medium text-espresso">
              <Star size={15} className="fill-gold text-gold" />
              {venue.rating.toFixed(1)}
            </span>
          ) : (
            <span className="flex items-center gap-1 text-sm text-taupe">
              <Star size={15} />
              Puan yok
            </span>
          )}
          {venue.reviewCount ? (
            <span className="text-sm text-taupe">({venue.reviewCount} yorum)</span>
          ) : null}
        </div>
        <p className="mt-1 text-sm text-taupe">
          {venue.area}
          {venue.address ? ` · ${venue.address}` : ''}
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-cream-line px-2">
        {TABS.map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className={`flex-1 border-b-2 px-2 py-3 text-xs font-medium transition-colors ${
              activeTab === tab
                ? 'border-tan text-espresso'
                : 'border-transparent text-taupe'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="flex-1 px-6 py-5">
        {/*
          Opacity-only fade (no transform) on tab switch. Deliberately not a
          slide: the Fotoğraflar tab renders `fixed`-positioned children (the
          compare-photo button/panel), and a non-"none" transform on this
          wrapper would change their containing block to this div instead of
          the viewport - opacity doesn't have that side effect.
        */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={shouldReduceMotion ? false : { opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={shouldReduceMotion ? undefined : { opacity: 0 }}
            transition={{ duration: 0.16, ease: 'easeOut' }}
          >
        {activeTab === 'Genel Bakış' && (
          <div>
            <WeatherCard weather={weather} loading={weatherLoading} failed={weatherFailed} />
            {hasTickInfoTag(venue) && (
              <div className="mb-4">
                <button
                  type="button"
                  onClick={() => setTickInfoOpen((open) => !open)}
                  aria-expanded={tickInfoOpen}
                  className="flex w-full items-center justify-between gap-2 rounded-2xl border border-cream-line bg-sand/40 px-4 py-3 text-sm font-medium text-espresso"
                >
                  <span className="flex items-center gap-2">
                    <Bug size={16} className="shrink-0 text-tan-dark" />
                    Kene Bilgisi
                  </span>
                  <ChevronDown
                    size={16}
                    className={`shrink-0 text-taupe transition-transform ${tickInfoOpen ? 'rotate-180' : ''}`}
                  />
                </button>
                {tickInfoOpen && (
                  <div className="mt-2 space-y-3 rounded-2xl bg-sand px-4 py-3 text-sm leading-relaxed text-espresso-soft">
                    <p>{TICK_INFO_INTRO}</p>
                    <ul className="space-y-2">
                      {TICK_INFO_SPECIES.map((species) => (
                        <li key={species.name} className="rounded-xl bg-cream/60 px-3 py-2">
                          <p className="font-medium text-espresso">{species.name}</p>
                          <p>{species.desc}</p>
                          <p className="text-taupe">Görüldüğü bölgeler: {species.regions}</p>
                        </li>
                      ))}
                    </ul>
                    <p className="text-taupe">{TICK_INFO_FOOTER}</p>
                  </div>
                )}
              </div>
            )}
            {weather && !weather.is_outdoor_friendly && isOutdoorWeatherSensitive(venue) && (
              <div className="mb-4 flex items-start gap-2 rounded-2xl bg-sand px-4 py-3 text-sm text-espresso-soft">
                <CloudRain size={16} className="mt-0.5 shrink-0 text-tan-dark" />
                <p>
                  Bugün {venue.area ?? 'bu bölgede'} {weather.condition.toLowerCase()} görünüyor —
                  bu açık hava mekanı için ideal olmayabilir.
                </p>
              </div>
            )}
            <div className="grid grid-cols-2 gap-3">
              <StatCard
                icon={<Users size={18} />}
                label="Yoğunluk"
                value={crowdLabel(venue)}
              />
              <StatCard
                icon={<Wallet size={18} />}
                label="Fiyat"
                value={priceLevelLabel(venue.priceLevel)}
              />
            </div>
            {venue.note ? (
              <p className="mt-5 text-sm leading-relaxed text-espresso-soft">{venue.note}</p>
            ) : null}
          </div>
        )}

        {activeTab === 'Anlık Durum' && (
          <div className="space-y-4">
            <StatCard
              icon={<Users size={18} />}
              label="Son 2 saatte buradaydı"
              value={checkinCount ? `${checkinCount} kişi` : 'Henüz veri yok'}
              wide
            />

            {statusError && <p className="text-sm text-tan-dark">{statusError}</p>}
            {statusContentNotice && <p className="text-sm text-tan-dark">{statusContentNotice}</p>}

            {!isLoggedIn ? (
              <button
                type="button"
                onClick={() => navigate('/login', loginState)}
                className="flex w-full items-center justify-center gap-2 rounded-full bg-tan px-4 py-3 text-sm font-medium text-cream"
              >
                Durum paylaşmak için giriş yap
              </button>
            ) : !checkedIn ? (
              <motion.button
                type="button"
                onClick={handleCheckin}
                disabled={checkinLoading}
                whileTap={shouldReduceMotion ? undefined : { scale: 0.96 }}
                className="flex w-full items-center justify-center gap-2 rounded-full bg-tan px-4 py-3 text-sm font-medium text-cream disabled:opacity-60"
              >
                {checkinLoading ? (
                  <Loader2 size={16} className="animate-spin" />
                ) : (
                  <Navigation size={16} />
                )}
                Buradayım
              </motion.button>
            ) : (
              <div className="space-y-3 rounded-2xl border border-cream-line bg-sand/50 p-4">
                {checkinNote && <p className="text-xs text-taupe">{checkinNote}</p>}
                <p className="text-sm font-medium text-espresso">
                  İsteğe bağlı: buradaki durumu hızlıca paylaş
                </p>
                <div className="flex gap-2">
                  {STATUS_TAGS.map((tag) => (
                    <button
                      key={tag}
                      type="button"
                      onClick={() => setSelectedTag(tag)}
                      className={`flex-1 rounded-full border px-3 py-2 text-xs font-medium transition-colors ${
                        selectedTag === tag
                          ? 'border-tan bg-tan text-cream'
                          : 'border-cream-line text-espresso'
                      }`}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
                <textarea
                  placeholder="Kısa bir not (opsiyonel)"
                  value={statusText}
                  onChange={(e) => setStatusText(e.target.value)}
                  rows={2}
                  className="w-full resize-none rounded-lg border border-cream-line bg-cream px-3 py-2 text-sm text-espresso outline-none focus:border-tan"
                />
                <motion.button
                  type="button"
                  onClick={handleStatusSubmit}
                  disabled={!selectedTag || statusSubmitting}
                  whileTap={shouldReduceMotion ? undefined : { scale: 0.96 }}
                  className="flex w-full items-center justify-center gap-2 rounded-full bg-tan px-4 py-2 text-sm font-medium text-cream disabled:opacity-60"
                >
                  {statusSubmitting ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                  Paylaş
                </motion.button>
              </div>
            )}

            <div>
              <p className="mb-2 text-xs font-medium uppercase tracking-wide text-taupe">
                Paylaşılan durumlar
              </p>
              {statusLoading ? (
                <div className="flex justify-center py-6 text-taupe">
                  <Loader2 className="animate-spin" size={18} />
                </div>
              ) : statusUpdates.length === 0 ? (
                <p className="py-6 text-center text-sm text-taupe">
                  Henüz kimse durum paylaşmadı. İlk paylaşan sen ol.
                </p>
              ) : (
                <ul className="space-y-2">
                  {statusUpdates
                    .slice()
                    .reverse()
                    .map((s) => (
                      <li
                        key={s.id}
                        className={`rounded-2xl border border-cream-line bg-sand/40 p-3 grain ${
                          s.is_stale ? 'opacity-50' : ''
                        }`}
                      >
                        <p className="text-sm text-espresso-soft">
                          <span className="text-taupe">{timeAgo(s.created_at)}, </span>
                          <span className="font-medium text-espresso">{s.author}</span>
                          {s.author_user_id && authorBadges[s.author_user_id]?.includes('gozcu') && (
                            <span
                              title="Gözcü rozeti: 10+ durum paylaşımı"
                              className="ml-1 inline-flex items-center gap-0.5 rounded-full bg-gold/20 px-1.5 py-0.5 text-[10px] font-medium text-tan-dark"
                            >
                              <Telescope size={10} />
                              Gözcü
                            </span>
                          )}
                          <span className="text-taupe"> paylaştı: </span>
                          <span className="font-medium text-espresso">{s.tag}</span>
                          {s.text ? ` — ${s.text}` : ''}
                        </p>
                        {s.is_stale && <p className="mt-0.5 text-xs text-taupe">Eski bilgi</p>}
                        {ownFlaggedMessage(s, user?.id) && (
                          <p className="mt-1.5 text-xs text-tan-dark">
                            {ownFlaggedMessage(s, user?.id)}
                          </p>
                        )}
                        <div className="mt-2 flex flex-wrap items-center gap-3">
                          <HelpfulButton
                            item={s}
                            currentUserId={user?.id}
                            isLoggedIn={isLoggedIn}
                            onNavigateLogin={() => navigate('/login', loginState)}
                            onToggle={() => handleStatusHelpful(s.id)}
                          />
                          <ModerationRow
                            item={s}
                            targetType="status"
                            placeId={placeId}
                            currentUserId={user?.id}
                            isLoggedIn={isLoggedIn}
                            onBlock={handleBlock}
                          />
                        </div>
                      </li>
                    ))}
                </ul>
              )}
            </div>
          </div>
        )}

        {activeTab === 'Fotoğraflar' && (
          <div>
            {venue.photos && venue.photos.length > 0 ? (
              <div className="grid grid-cols-2 gap-3">
                {venue.photos.map((photo, idx) => (
                  <a
                    key={photo.url ?? idx}
                    href={photo.source ?? photo.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="group block overflow-hidden rounded-2xl border border-cream-line"
                  >
                    <img
                      src={photo.url}
                      alt={`${venue.name} fotoğrafı`}
                      loading="lazy"
                      className="aspect-square w-full object-cover transition-transform duration-200 group-hover:scale-105"
                    />
                    {photo.attribution ? (
                      <p className="truncate px-2 py-1.5 text-[10px] text-taupe">
                        {photo.attribution}
                      </p>
                    ) : null}
                  </a>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center gap-2 rounded-2xl border border-dashed border-cream-line py-14 text-center">
                <p className="text-sm text-taupe">Bu mekan için henüz fotoğraf yok.</p>
              </div>
            )}

            {venue.embeds && venue.embeds.length > 0 && (
              <div className="mt-6">
                <p className="mb-3 text-xs font-medium uppercase tracking-wide text-taupe">
                  Videolar
                </p>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  {venue.embeds.map((embed) => (
                    <div
                      key={embed.url}
                      className="overflow-hidden rounded-2xl border border-cream-line bg-sand/30 p-2"
                    >
                      <div className="mb-2 flex items-center justify-between px-1">
                        <span className="inline-flex items-center gap-1 rounded-full bg-espresso px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide text-cream">
                          <Video size={11} />
                          {embed.platform === 'tiktok'
                            ? 'TikTok'
                            : embed.platform === 'instagram'
                              ? 'Instagram'
                              : embed.platform}
                        </span>
                        <a
                          href={embed.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[11px] text-taupe underline"
                        >
                          Orijinal gönderi
                        </a>
                      </div>
                      {embed.platform === 'instagram' ? (
                        <InstagramEmbed html={embed.oembed_html} />
                      ) : (
                        <TikTokEmbed html={embed.oembed_html} />
                      )}
                      {embed.creator ? (
                        <p className="px-1 pb-1 pt-2 text-[10px] text-taupe">@{embed.creator}</p>
                      ) : null}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {venue.photos && venue.photos.length > 0 && (
              <button
                type="button"
                onClick={() => {
                  if (!isLoggedIn) {
                    navigate('/login', loginState)
                    return
                  }
                  setComparePanelOpen(true)
                }}
                aria-label="Fotoğrafını karşılaştır"
                className="fixed bottom-28 right-6 z-30 flex h-14 w-14 items-center justify-center rounded-full bg-tan text-cream shadow-lg transition-transform hover:scale-105"
              >
                <Camera size={22} />
              </button>
            )}

            {comparePanelOpen && (
              <ComparePhotoPanel
                venueName={venue.name}
                loading={compareLoading}
                result={compareResult}
                error={compareError}
                onFileSelected={handleComparePhoto}
                onClose={closeComparePanel}
              />
            )}
          </div>
        )}

        {activeTab === 'Yorumlar' && (
          <div>
            {showForm && (
              <form
                onSubmit={handleSubmit}
                className="mb-5 space-y-3 rounded-2xl border border-cream-line bg-sand/50 p-4"
              >
                <p className="text-xs text-taupe">
                  <span className="font-medium text-espresso">{user?.display_name}</span> olarak
                  yorum yapıyorsun.
                </p>
                <textarea
                  placeholder="Yorumunuz..."
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  rows={3}
                  className="w-full resize-none rounded-lg border border-cream-line bg-cream px-3 py-2 text-sm text-espresso outline-none focus:border-tan"
                  required
                />
                <motion.button
                  type="submit"
                  disabled={submitting}
                  whileTap={shouldReduceMotion ? undefined : { scale: 0.96 }}
                  className="flex w-full items-center justify-center gap-2 rounded-full bg-tan px-4 py-2 text-sm font-medium text-cream disabled:opacity-60"
                >
                  {submitting ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                  Gönder
                </motion.button>
              </form>
            )}

            {contentNotice && <p className="mb-3 text-sm text-tan-dark">{contentNotice}</p>}
            {commentsError && <p className="mb-3 text-sm text-tan-dark">{commentsError}</p>}

            {commentsLoading ? (
              <div className="flex justify-center py-8 text-taupe">
                <Loader2 className="animate-spin" size={18} />
              </div>
            ) : comments.length === 0 ? (
              <p className="py-8 text-center text-sm text-taupe">
                Henüz yorum yok. İlk yorumu sen yaz.
              </p>
            ) : (
              <ul className="space-y-3">
                {comments.map((c) => (
                  <li
                    key={c.id}
                    className="rounded-2xl border border-cream-line bg-sand/40 p-4 grain"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-espresso">{c.author}</span>
                      <span className="text-xs text-taupe">{timeAgo(c.created_at)}</span>
                    </div>
                    <p className="mt-1 text-sm text-espresso-soft">{c.text}</p>
                    {c.review_status === 'pending_review' && (
                      <span className="mt-2 inline-flex items-center gap-1 rounded-full bg-gold/15 px-2.5 py-1 text-xs font-medium text-tan-dark">
                        <ShieldQuestion size={12} />
                        Topluluk incelemesi bekliyor
                      </span>
                    )}
                    {ownFlaggedMessage(c, user?.id) && (
                      <p className="mt-2 text-xs text-tan-dark">{ownFlaggedMessage(c, user?.id)}</p>
                    )}
                    <div className="mt-2 flex flex-wrap items-center gap-3">
                      <HelpfulButton
                        item={c}
                        currentUserId={user?.id}
                        isLoggedIn={isLoggedIn}
                        onNavigateLogin={() => navigate('/login', loginState)}
                        onToggle={() => handleCommentHelpful(c.id)}
                      />
                      <ModerationRow
                        item={c}
                        targetType="comment"
                        placeId={placeId}
                        currentUserId={user?.id}
                        isLoggedIn={isLoggedIn}
                        onBlock={handleBlock}
                      />
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Bottom actions */}
      <div className="fixed bottom-0 left-1/2 flex w-full max-w-[430px] -translate-x-1/2 gap-3 border-t border-cream-line bg-cream px-6 py-4">
        <button
          type="button"
          onClick={openMap}
          className="flex flex-1 items-center justify-center gap-2 rounded-full border border-tan-dark px-4 py-3 text-sm font-medium text-espresso"
        >
          <MapPin size={16} />
          Haritada Gör
        </button>
        <motion.button
          type="button"
          onClick={() => {
            if (!isLoggedIn) {
              navigate('/login', loginState)
              return
            }
            setActiveTab('Yorumlar')
            setShowForm(true)
            setContentNotice(null)
          }}
          whileTap={shouldReduceMotion ? undefined : { scale: 0.96 }}
          className="flex flex-1 items-center justify-center gap-2 rounded-full bg-tan px-4 py-3 text-sm font-medium text-cream"
        >
          Yorum Yap
        </motion.button>
      </div>
    </div>
  )
}

/**
 * Genel Bakış sekmesinde HER mekan için her zaman görünen, gerçek anlık
 * hava durumu kartı (venue.area üzerinden GET /weather/{district} - bkz.
 * yukarıdaki useEffect). Bu, aşağıdaki koşullu açık-hava uyarısının
 * YERİNE geçmiyor: o uyarı sadece açık-hava-duyarlı etiketli bir mekan
 * VE hava elverişsizken görünen, eyleme çağıran özel bir satır; bu kart
 * ise her mekan için nötr/bilgilendirici genel durum. Bilerek
 * birleştirilmedi - birleştirseydik nötr kart, uyarının kendine özgü
 * görsel vurgusunu (CloudRain ikonlu sand kutusu) yutardı ve "sadece bu
 * mekan için önemli" sinyali kaybolurdu.
 *
 * loading = istek sürüyor. !weather (loading bittikten sonra) = Open-
 * Meteo'ya ulaşılamadı - sahte/son-bilinen bir sıcaklık UYDURULMAZ,
 * dürüstçe "hava durumu bilgisi şu an yok" gösterilir (CLAUDE.md "sahte
 * veri yasak", aynı desen Home.jsx'te de kullanılıyor).
 */
function WeatherCard({ weather, loading, failed }) {
  if (loading) {
    return (
      <div className="mb-4 flex items-center gap-2 rounded-2xl border border-cream-line bg-sand/40 px-4 py-3 text-sm text-taupe">
        <Loader2 size={16} className="shrink-0 animate-spin" />
        Hava durumu yükleniyor…
      </div>
    )
  }

  if (!weather) {
    return (
      <div className="mb-4 rounded-2xl border border-cream-line bg-sand/40 px-4 py-3 text-sm text-taupe">
        {failed
          ? 'Hava durumu bilgisi şu an yok.'
          : 'Bu mekan için hava durumu bilgisi yok.'}
      </div>
    )
  }

  const WeatherIcon = WEATHER_ICONS[weather.condition_group] ?? Cloud

  return (
    <div className="mb-4 rounded-2xl border border-cream-line bg-sand/40 px-4 py-3 grain">
      <div className="flex items-center gap-2">
        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-sand text-tan-dark">
          <WeatherIcon size={18} />
        </span>
        <p className="text-sm text-espresso-soft">
          <span className="font-medium text-espresso">{Math.round(weather.temperature)}°C</span>{' '}
          · {weather.district} · {weather.condition}
        </p>
      </div>
      <p className="mt-1.5 text-[10px] text-taupe">Hava durumu verisi: Open-Meteo.com</p>
    </div>
  )
}

function StatCard({ icon, label, value, wide }) {
  return (
    <div
      className={`flex items-center gap-3 rounded-2xl border border-cream-line bg-sand/40 p-4 grain ${
        wide ? 'col-span-2' : ''
      }`}
    >
      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-sand text-tan-dark">
        {icon}
      </span>
      <div className="min-w-0">
        <p className="text-xs text-taupe">{label}</p>
        <p className="truncate text-sm font-medium text-espresso">{value}</p>
      </div>
    </div>
  )
}

/**
 * Renders a TikTok oEmbed blockquote (fetched ahead of time from
 * https://www.tiktok.com/oembed - a public endpoint, no account/API key
 * needed, see database/seed/*.json `embeds[].oembed_html`). TikTok's own
 * `embed.js` scans the page for `.tiktok-embed` blockquotes and replaces
 * them with the real player; it's loaded once and re-invoked via
 * `window.tiktokEmbed.lib.render()` for any embeds mounted afterwards
 * (e.g. switching tabs), matching TikTok's documented embed pattern.
 */
function TikTokEmbed({ html }) {
  useEffect(() => {
    if (!html) return
    const scriptId = 'tiktok-embed-script'
    if (window.tiktokEmbed?.lib?.render) {
      window.tiktokEmbed.lib.render()
      return
    }
    if (document.getElementById(scriptId)) return
    const script = document.createElement('script')
    script.id = scriptId
    script.src = 'https://www.tiktok.com/embed.js'
    script.async = true
    document.body.appendChild(script)
  }, [html])

  if (!html) return null
  return <div dangerouslySetInnerHTML={{ __html: html }} />
}

/**
 * Renders an Instagram oEmbed blockquote (fetched ahead of time from
 * https://graph.facebook.com/v21.0/instagram_oembed - Meta made this public
 * endpoint work without an access token as of June 15, 2026, see
 * database/seed/*.json `embeds[].oembed_html`). Instagram's own
 * `embeds.js` scans the page for `.instagram-media` blockquotes and
 * replaces them with the real player; it's loaded once and re-invoked via
 * `window.instgrm.Embeds.process()` for any embeds mounted afterwards
 * (e.g. switching tabs), matching Instagram's documented embed pattern -
 * same approach as `TikTokEmbed` above, kept consistent on purpose.
 */
function InstagramEmbed({ html }) {
  useEffect(() => {
    if (!html) return
    const scriptId = 'instagram-embed-script'
    if (window.instgrm?.Embeds?.process) {
      window.instgrm.Embeds.process()
      return
    }
    if (document.getElementById(scriptId)) return
    const script = document.createElement('script')
    script.id = scriptId
    script.src = 'https://www.instagram.com/embed.js'
    script.async = true
    document.body.appendChild(script)
  }, [html])

  if (!html) return null
  return <div dangerouslySetInnerHTML={{ __html: html }} />
}

/**
 * "👍 Faydalı (N)" toggle button for a comment or status update (see
 * docs/research/anlik-bilgi-akisi.md "Teşvik Katmanı" - TripAdvisor's
 * "helpful" signal). N is the real helpful_count from the backend, never a
 * guessed number. active = the current user already marked it helpful
 * (item.helpful_user_ids includes their id) - shown filled/highlighted so
 * a second click reads as "undo" rather than "mark again". Hidden entirely
 * for the item's own author (self-marking is refused server-side too, see
 * database/comments_store.toggle_helpful_comment / checkins_store's
 * equivalent - this is just the matching UI-side rule).
 */
function HelpfulButton({ item, currentUserId, isLoggedIn, onNavigateLogin, onToggle }) {
  const [submitting, setSubmitting] = useState(false)
  const isOwnContent = item.author_user_id && item.author_user_id === currentUserId
  if (isOwnContent) return null

  const count = item.helpful_count ?? 0
  const active = Boolean(
    isLoggedIn && currentUserId && (item.helpful_user_ids ?? []).includes(currentUserId),
  )

  async function handleClick() {
    if (!isLoggedIn) {
      onNavigateLogin()
      return
    }
    setSubmitting(true)
    try {
      await onToggle()
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={submitting}
      aria-pressed={active}
      className={`flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium transition-colors disabled:opacity-60 ${
        active ? 'bg-tan text-cream' : 'border border-cream-line text-taupe'
      }`}
    >
      <ThumbsUp size={12} className={active ? 'fill-cream' : ''} />
      Faydalı{count > 0 ? ` (${count})` : ''}
    </button>
  )
}

/**
 * "Şikayet et" / "Engelle" row under a comment or status card. Both are
 * single-click-to-reveal, second-click-to-confirm (never fires on the
 * first tap) - see task requirement: report/block must never happen
 * without an explicit confirm step, but also without a full modal dialog.
 * Hidden entirely for logged-out visitors (reporting/blocking requires a
 * real account) and for a user's own content.
 */
function ModerationRow({ item, targetType, placeId, currentUserId, isLoggedIn, onBlock }) {
  const [reportOpen, setReportOpen] = useState(false)
  const [reason, setReason] = useState('')
  const [reportSubmitting, setReportSubmitting] = useState(false)
  const [reportDone, setReportDone] = useState(false)
  const [reportError, setReportError] = useState(null)

  const [blockConfirming, setBlockConfirming] = useState(false)
  const [blockSubmitting, setBlockSubmitting] = useState(false)

  if (!isLoggedIn) return null
  const isOwnContent = item.author_user_id && item.author_user_id === currentUserId
  if (isOwnContent) return null

  async function handleReportSubmit() {
    if (!reason.trim()) return
    setReportSubmitting(true)
    setReportError(null)
    try {
      await reportContent({
        targetType,
        targetId: item.id,
        placeId,
        reason: reason.trim(),
      })
      setReportDone(true)
      setReportOpen(false)
    } catch {
      setReportError('Şikayet gönderilemedi.')
    } finally {
      setReportSubmitting(false)
    }
  }

  async function handleBlockConfirm() {
    if (!item.author_user_id) return
    setBlockSubmitting(true)
    try {
      await onBlock(item.author_user_id)
    } finally {
      setBlockSubmitting(false)
      setBlockConfirming(false)
    }
  }

  return (
    <div className="flex flex-wrap items-center gap-3 text-xs">
      {reportDone ? (
        <span className="text-taupe">Şikayet edildi, teşekkürler.</span>
      ) : reportOpen ? (
        <div className="flex w-full flex-col gap-2 rounded-xl border border-cream-line bg-cream p-3">
          <input
            type="text"
            autoFocus
            placeholder="Şikayet nedeni (kısaca)"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className="w-full rounded-lg border border-cream-line bg-cream px-2.5 py-1.5 text-xs text-espresso outline-none focus:border-tan"
          />
          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleReportSubmit}
              disabled={!reason.trim() || reportSubmitting}
              className="rounded-full bg-tan px-3 py-1.5 font-medium text-cream disabled:opacity-60"
            >
              {reportSubmitting ? 'Gönderiliyor…' : 'Şikayeti gönder'}
            </button>
            <button
              type="button"
              onClick={() => {
                setReportOpen(false)
                setReason('')
              }}
              className="text-taupe"
            >
              Vazgeç
            </button>
          </div>
        </div>
      ) : (
        <button
          type="button"
          onClick={() => setReportOpen(true)}
          className="flex items-center gap-1 text-taupe"
        >
          <Flag size={12} />
          Şikayet et
        </button>
      )}

      {reportError && <span className="text-tan-dark">{reportError}</span>}

      {item.author_user_id && (
        <>
          {blockConfirming ? (
            <span className="flex items-center gap-2">
              <span className="text-taupe">Bu kişiyi engelle, emin misin?</span>
              <button
                type="button"
                onClick={handleBlockConfirm}
                disabled={blockSubmitting}
                className="font-medium text-tan-dark"
              >
                {blockSubmitting ? '…' : 'Evet'}
              </button>
              <button type="button" onClick={() => setBlockConfirming(false)} className="text-taupe">
                Vazgeç
              </button>
            </span>
          ) : (
            <button
              type="button"
              onClick={() => setBlockConfirming(true)}
              className="flex items-center gap-1 text-taupe"
            >
              <UserX size={12} />
              Engelle
            </button>
          )}
        </>
      )}
    </div>
  )
}

const VERDICT_LABELS = {
  muhtemelen_ayni_yer: 'Muhtemelen aynı yer',
  belirsiz: 'Belirsiz',
  farkli_gorunuyor: 'Farklı görünüyor',
}

/**
 * Bottom-sheet panel for the real photo-comparison feature: lets the user
 * take/upload a photo, uploads it to POST /places/{id}/compare-photo, and
 * shows the REAL similarity_percent computed there via perceptual hashing
 * (database/photo_compare.py) - never a made-up number. Loading and error
 * states (no reference photo, backend/network failure) are shown honestly,
 * matching this screen's other async flows (comments/status).
 *
 * Privacy: the chosen File is handed straight to comparePhoto() (a
 * fetch/FormData upload) - it's never written anywhere by this component,
 * only held in the browser's own file picker state until the request
 * completes, same as any other file input.
 */
function ComparePhotoPanel({ venueName, loading, result, error, onFileSelected, onClose }) {
  const [previewName, setPreviewName] = useState(null)

  function handleChange(e) {
    const file = e.target.files?.[0]
    if (!file) return
    setPreviewName(file.name)
    onFileSelected(file)
  }

  return (
    <div className="fixed inset-0 z-40 flex items-end justify-center bg-espresso/50 backdrop-blur-sm">
      <div className="w-full max-w-[430px] rounded-t-3xl border-t border-cream-line bg-cream p-6 pb-8 grain">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-lg font-medium text-espresso">Fotoğraf Karşılaştır</h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Kapat"
            className="flex h-8 w-8 items-center justify-center rounded-full bg-sand text-espresso"
          >
            <X size={16} />
          </button>
        </div>

        <p className="mt-2 text-sm text-taupe">
          Çektiğin fotoğrafı {venueName}'in referans fotoğrafıyla karşılaştıralım - gerçekten
          hesaplanmış bir görsel benzerlik ölçümü (perceptual hash), tahmin değil.
        </p>

        <div className="mt-5">
          {loading ? (
            <div className="flex flex-col items-center gap-2 py-8 text-taupe">
              <Loader2 className="animate-spin" size={22} />
              <p className="text-sm">Karşılaştırılıyor…</p>
            </div>
          ) : result ? (
            <div className="space-y-3 rounded-2xl border border-cream-line bg-sand/50 p-4">
              <div className="flex items-baseline justify-between">
                <span className="text-sm text-taupe">Benzerlik</span>
                <span className="font-display text-3xl font-medium text-espresso">
                  %{result.similarity_percent}
                </span>
              </div>
              <p
                className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium ${
                  result.verdict === 'muhtemelen_ayni_yer'
                    ? 'bg-tan/15 text-tan-dark'
                    : result.verdict === 'belirsiz'
                      ? 'bg-gold/15 text-tan-dark'
                      : 'bg-sand-dark text-espresso-soft'
                }`}
              >
                {VERDICT_LABELS[result.verdict] ?? result.verdict}
              </p>
              <p className="text-xs text-taupe">
                Hamming mesafesi: {result.hamming_distance} bit (64 bit üzerinden) - perceptual
                hash (pHash) ile hesaplandı.
              </p>
              <label className="block">
                <span className="flex w-full cursor-pointer items-center justify-center gap-2 rounded-full border border-tan-dark px-4 py-2.5 text-sm font-medium text-espresso">
                  <Camera size={16} />
                  Tekrar dene
                </span>
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  capture="environment"
                  onChange={handleChange}
                  className="hidden"
                />
              </label>
            </div>
          ) : error ? (
            <div className="space-y-3 rounded-2xl border border-cream-line bg-sand/50 p-4">
              <p className="flex items-start gap-2 text-sm text-espresso-soft">
                <AlertTriangle size={16} className="mt-0.5 shrink-0 text-tan-dark" />
                {error}
              </p>
              <label className="block">
                <span className="flex w-full cursor-pointer items-center justify-center gap-2 rounded-full bg-tan px-4 py-2.5 text-sm font-medium text-cream">
                  <Camera size={16} />
                  Tekrar dene
                </span>
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  capture="environment"
                  onChange={handleChange}
                  className="hidden"
                />
              </label>
            </div>
          ) : (
            <label className="block">
              <span className="flex w-full cursor-pointer items-center justify-center gap-2 rounded-full bg-tan px-4 py-3 text-sm font-medium text-cream">
                <Camera size={18} />
                Fotoğraf çek / yükle
              </span>
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                capture="environment"
                onChange={handleChange}
                className="hidden"
              />
              {previewName && (
                <p className="mt-2 text-center text-xs text-taupe">{previewName}</p>
              )}
            </label>
          )}
        </div>
      </div>
    </div>
  )
}
