import { useState } from 'react'
import { Camera, Clock, Info, MapPin, Send, Sparkles } from 'lucide-react'

const quickActions = [
  { id: 'about', label: 'Mekan hakkında', icon: Info },
  { id: 'live', label: 'Anlık durumu öğren', icon: Clock },
  { id: 'compare', label: 'Fotoğrafları karşılaştır', icon: Camera },
  { id: 'route', label: 'Rota oluştur', icon: MapPin },
]

export default function AIAssistant() {
  const [messages, setMessages] = useState([])
  const [draft, setDraft] = useState('')
  const [activeAction, setActiveAction] = useState(null)

  function handleSend(event) {
    event.preventDefault()
    const text = draft.trim()
    if (!text) return
    setMessages((prev) => [...prev, { id: Date.now(), text }])
    setDraft('')
  }

  const activeLabel = quickActions.find((action) => action.id === activeAction)?.label

  return (
    <div className="flex min-h-screen flex-col px-6 pb-6 pt-10">
      <header className="flex flex-col items-center text-center">
        <span className="flex h-11 w-11 items-center justify-center rounded-full bg-tan/20 text-tan-dark">
          <Sparkles size={22} />
        </span>
        <h1 className="mt-3 font-display text-3xl font-medium text-espresso">Keşfet+ AI</h1>
        <p className="mt-2 font-sans text-sm text-taupe">
          Planla. Sor. Karşılaştır. Güvende Kal.
        </p>
      </header>

      <div className="mt-6 grid grid-cols-2 gap-3">
        {quickActions.map((action) => {
          const Icon = action.icon
          const isActive = activeAction === action.id
          return (
            <button
              key={action.id}
              type="button"
              onClick={() => setActiveAction(action.id)}
              className={`flex flex-col items-start gap-3 rounded-2xl border px-4 py-4 text-left transition-colors ${
                isActive
                  ? 'border-tan bg-sand-dark'
                  : 'border-cream-line bg-sand hover:bg-sand-dark'
              }`}
            >
              <Icon size={20} className="text-tan-dark" />
              <span className="font-sans text-sm font-medium text-espresso">{action.label}</span>
            </button>
          )
        })}
      </div>

      {activeAction && (
        <p className="mt-3 font-sans text-xs text-taupe">
          “{activeLabel}” özelliği yakında aktif olacak.
        </p>
      )}

      <div className="mt-6 rounded-2xl border border-cream-line bg-sand/60 p-4">
        <p className="font-display text-lg text-espresso">Gerçek mi, aynı mı?</p>
        <p className="mt-1 font-sans text-sm text-espresso-soft">
          Instagram'daki fotoğraflarla mekanın güncel fotoğraflarını karşılaştır.
        </p>
        <div className="mt-3 flex gap-2">
          <div className="h-16 w-16 rounded-xl bg-gradient-to-br from-tan to-tan-dark" />
          <div className="h-16 w-16 rounded-xl bg-gradient-to-br from-sand-dark to-taupe" />
        </div>
      </div>

      <div className="mt-6 flex-1 space-y-3">
        {messages.map((message) => (
          <div key={message.id} className="flex justify-end">
            <div className="max-w-[80%] rounded-2xl rounded-br-sm bg-espresso px-4 py-2.5 font-sans text-sm text-cream">
              {message.text}
            </div>
          </div>
        ))}
        {messages.length > 0 && (
          <p className="font-sans text-xs italic text-taupe">Bu özellik yakında.</p>
        )}
      </div>

      <form onSubmit={handleSend} className="mt-6 flex items-center gap-2">
        <input
          type="text"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Bir şey sor..."
          className="flex-1 rounded-full border border-cream-line bg-sand px-5 py-3 font-sans text-sm text-espresso placeholder:text-taupe focus:outline-none focus:ring-2 focus:ring-tan"
        />
        <button
          type="submit"
          aria-label="Gönder"
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-tan text-cream transition-colors hover:bg-tan-dark"
        >
          <Send size={18} />
        </button>
      </form>
    </div>
  )
}
