import { Bell, ChevronLeft } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

// Not yet used anywhere — kept ready for when a real notifications feed exists.
function NotificationItem({ icon, title, description, time }) {
  return (
    <li className="flex items-start gap-3 rounded-2xl border border-cream-line bg-sand/40 p-4">
      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-sand text-tan-dark">
        {icon}
      </span>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-espresso">{title}</p>
        <p className="mt-0.5 text-sm text-espresso-soft">{description}</p>
      </div>
      <span className="shrink-0 text-xs text-taupe">{time}</span>
    </li>
  )
}

export default function Notifications() {
  const navigate = useNavigate()

  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex items-center gap-3 border-b border-cream-line px-5 pb-4 pt-6">
        <button
          type="button"
          onClick={() => navigate(-1)}
          aria-label="Geri"
          className="flex h-9 w-9 items-center justify-center rounded-full bg-sand text-espresso-soft"
        >
          <ChevronLeft size={20} />
        </button>
        <h1 className="font-display text-xl text-espresso">Bildirimler</h1>
      </header>

      <div className="flex flex-1 flex-col items-center justify-center gap-3 px-10 text-center">
        <Bell size={40} className="text-taupe" />
        <p className="font-display text-lg text-espresso">Henüz bildirimin yok</p>
        <p className="text-sm text-taupe">
          Kaydettiğin mekanlarda bir şey değiştiğinde burada göreceksin.
        </p>
      </div>
    </div>
  )
}
