import { BarChart3, ChevronLeft, Eye, EyeOff, Flag, RotateCcw, ShieldCheck } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  getHiddenContent,
  getModerationReports,
  getModerationStats,
  getUserProfile,
  resolveReport,
  restoreContent,
} from '../lib/api.js'
import { useAuth } from '../lib/AuthContext.jsx'

const TABS = ['Şikayetler', 'Gizli İçerik', 'İstatistikler']

const STAT_CARDS = [
  { key: 'total_users', label: 'Toplam Kullanıcı' },
  { key: 'total_comments', label: 'Toplam Yorum' },
  { key: 'total_checkins', label: 'Toplam Check-in' },
  { key: 'total_status_updates', label: 'Toplam Durum Güncellemesi' },
  { key: 'hidden_comments_count', label: 'Gizli Yorum' },
  { key: 'hidden_status_count', label: 'Gizli Durum Güncellemesi' },
  { key: 'open_reports_count', label: 'Açık Şikayet' },
  { key: 'resolved_reports_count', label: 'İncelenen Şikayet' },
  { key: 'venues_with_activity', label: 'Aktivite Olan Mekan' },
]

const TARGET_TYPE_LABELS = {
  comment: 'Yorum',
  status: 'Durum',
  checkin: 'Check-in',
}

function formatDate(isoString) {
  try {
    return new Date(isoString).toLocaleString('tr-TR')
  } catch {
    return isoString
  }
}

export default function Moderation() {
  const navigate = useNavigate()
  const { user, loading: authLoading, isLoggedIn } = useAuth()
  const [activeTab, setActiveTab] = useState(TABS[0])
  const [toast, setToast] = useState(null)
  const toastTimer = useRef(null)

  const [reports, setReports] = useState([])
  const [reportsLoading, setReportsLoading] = useState(true)
  const [reportsError, setReportsError] = useState(null)
  const [reporterNames, setReporterNames] = useState({})

  const [hiddenContent, setHiddenContent] = useState({ comments: [], status_updates: [] })
  const [hiddenLoading, setHiddenLoading] = useState(true)
  const [hiddenError, setHiddenError] = useState(null)
  const [restoreConfirmKey, setRestoreConfirmKey] = useState(null)

  const [stats, setStats] = useState(null)
  const [statsLoading, setStatsLoading] = useState(true)
  const [statsError, setStatsError] = useState(null)

  const isModerator = Boolean(user?.is_moderator)

  function showToast(message) {
    setToast(message)
    clearTimeout(toastTimer.current)
    toastTimer.current = setTimeout(() => setToast(null), 1800)
  }

  useEffect(() => {
    if (!isModerator) return
    let cancelled = false

    setReportsLoading(true)
    getModerationReports()
      .then((data) => {
        if (cancelled) return
        setReports(data)
        setReportsError(null)
        const uniqueReporterIds = [...new Set(data.map((r) => r.reporter_user_id))]
        Promise.all(
          uniqueReporterIds.map((id) =>
            getUserProfile(id)
              .then((p) => [id, p.display_name])
              .catch(() => [id, '(silinmiş hesap)']),
          ),
        ).then((pairs) => {
          if (!cancelled) setReporterNames(Object.fromEntries(pairs))
        })
      })
      .catch((err) => {
        if (!cancelled) setReportsError(err.message || 'Şikayetler yüklenemedi.')
      })
      .finally(() => {
        if (!cancelled) setReportsLoading(false)
      })

    setHiddenLoading(true)
    getHiddenContent()
      .then((data) => {
        if (!cancelled) {
          setHiddenContent(data)
          setHiddenError(null)
        }
      })
      .catch((err) => {
        if (!cancelled) setHiddenError(err.message || 'Gizli içerik yüklenemedi.')
      })
      .finally(() => {
        if (!cancelled) setHiddenLoading(false)
      })

    setStatsLoading(true)
    getModerationStats()
      .then((data) => {
        if (!cancelled) {
          setStats(data)
          setStatsError(null)
        }
      })
      .catch((err) => {
        if (!cancelled) setStatsError(err.message || 'İstatistikler yüklenemedi.')
      })
      .finally(() => {
        if (!cancelled) setStatsLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [isModerator])

  async function handleResolve(reportId) {
    try {
      await resolveReport(reportId)
      setReports((prev) => prev.map((r) => (r.id === reportId ? { ...r, status: 'resolved' } : r)))
      showToast('Şikayet incelendi olarak işaretlendi')
    } catch (err) {
      showToast(err.message || 'İşlem başarısız oldu')
    }
  }

  async function handleRestore(contentType, contentId) {
    try {
      await restoreContent(contentType, contentId)
      if (contentType === 'comment') {
        setHiddenContent((prev) => ({
          ...prev,
          comments: prev.comments.filter((c) => c.id !== contentId),
        }))
      } else {
        setHiddenContent((prev) => ({
          ...prev,
          status_updates: prev.status_updates.filter((s) => s.id !== contentId),
        }))
      }
      setRestoreConfirmKey(null)
      showToast('İçerik geri getirildi')
    } catch (err) {
      showToast(err.message || 'İşlem başarısız oldu')
    }
  }

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-cream">
        <p className="text-sm text-taupe">Yükleniyor…</p>
      </div>
    )
  }

  if (!isLoggedIn || !isModerator) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-cream px-6 text-center">
        <ShieldCheck size={32} className="text-taupe" />
        <p className="font-display text-lg text-espresso">Bu sayfaya erişimin yok</p>
        <p className="text-sm text-taupe">Moderasyon paneli sadece moderatörlere açık.</p>
        <button
          type="button"
          onClick={() => navigate('/profile')}
          className="mt-2 rounded-full bg-tan px-4 py-2 text-xs font-medium text-cream"
        >
          Profile Dön
        </button>
      </div>
    )
  }

  const openReports = reports.filter((r) => r.status === 'open')
  const resolvedReports = reports.filter((r) => r.status !== 'open')

  return (
    <div className="relative min-h-screen bg-cream pb-10">
      <header className="flex items-center px-5 pt-6">
        <button
          type="button"
          aria-label="Geri"
          onClick={() => navigate(-1)}
          className="flex h-9 w-9 items-center justify-center rounded-full bg-sand text-espresso-soft"
        >
          <ChevronLeft size={20} />
        </button>
        <h1 className="ml-3 font-display text-xl text-espresso">Moderasyon Paneli</h1>
      </header>

      {/* Tabs */}
      <div className="mt-6 flex border-b border-cream-line px-5">
        {TABS.map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className={`flex-1 border-b-2 px-2 py-3 text-xs font-medium transition-colors ${
              activeTab === tab ? 'border-tan text-espresso' : 'border-transparent text-taupe'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="px-5 py-5">
        {activeTab === 'Şikayetler' && (
          <div className="space-y-5">
            {reportsLoading ? (
              <p className="text-sm text-taupe">Yükleniyor…</p>
            ) : reportsError ? (
              <p className="text-sm text-tan-dark">{reportsError}</p>
            ) : reports.length === 0 ? (
              <p className="text-sm text-taupe">Hiç şikayet yok.</p>
            ) : (
              <>
                <div>
                  <p className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-taupe">
                    <Flag size={14} />
                    Açık ({openReports.length})
                  </p>
                  <div className="space-y-3">
                    {openReports.length === 0 ? (
                      <p className="text-sm text-taupe">Açık şikayet yok.</p>
                    ) : (
                      openReports.map((report) => (
                        <div
                          key={report.id}
                          className="rounded-2xl border border-cream-line bg-sand/40 px-4 py-4"
                        >
                          <p className="text-sm text-espresso">
                            <span className="font-medium">
                              {reporterNames[report.reporter_user_id] ?? '…'}
                            </span>{' '}
                            şu içeriği şikayet etti:{' '}
                            <span className="font-medium">
                              {TARGET_TYPE_LABELS[report.target_type] ?? report.target_type}
                            </span>{' '}
                            (mekan: {report.place_id})
                          </p>
                          <p className="mt-1 text-sm text-espresso-soft">
                            Sebep: {report.reason}
                          </p>
                          <p className="mt-1 text-[11px] text-taupe">
                            {formatDate(report.created_at)}
                          </p>
                          <button
                            type="button"
                            onClick={() => handleResolve(report.id)}
                            className="mt-3 flex items-center gap-2 rounded-full bg-tan px-3 py-1.5 text-xs font-medium text-cream"
                          >
                            <ShieldCheck size={14} />
                            İncelendi
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                {resolvedReports.length > 0 && (
                  <div>
                    <p className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-taupe">
                      <ShieldCheck size={14} />
                      İncelendi ({resolvedReports.length})
                    </p>
                    <div className="space-y-3">
                      {resolvedReports.map((report) => (
                        <div
                          key={report.id}
                          className="rounded-2xl border border-cream-line bg-sand/20 px-4 py-4 opacity-70"
                        >
                          <p className="text-sm text-espresso">
                            <span className="font-medium">
                              {reporterNames[report.reporter_user_id] ?? '…'}
                            </span>{' '}
                            —{' '}
                            {TARGET_TYPE_LABELS[report.target_type] ?? report.target_type} (mekan:{' '}
                            {report.place_id})
                          </p>
                          <p className="mt-1 text-sm text-espresso-soft">
                            Sebep: {report.reason}
                          </p>
                          <p className="mt-1 text-[11px] text-taupe">
                            {formatDate(report.created_at)}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {activeTab === 'Gizli İçerik' && (
          <div className="space-y-5">
            {hiddenLoading ? (
              <p className="text-sm text-taupe">Yükleniyor…</p>
            ) : hiddenError ? (
              <p className="text-sm text-tan-dark">{hiddenError}</p>
            ) : hiddenContent.comments.length === 0 &&
              hiddenContent.status_updates.length === 0 ? (
              <p className="text-sm text-taupe">Gizli içerik yok.</p>
            ) : (
              <>
                <div>
                  <p className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-taupe">
                    <EyeOff size={14} />
                    Gizli Yorumlar ({hiddenContent.comments.length})
                  </p>
                  <div className="space-y-3">
                    {hiddenContent.comments.map((comment) => {
                      const key = `comment:${comment.id}`
                      return (
                        <div
                          key={comment.id}
                          className="rounded-2xl border border-cream-line bg-sand/40 px-4 py-4"
                        >
                          <p className="text-sm font-medium text-espresso">{comment.author}</p>
                          <p className="mt-1 text-sm text-espresso-soft">{comment.text}</p>
                          <p className="mt-1 text-[11px] text-taupe">
                            mekan: {comment.place_id} · sebep:{' '}
                            {comment.flagged_reason ?? 'belirtilmemiş'} ·{' '}
                            {formatDate(comment.created_at)}
                          </p>
                          {restoreConfirmKey === key ? (
                            <div className="mt-3 flex items-center gap-2">
                              <button
                                type="button"
                                onClick={() => handleRestore('comment', comment.id)}
                                className="rounded-full bg-tan px-3 py-1.5 text-xs font-medium text-cream"
                              >
                                Emin misin?
                              </button>
                              <button
                                type="button"
                                onClick={() => setRestoreConfirmKey(null)}
                                className="text-xs text-taupe"
                              >
                                Vazgeç
                              </button>
                            </div>
                          ) : (
                            <button
                              type="button"
                              onClick={() => setRestoreConfirmKey(key)}
                              className="mt-3 flex items-center gap-2 rounded-full border border-tan-dark px-3 py-1.5 text-xs font-medium text-espresso"
                            >
                              <RotateCcw size={14} />
                              Geri Getir
                            </button>
                          )}
                        </div>
                      )
                    })}
                  </div>
                </div>

                <div>
                  <p className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-taupe">
                    <Eye size={14} />
                    Gizli Durum Güncellemeleri ({hiddenContent.status_updates.length})
                  </p>
                  <div className="space-y-3">
                    {hiddenContent.status_updates.map((status) => {
                      const key = `status:${status.id}`
                      return (
                        <div
                          key={status.id}
                          className="rounded-2xl border border-cream-line bg-sand/40 px-4 py-4"
                        >
                          <p className="text-sm font-medium text-espresso">
                            {status.author} · {status.tag}
                          </p>
                          {status.text && (
                            <p className="mt-1 text-sm text-espresso-soft">{status.text}</p>
                          )}
                          <p className="mt-1 text-[11px] text-taupe">
                            mekan: {status.place_id} · sebep:{' '}
                            {status.flagged_reason ?? 'belirtilmemiş'} ·{' '}
                            {formatDate(status.created_at)}
                          </p>
                          {restoreConfirmKey === key ? (
                            <div className="mt-3 flex items-center gap-2">
                              <button
                                type="button"
                                onClick={() => handleRestore('status', status.id)}
                                className="rounded-full bg-tan px-3 py-1.5 text-xs font-medium text-cream"
                              >
                                Emin misin?
                              </button>
                              <button
                                type="button"
                                onClick={() => setRestoreConfirmKey(null)}
                                className="text-xs text-taupe"
                              >
                                Vazgeç
                              </button>
                            </div>
                          ) : (
                            <button
                              type="button"
                              onClick={() => setRestoreConfirmKey(key)}
                              className="mt-3 flex items-center gap-2 rounded-full border border-tan-dark px-3 py-1.5 text-xs font-medium text-espresso"
                            >
                              <RotateCcw size={14} />
                              Geri Getir
                            </button>
                          )}
                        </div>
                      )
                    })}
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {activeTab === 'İstatistikler' && (
          <div>
            {statsLoading ? (
              <p className="text-sm text-taupe">Yükleniyor…</p>
            ) : statsError ? (
              <p className="text-sm text-tan-dark">{statsError}</p>
            ) : (
              <div className="grid grid-cols-2 gap-3">
                {STAT_CARDS.map(({ key, label }) => (
                  <div
                    key={key}
                    className="rounded-2xl border border-cream-line bg-sand/40 px-4 py-4"
                  >
                    <p className="flex items-center gap-1.5 text-[11px] font-medium uppercase tracking-wide text-taupe">
                      <BarChart3 size={12} />
                      {label}
                    </p>
                    <p className="mt-1 font-display text-2xl text-espresso">{stats[key]}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {toast && (
        <div className="fixed bottom-8 inset-x-0 z-10 mx-auto w-fit max-w-[430px] rounded-full bg-espresso px-4 py-2 text-xs font-medium text-cream shadow-lg">
          {toast}
        </div>
      )}
    </div>
  )
}
