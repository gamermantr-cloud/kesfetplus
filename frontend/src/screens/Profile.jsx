import {
  Bookmark,
  ChevronLeft,
  ChevronRight,
  HelpCircle,
  LogIn,
  LogOut,
  MessageSquare,
  Settings,
  ShieldCheck,
  ShieldX,
  User,
  UserX,
} from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/AuthContext.jsx'
import { getUserProfile } from '../lib/api.js'

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

      {toast && (
        <div className="fixed bottom-8 inset-x-0 z-10 mx-auto w-fit max-w-[430px] rounded-full bg-espresso px-4 py-2 text-xs font-medium text-cream shadow-lg">
          {toast}
        </div>
      )}
    </div>
  )
}
