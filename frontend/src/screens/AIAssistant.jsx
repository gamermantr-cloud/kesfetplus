import { useState } from 'react'
import { Camera, Clock, Info, MapPin, Send, Sparkles } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { getAllVenues } from '../lib/data.js'

const quickActions = [
  { id: 'about', label: 'Mekan hakkında', icon: Info },
  { id: 'live', label: 'Anlık durumu öğren', icon: Clock },
  { id: 'compare', label: 'Fotoğrafları karşılaştır', icon: Camera },
  { id: 'route', label: 'Rota oluştur', icon: MapPin },
]

// Kural tabanlı, gerçek veri setine dayanan basit bir asistan — bu bir LLM
// değil, sadece database/seed/*.json içindeki gerçek mekanları arayıp
// bulduğunu döndürüyor. Bilmediği bir şeyi asla uydurmuyor.
function findVenue(venues, query) {
  const q = query.toLowerCase().trim()
  if (!q) return null
  return (
    venues.find((v) => v.name.toLowerCase() === q) ??
    venues.find((v) => v.name.toLowerCase().includes(q) || q.includes(v.name.toLowerCase()))
  )
}

function answerAbout(venue) {
  if (!venue) {
    return 'Bu isimde bir mekan bulamadım. Elimdeki 243 gerçek mekandan biri değil gibi görünüyor — tam adını yazmayı dener misin?'
  }
  const parts = [`${venue.name}, ${venue.area ?? 'konumu kayıtlı değil'}.`]
  if (venue.tags?.length) parts.push(`Etiketler: ${venue.tags.join(', ')}.`)
  if (venue.crowdToday) parts.push(`Bugünkü yoğunluk (kayıtlı veri): ${venue.crowdToday}.`)
  return parts.join(' ')
}

function answerRoute(venue) {
  if (!venue) {
    return 'Rota oluşturmak için bir mekan adı söyler misin?'
  }
  const query = encodeURIComponent(`${venue.name} ${venue.area ?? ''}`)
  return {
    text: `${venue.name} için yol tarifi: `,
    link: `https://www.google.com/maps/dir/?api=1&destination=${query}`,
  }
}

export default function AIAssistant() {
  const navigate = useNavigate()
  const [messages, setMessages] = useState([])
  const [draft, setDraft] = useState('')
  const [activeAction, setActiveAction] = useState(null)
  const [venues, setVenues] = useState(null)

  async function ensureVenues() {
    if (venues) return venues
    const data = await getAllVenues()
    setVenues(data)
    return data
  }

  function pushMessage(role, content) {
    setMessages((prev) => [...prev, { id: Date.now() + Math.random(), role, content }])
  }

  async function handleSend(event) {
    event.preventDefault()
    const text = draft.trim()
    if (!text) return
    pushMessage('user', text)
    setDraft('')

    const data = await ensureVenues()

    if (activeAction === 'compare') {
      pushMessage(
        'assistant',
        'Fotoğraf karşılaştırma özelliği için henüz gerçek bir görsel analiz sistemimiz yok — bunu uydurmak istemiyorum, şu an yalnızca mekan bilgisi ve rota konusunda yardımcı olabilirim.',
      )
      return
    }

    if (activeAction === 'live') {
      const venue = findVenue(data, text)
      if (!venue) {
        pushMessage('assistant', 'Hangi mekanın anlık durumunu öğrenmek istiyorsun? Bir isim yazar mısın?')
        return
      }
      pushMessage('assistant', {
        text: `${venue.name} için anlık durumu, mekan sayfasındaki "Anlık Durum" sekmesinde gerçek zamanlı görebilirsin — oraya gidelim mi?`,
        goTo: venue.id,
      })
      return
    }

    if (activeAction === 'route') {
      const venue = findVenue(data, text)
      const result = answerRoute(venue)
      pushMessage('assistant', result)
      return
    }

    // Varsayılan / "about": serbest metinde geçen mekan adını ara.
    const venue = findVenue(data, text)
    pushMessage('assistant', answerAbout(venue))
  }

  function handleQuickAction(actionId) {
    setActiveAction(actionId)
    if (actionId === 'compare') {
      pushMessage(
        'assistant',
        'Fotoğraf karşılaştırma özelliği için henüz gerçek bir görsel analiz sistemimiz yok — uydurmak istemiyorum, bu özellik yakında eklenecek.',
      )
    } else {
      pushMessage('assistant', 'Bir mekan adı yazar mısın?')
    }
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
          Gerçek mekan verimizde arama yapan basit bir asistan — tam bir yapay zeka değil.
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
              onClick={() => handleQuickAction(action.id)}
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
        <p className="mt-3 font-sans text-xs text-taupe">“{activeLabel}” seçili — bir mekan adı yaz.</p>
      )}

      <div className="mt-6 flex-1 space-y-3">
        {messages.map((message) => {
          const isUser = message.role === 'user'
          const content = message.content
          const text = typeof content === 'string' ? content : content.text
          return (
            <div key={message.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-2.5 font-sans text-sm ${
                  isUser
                    ? 'rounded-br-sm bg-espresso text-cream'
                    : 'rounded-bl-sm border border-cream-line bg-sand text-espresso'
                }`}
              >
                {text}
                {!isUser && content.link && (
                  <a
                    href={content.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-1 block font-medium text-tan-dark underline"
                  >
                    Yol tarifini aç →
                  </a>
                )}
                {!isUser && content.goTo && (
                  <button
                    type="button"
                    onClick={() => navigate(`/place/${content.goTo}`)}
                    className="mt-1 block font-medium text-tan-dark underline"
                  >
                    Mekana git →
                  </button>
                )}
              </div>
            </div>
          )
        })}
      </div>

      <form onSubmit={handleSend} className="mt-6 flex items-center gap-2">
        <input
          type="text"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Bir mekan adı yaz..."
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
