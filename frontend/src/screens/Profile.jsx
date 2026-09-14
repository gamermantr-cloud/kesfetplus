import {
  Bookmark,
  ChevronLeft,
  ChevronRight,
  HelpCircle,
  MessageSquare,
  Settings,
  User,
} from 'lucide-react'
import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

const MENU_ITEMS = [
  { id: 'saved', label: 'Kaydettiklerim', icon: Bookmark },
  { id: 'comments', label: 'Yorumlarım', icon: MessageSquare },
  { id: 'settings', label: 'Ayarlar', icon: Settings },
  { id: 'help', label: 'Yardım', icon: HelpCircle },
]

export default function Profile() {
  const navigate = useNavigate()
  const [toast, setToast] = useState(null)
  const toastTimer = useRef(null)

  function showComingSoon(label) {
    setToast(`${label} yakında geliyor`)
    clearTimeout(toastTimer.current)
    toastTimer.current = setTimeout(() => setToast(null), 1800)
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
        <p className="mt-4 font-display text-lg text-espresso">Misafir Kullanıcı</p>
        <p className="mt-1 text-xs text-taupe">Hesap sistemi yakında eklenecek</p>
      </div>

      <div className="mt-8 px-5">
        <div className="overflow-hidden rounded-2xl border border-cream-line bg-sand/40">
          {MENU_ITEMS.map((item, i) => {
            const Icon = item.icon
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => showComingSoon(item.label)}
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

      {toast && (
        <div className="fixed bottom-8 inset-x-0 z-10 mx-auto w-fit max-w-[430px] rounded-full bg-espresso px-4 py-2 text-xs font-medium text-cream shadow-lg">
          {toast}
        </div>
      )}
    </div>
  )
}
