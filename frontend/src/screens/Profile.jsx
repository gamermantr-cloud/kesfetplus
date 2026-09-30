import {
  Award,
  Bell,
  BellOff,
  Bookmark,
  Check,
  ChevronLeft,
  ChevronRight,
  Copy,
  HelpCircle,
  LogIn,
  LogOut,
  MessageSquare,
  Settings,
  ShieldCheck,
  ShieldX,
  Telescope,
  User,
  UserPlus,
  UserX,
} from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Toast from '../components/Toast.jsx'
import { useAuth } from '../lib/AuthContext.jsx'
import { getUserProfile, getUserStats } from '../lib/api.js'
import { disablePushNotifications, enablePushNotifications, getPermissionState, isPushSupported } from '../lib/push.js'

const MENU_ITEMS = [
  { id: 'saved', label: 'Kaydettiklerim', icon: Bookmark },
  { id: 'comments', label: 'Yorumlarım', icon: MessageSquare },
  { id: 'settings', label: 'Ayarlar', icon: Settings },
  { id: 'help', label: 'Destek', icon: HelpCircle, to: '/support' },
]

export default function Profile() {
  const navigate = useNavigate()
  const { user, loading, isLoggedIn, logout, unblock } = useAuth()
  const [toast, setToast] = useState(null)
  const toastTimer = useRef(null)

  const [blockedProfiles, setBlockedProfiles] = useState([])
  const [blockedLoading, setBlockedLoading] = useState(false)
  const [unblockConfirmId, setUnblockConfirmId] = useState(null)

  const [pushPermission, setPushPermission] = useState(() => getPermissionState())
  const [pushBusy, setPushBusy] = useState(false)

  const [referralLinkCopied, setReferralLinkCopied] = useState(false)

  // Real, on-demand computed stats for the "Teşvik Katmanı" (Gözcü rozeti) -
  // see docs/research/anlik-bilgi-akisi.md and GET /users/{id}/stats.
  // stats === null while loading/not-yet-fetched; never a guessed number.
  const [stats, setStats] = useState(null)
  const [statsError, setStatsError] = useState(false)

  useEffect(() => {
    let cancelled = false
    if (!isLoggedIn || !user?.id) {
      setStats(null)
      return undefined
    }
    setStatsError(false)
    getUserStats(user.id)
      .then((data) => {
        if (!cancelled) setStats(data)
      })
      .catch(() => {
        if (!cancelled) setStatsError(true)
      })
    return () => {
      cancelled = true
    }
  }, [isLoggedIn, user?.id])

  useEffect(() => {
    let cancelled = false
    const blockedIds = user?.blocked_user_ids ?? []
    if (blockedIds.length === 0) {
      setBlockedProfiles([])
      return
    }
    setBlockedLoading(true)
    Promise.all(
      blockedIds.map((id) =>
        getUserProfile(id).catch(() => ({ id, display_name: '(silinmiş hesap)' })),
      ),
    ).then((profiles) => {
      if (!cancelled) setBlockedProfiles(profiles)
    }).finally(() => {
      if (!cancelled) setBlockedLoading(false)
    })
    return () => {
      cancelled = true
    }
  }, [user?.blocked_user_ids])

  function showToast(message) {
    setToast(message)
    clearTimeout(toastTimer.current)
    toastTimer.current = setTimeout(() => setToast(null), 1800)
  }

  function showComingSoon(label) {
    showToast(`${label} yakında geliyor`)
  }

  async function handleUnblock(userId) {
    try {
      await unblock(userId)
      setUnblockConfirmId(null)
      showToast('Engel kaldırıldı')
    } catch {
      showToast('Engel kaldırılamadı')
    }
  }

  async function handleLogout() {
    await logout()
    showToast('Çıkış yapıldı')
    navigate('/home')
  }

  async function handleCopyReferralLink() {
    if (!user?.referral_code) return
    // Real origin the app is actually served from - never a hardcoded/guessed
    // domain (see docs/research/buyume-ilk-100-kullanici-stratejisi.md 2.4).
    const link = `${window.location.origin}/register?ref=${encodeURIComponent(user.referral_code)}`
    try {
      await navigator.clipboard.writeText(link)
      setReferralLinkCopied(true)
      showToast('Davet linki kopyalandı')
      setTimeout(() => setReferralLinkCopied(false), 1800)
    } catch {
      showToast('Kopyalanamadı')
    }
  }

  async function handleEnablePush() {
    setPushBusy(true)
    try {
      await enablePushNotifications()
      setPushPermission(getPermissionState())
      showToast('Bildirimler açıldı')
    } catch (err) {
      showToast(err?.message ?? 'Bildirimler açılamadı')
    } finally {
      setPushBusy(false)
    }
  }

  async function handleDisablePush() {
    setPushBusy(true)
    try {
      await disablePushNotifications()
      showToast('Bildirimler kapatıldı')
    } catch {
      showToast('Bildirimler kapatılamadı')
    } finally {
      setPushBusy(false)
    }
  }

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
        <h1 className="ml-3 font-display text-xl text-espresso">Profil</h1>
      </header>

      <div className="mt-8 flex flex-col items-center px-6">
        <div className="flex h-24 w-24 items-center justify-center rounded-full bg-sand-dark text-espresso-soft">
          <User size={40} />
        </div>
        {loading ? (
          <p className="mt-4 text-sm text-taupe">Yükleniyor…</p>
        ) : isLoggedIn ? (
          <>
            <p className="mt-4 font-display text-lg text-espresso">{user.display_name}</p>
            <p className="mt-1 text-xs text-taupe">{user.email}</p>
            {user.is_founding_member && (
              <span className="mt-2 flex items-center gap-1.5 rounded-full bg-gold/15 px-3 py-1 text-xs font-medium text-tan-dark">
                <Award size={13} />
                {user.member_number}. Kurucu Üye
              </span>
            )}
            <button
              type="button"
              onClick={handleLogout}
              className="mt-4 flex items-center gap-2 rounded-full border border-tan-dark px-4 py-2 text-xs font-medium text-espresso"
            >
              <LogOut size={14} />
              Çıkış Yap
            </button>
          </>
        ) : (
          <>
            <p className="mt-4 font-display text-lg text-espresso">Misafir Kullanıcı</p>
            <p className="mt-1 text-xs text-taupe">
              Yorum yapmak ve durum paylaşmak için giriş yapmalısın
            </p>
            <button
              type="button"
              onClick={() => navigate('/login')}
              className="mt-4 flex items-center gap-2 rounded-full bg-tan px-4 py-2 text-xs font-medium text-cream"
            >
              <LogIn size={14} />
              Giriş Yap
            </button>
          </>
        )}
      </div>

      <div className="mt-8 px-5">
        <div className="overflow-hidden rounded-2xl border border-cream-line bg-sand/40">
          {MENU_ITEMS.map((item, i) => {
            const Icon = item.icon
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => (item.to ? navigate(item.to) : showComingSoon(item.label))}
                className={`flex w-full items-center gap-3 px-4 py-4 text-left ${
                  i !== MENU_ITEMS.length - 1 ? 'border-b border-cream-line' : ''
                }`}
              >
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-sand text-tan-dark">
                  <Icon size={18} />
                </span>
                <span className="flex-1 text-sm font-medium text-espresso">{item.label}</span>
                <ChevronRight size={18} className="text-taupe" />
              </button>
            )
          })}
        </div>
      </div>

      {isLoggedIn && (
        <div className="mt-6 px-5">
          <p className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-taupe">
            <Bell size={14} />
            Push Bildirimleri
          </p>
          <div className="rounded-2xl border border-cream-line bg-sand/40 p-4">
            {!isPushSupported() ? (
              <p className="text-sm text-taupe">
                Bu tarayıcı push bildirimlerini desteklemiyor.
              </p>
            ) : pushPermission === 'denied' ? (
              <p className="text-sm text-taupe">
                Bildirim izni engellenmiş. Açmak için tarayıcı site ayarlarından izni
                değiştirmen gerekiyor.
              </p>
            ) : pushPermission === 'granted' ? (
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm text-espresso-soft">
                  Bildirimler açık - takip ettiğin mekanlarda yeni bir durum
                  paylaşıldığında haber verilir.
                </p>
                <button
                  type="button"
                  onClick={handleDisablePush}
                  disabled={pushBusy}
                  className="flex shrink-0 items-center gap-2 rounded-full border border-tan-dark px-3 py-2 text-xs font-medium text-espresso disabled:opacity-60"
                >
                  <BellOff size={14} />
                  Kapat
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                <p className="text-sm text-espresso-soft">
                  Check-in yaptığın bir mekanda yeni bir durum paylaşıldığında anında
                  haberin olsun.
                </p>
                <button
                  type="button"
                  onClick={handleEnablePush}
                  disabled={pushBusy}
                  className="flex items-center gap-2 rounded-full bg-tan px-4 py-2 text-xs font-medium text-cream disabled:opacity-60"
                >
                  <Bell size={14} />
                  {pushBusy ? 'Açılıyor…' : 'Bildirimleri Aç'}
                </button>
                {typeof window !== 'undefined' && !window.isSecureContext && (
                  <p className="text-xs text-taupe">
                    Bildirimleri açabilmek için bu sayfaya güvenli bir bağlantı
                    üzerinden erişmen gerekiyor.
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {isLoggedIn && (
        <div className="mt-6 px-5">
          <p className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-taupe">
            <Telescope size={14} />
            Gözcü Rozeti
          </p>
          <div className="rounded-2xl border border-cream-line bg-sand/40 p-4">
            {stats === null ? (
              statsError ? (
                <p className="text-sm text-taupe">İstatistikler yüklenemedi.</p>
              ) : (
                <p className="text-sm text-taupe">Yükleniyor…</p>
              )
            ) : stats.badges.includes('gozcu') ? (
              <div className="flex items-center gap-3">
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gold/20 text-tan-dark">
                  <Telescope size={20} />
                </span>
                <div>
                  <p className="text-sm font-medium text-espresso">
                    Gözcü rozetini kazandın!
                  </p>
                  <p className="text-xs text-taupe">
                    Toplam {stats.status_count} durum paylaştın.
                  </p>
                </div>
              </div>
            ) : (
              <div>
                <p className="text-sm font-medium text-espresso">
                  {stats.status_count === 0
                    ? 'Henüz durum paylaşımın yok.'
                    : `${stats.status_count} durum paylaştın.`}
                </p>
                <p className="mt-1 text-xs text-taupe">
                  Gözcü rozetini kazanmak için {stats.gozcu_threshold - stats.status_count} durum
                  daha paylaş.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {isLoggedIn && user?.referral_code && (
        <div className="mt-6 px-5">
          <p className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-taupe">
            <UserPlus size={14} />
            Arkadaşını Davet Et
          </p>
          <div className="rounded-2xl border border-cream-line bg-sand/40 p-4">
            <p className="text-sm text-espresso-soft">
              Davet ettiğin kişi sayısı:{' '}
              <span className="font-medium text-espresso">
                {stats === null ? '…' : stats.referral_count}
              </span>
            </p>
            <div className="mt-3 flex items-center gap-2">
              <code className="flex-1 truncate rounded-lg border border-cream-line bg-cream px-3 py-2 text-xs text-espresso-soft">
                {window.location.origin}/register?ref={user.referral_code}
              </code>
              <button
                type="button"
                onClick={handleCopyReferralLink}
                aria-label="Davet linkini kopyala"
                className="flex shrink-0 items-center gap-1.5 rounded-full bg-tan px-3 py-2 text-xs font-medium text-cream"
              >
                {referralLinkCopied ? <Check size={14} /> : <Copy size={14} />}
                Kopyala
              </button>
            </div>
            <p className="mt-2 text-xs text-taupe">Davet kodun: {user.referral_code}</p>
          </div>
        </div>
      )}

      {isLoggedIn && user?.is_moderator && (
        <div className="mt-6 px-5">
          <button
            type="button"
            onClick={() => navigate('/moderation')}
            className="flex w-full items-center gap-3 rounded-2xl border border-cream-line bg-sand/40 px-4 py-4 text-left"
          >
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-sand text-tan-dark">
              <ShieldCheck size={18} />
            </span>
            <span className="flex-1 text-sm font-medium text-espresso">Moderasyon Paneli</span>
            <ChevronRight size={18} className="text-taupe" />
          </button>
        </div>
      )}

      {isLoggedIn && (
        <div className="mt-6 px-5">
          <p className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-taupe">
            <ShieldX size={14} />
            Engellediklerim
          </p>
          <div className="overflow-hidden rounded-2xl border border-cream-line bg-sand/40">
            {blockedLoading ? (
              <p className="px-4 py-4 text-sm text-taupe">Yükleniyor…</p>
            ) : blockedProfiles.length === 0 ? (
              <p className="px-4 py-4 text-sm text-taupe">Kimseyi engellemedin.</p>
            ) : (
              blockedProfiles.map((profile, i) => (
                <div
                  key={profile.id}
                  className={`flex items-center gap-3 px-4 py-3 ${
                    i !== blockedProfiles.length - 1 ? 'border-b border-cream-line' : ''
                  }`}
                >
                  <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-sand text-tan-dark">
                    <UserX size={16} />
                  </span>
                  <span className="flex-1 text-sm font-medium text-espresso">
                    {profile.display_name}
                  </span>
                  {unblockConfirmId === profile.id ? (
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => handleUnblock(profile.id)}
                        className="rounded-full bg-tan px-3 py-1.5 text-xs font-medium text-cream"
                      >
                        Emin misin?
                      </button>
                      <button
                        type="button"
                        onClick={() => setUnblockConfirmId(null)}
                        className="text-xs text-taupe"
                      >
                        Vazgeç
                      </button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={() => setUnblockConfirmId(profile.id)}
                      className="rounded-full border border-tan-dark px-3 py-1.5 text-xs font-medium text-espresso"
                    >
                      Engeli kaldır
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      <Toast message={toast} />
    </div>
  )
}
