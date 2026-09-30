import { Bell, ChevronLeft } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import EmptyState from '../components/EmptyState.jsx'

// Not yet used anywhere — kept ready for when a real notifications feed exists
// (a real list design will replace this draft item shape alongside EmptyState).
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

      <EmptyState
        icon={<Bell size={26} />}
        title="Henüz bildirimin yok"
        description="Kaydettiğin mekanlarda bir şey değiştiğinde burada göreceksin."
      />
    </div>
  )
}
