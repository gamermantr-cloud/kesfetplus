import {
  Bell,
  ChevronLeft,
  Loader2,
  MapPin,
  Navigation,
  Send,
  ShieldQuestion,
  Sparkles,
  Star,
  Users,
  Wallet,
} from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  getCheckinCount,
  getComments,
  getStatusUpdates,
  postCheckin,
  postComment,
  postStatusUpdate,
} from '../lib/api.js'
import { getAllVenues } from '../lib/data.js'

const TABS = ['Genel Bakış', 'Anlık Durum', 'Fotoğraflar', 'Yorumlar']
const STATUS_TAGS = ['Kalabalık', 'Orta', 'Sakin']
const DISPLAY_NAME_KEY = 'kesfetplus_display_name'

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

  const [venue, setVenue] = useState(undefined) // undefined = loading, null = not found
  const [activeTab, setActiveTab] = useState(TABS[0])

  const [comments, setComments] = useState([])
  const [commentsLoading, setCommentsLoading] = useState(true)
  const [commentsError, setCommentsError] = useState(null)

  const [showForm, setShowForm] = useState(false)
  const [author, setAuthor] = useState('')
  const [text, setText] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const [displayName, setDisplayName] = useState(() => {
    try {
      return localStorage.getItem(DISPLAY_NAME_KEY) || ''
    } catch {
      return ''
    }
  })
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

  useEffect(() => {
    try {
      if (displayName.trim()) localStorage.setItem(DISPLAY_NAME_KEY, displayName.trim())
    } catch {
      // localStorage unavailable (private mode etc.) - not critical, skip silently
    }
  }, [displayName])

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

  const loadComments = useMemo(
    () => async () => {
      setCommentsLoading(true)
      setCommentsError(null)
      try {
        const data = await getComments(placeId)
        setComments(data)
      } catch {
        setCommentsError('Yorumlar yüklenemedi. Backend çalışıyor mu kontrol edin.')
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
      } catch {
        setStatusError('Anlık durumlar yüklenemedi. Backend çalışıyor mu kontrol edin.')
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

  async function handleCheckin() {
    const name = displayName.trim()
    if (!name) return
    setCheckinLoading(true)
    setCheckinNote(null)
    setStatusError(null)

    const submit = async (lat, lng, accuracy, note) => {
      try {
        await postCheckin(placeId, { author: name, lat, lng, accuracy })
        setCheckedIn(true)
        setCheckinNote(note)
        await Promise.all([loadStatus(), loadCheckinCount()])
      } catch {
        setStatusError('Check-in gönderilemedi. Backend çalışıyor mu kontrol edin.')
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
    const name = displayName.trim()
    if (!name || !selectedTag) return
    setStatusSubmitting(true)
    setStatusError(null)
    try {
      await postStatusUpdate(placeId, { author: name, tag: selectedTag, text: statusText.trim() })
      setSelectedTag(null)
      setStatusText('')
      await loadStatus()
    } catch {
      setStatusError('Durum paylaşılamadı. Backend çalışıyor mu kontrol edin.')
    } finally {
      setStatusSubmitting(false)
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
    if (!author.trim() || !text.trim()) return
    setSubmitting(true)
    try {
      const { lat, lng, accuracy } = await getCommentLocation()
      await postComment(placeId, { author: author.trim(), text: text.trim(), lat, lng, accuracy })
      setAuthor('')
      setText('')
      setShowForm(false)
      await loadComments()
    } catch {
      setCommentsError('Yorum gönderilemedi. Backend çalışıyor mu kontrol edin.')
    } finally {
      setSubmitting(false)
    }
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
        <div className="absolute inset-0 bg-gradient-to-br from-tan via-tan-dark to-espresso" />
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
        {activeTab === 'Genel Bakış' && (
          <div>
            <div className="grid grid-cols-2 gap-3">
              <StatCard
                icon={<Users size={18} />}
                label="Yoğunluk"
                value={crowdLabel(venue)}
              />
              <StatCard icon={<Sparkles size={18} />} label="Temizlik" value="Veri yok" />
              <StatCard icon={<Bell size={18} />} label="Hizmet" value="Veri yok" />
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

            {!displayName.trim() && (
              <input
                type="text"
                placeholder="İsmin (paylaşımlarda görünür)"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                className="w-full rounded-lg border border-cream-line bg-cream px-3 py-2 text-sm text-espresso outline-none focus:border-tan"
              />
            )}

            {!checkedIn ? (
              <button
                type="button"
                onClick={handleCheckin}
                disabled={!displayName.trim() || checkinLoading}
                className="flex w-full items-center justify-center gap-2 rounded-full bg-tan px-4 py-3 text-sm font-medium text-cream disabled:opacity-60"
              >
                {checkinLoading ? (
                  <Loader2 size={16} className="animate-spin" />
                ) : (
                  <Navigation size={16} />
                )}
                Buradayım
              </button>
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
                <button
                  type="button"
                  onClick={handleStatusSubmit}
                  disabled={!selectedTag || statusSubmitting}
                  className="flex w-full items-center justify-center gap-2 rounded-full bg-tan px-4 py-2 text-sm font-medium text-cream disabled:opacity-60"
                >
                  {statusSubmitting ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                  Paylaş
                </button>
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
                        className={`rounded-2xl border border-cream-line bg-sand/40 p-3 ${
                          s.is_stale ? 'opacity-50' : ''
                        }`}
                      >
                        <p className="text-sm text-espresso-soft">
                          <span className="text-taupe">{timeAgo(s.created_at)}, </span>
                          <span className="font-medium text-espresso">{s.author}</span>
                          <span className="text-taupe"> paylaştı: </span>
                          <span className="font-medium text-espresso">{s.tag}</span>
                          {s.text ? ` — ${s.text}` : ''}
                        </p>
                        {s.is_stale && <p className="mt-0.5 text-xs text-taupe">Eski bilgi</p>}
                      </li>
                    ))}
                </ul>
              )}
            </div>
          </div>
        )}

        {activeTab === 'Fotoğraflar' && (
          <div className="flex flex-col items-center justify-center gap-2 rounded-2xl border border-dashed border-cream-line py-14 text-center">
            <p className="text-sm text-taupe">Henüz fotoğraf eklenmedi.</p>
          </div>
        )}

        {activeTab === 'Yorumlar' && (
          <div>
            {showForm && (
              <form
                onSubmit={handleSubmit}
                className="mb-5 space-y-3 rounded-2xl border border-cream-line bg-sand/50 p-4"
              >
                <input
                  type="text"
                  placeholder="İsminiz"
                  value={author}
                  onChange={(e) => setAuthor(e.target.value)}
                  className="w-full rounded-lg border border-cream-line bg-cream px-3 py-2 text-sm text-espresso outline-none focus:border-tan"
                  required
                />
                <textarea
                  placeholder="Yorumunuz..."
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  rows={3}
                  className="w-full resize-none rounded-lg border border-cream-line bg-cream px-3 py-2 text-sm text-espresso outline-none focus:border-tan"
                  required
                />
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex w-full items-center justify-center gap-2 rounded-full bg-tan px-4 py-2 text-sm font-medium text-cream disabled:opacity-60"
                >
                  {submitting ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                  Gönder
                </button>
              </form>
            )}

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
                    className="rounded-2xl border border-cream-line bg-sand/40 p-4"
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
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
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
        <button
          type="button"
          onClick={() => {
            setActiveTab('Yorumlar')
            setShowForm(true)
          }}
          className="flex flex-1 items-center justify-center gap-2 rounded-full bg-tan px-4 py-3 text-sm font-medium text-cream"
        >
          Yorum Yap
        </button>
      </div>
    </div>
  )
}

function StatCard({ icon, label, value, wide }) {
  return (
    <div
      className={`flex items-center gap-3 rounded-2xl border border-cream-line bg-sand/40 p-4 ${
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
