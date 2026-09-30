import { ChevronLeft, MessageCircle } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import EmptyState from '../components/EmptyState.jsx'

// Placeholder shape for a future conversation list item. Not wired up yet -
// there is no messaging backend, so nothing renders this component today.
// eslint-disable-next-line no-unused-vars
function ConversationItem({ conversation }) {
  return (
    <button
      type="button"
      className="flex w-full items-center gap-3 rounded-2xl border border-cream-line bg-sand/40 p-3 text-left"
    >
      <span className="h-11 w-11 shrink-0 rounded-full bg-sand-dark" />
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-espresso">{conversation.author}</p>
        <p className="truncate text-xs text-taupe">{conversation.lastMessage}</p>
      </div>
    </button>
  )
}

export default function Messages() {
  const navigate = useNavigate()

  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex items-center gap-3 border-b border-cream-line px-4 py-4">
        <button
          type="button"
          onClick={() => navigate(-1)}
          aria-label="Geri"
          className="flex h-9 w-9 items-center justify-center rounded-full text-espresso-soft"
        >
          <ChevronLeft size={22} />
        </button>
        <h1 className="font-display text-xl text-espresso">Mesajlar</h1>
      </header>

      <EmptyState
        icon={<MessageCircle size={26} />}
        title="Henüz mesajın yok"
        description="Bir mekan sayfasından yorum yapan kullanıcılarla ileride buradan mesajlaşabileceksin."
      />
    </div>
  )
}
