import {
  Bell,
  ChevronLeft,
  Loader2,
  MapPin,
  Send,
  Sparkles,
  Star,
  Users,
  Wallet,
} from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { getComments, postComment } from '../lib/api.js'
import { getAllVenues } from '../lib/data.js'

const TABS = ['Genel Bakış', 'Anlık Durum', 'Fotoğraflar', 'Yorumlar']

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

  async function handleSubmit(e) {
    e.preventDefault()
    if (!author.trim() || !text.trim()) return
    setSubmitting(true)
    try {
      await postComment(placeId, { author: author.trim(), text: text.trim() })
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
    window.open(`https://www.google.com/maps/search/?api=1&query=${query}`, '_blank')
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
          <div className="space-y-3">
            <StatCard
              icon={<Users size={18} />}
              label="Şu anki yoğunluk"
              value={crowdLabel(venue)}
              wide
            />
            <p className="text-sm text-taupe">
              Anlık bilgi akışı, orada bulunan kullanıcıların paylaşımlarıyla zamanla
              zenginleşecek. Şu an için elimizdeki tek anlık sinyal bu.
            </p>
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
