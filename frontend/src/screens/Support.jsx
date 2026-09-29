import { ChevronLeft, HelpCircle, Mail, Send, ShieldX } from 'lucide-react'
import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

const SUPPORT_EMAIL = 'kesfetplusdestek@gmail.com'

const FAQ_ITEMS = [
  {
    question: 'Şikayet ettiğim bir yorum ne oluyor?',
    answer:
      'Bir yorumu veya kullanıcıyı şikayet ettiğinde bu bilgi kaydediliyor; ' +
      'ekibimiz inceliyor ve gerekirse içeriği kaldırıyor. Şikayet ettiğin ' +
      'yorum, senin akışından hemen kayboluyor — inceleme sonucu beklemene ' +
      'gerek yok.',
  },
  {
    question: 'Bir kullanıcıyı engellersem ne değişir?',
    answer:
      'Engellediğin kullanıcının yorumlarını ve durumlarını bir daha görmezsin. ' +
      'Profil ekranındaki "Engellediklerim" listesinden istediğin zaman ' +
      'engeli kaldırabilirsin.',
  },
]

export default function Support() {
  const navigate = useNavigate()
  const [reportText, setReportText] = useState('')
  const [toast, setToast] = useState(null)
  const toastTimer = useRef(null)

  function showToast(message) {
    setToast(message)
    clearTimeout(toastTimer.current)
    toastTimer.current = setTimeout(() => setToast(null), 1800)
  }

  function handleSendReport(event) {
    event.preventDefault()
    const trimmed = reportText.trim()
    if (!trimmed) {
      showToast('Önce ne olduğunu yazmalısın')
      return
    }
    const subject = encodeURIComponent('Keşfet Plus Hata Bildirimi')
    const body = encodeURIComponent(trimmed)
    window.location.href = `mailto:${SUPPORT_EMAIL}?subject=${subject}&body=${body}`
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
        <h1 className="ml-3 font-display text-xl text-espresso">Destek / Yardım</h1>
      </header>

      {/* Bize Ulaş */}
      <div className="mt-8 px-5">
        <p className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-taupe">
          <Mail size={14} />
          Bize Ulaş
        </p>
        <div className="overflow-hidden rounded-2xl border border-cream-line bg-sand/40 px-4 py-4">
          <p className="text-sm text-espresso-soft">
            Sorularının, önerilerinin veya şikayetlerinin için bize doğrudan
            e-posta ile ulaşabilirsin.
          </p>
          <a
            href={`mailto:${SUPPORT_EMAIL}`}
            className="mt-3 flex w-fit items-center gap-2 rounded-full bg-tan px-4 py-2 text-xs font-medium text-cream"
          >
            <Mail size={14} />
            {SUPPORT_EMAIL}
          </a>
        </div>
      </div>

      {/* Hata Bildir */}
      <div className="mt-6 px-5">
        <p className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-taupe">
          <Send size={14} />
          Hata Bildir
        </p>
        <form
          onSubmit={handleSendReport}
          className="overflow-hidden rounded-2xl border border-cream-line bg-sand/40 px-4 py-4"
        >
          <p className="mb-3 text-sm text-espresso-soft">
            Karşılaştığın bir sorunu anlat, gönder butonuna bastığında mail
            istemcin açılır ve mesajını doğrudan bize gönderebilirsin.
          </p>
          <textarea
            value={reportText}
            onChange={(event) => setReportText(event.target.value)}
            placeholder="Ne oldu? Hangi ekrandaydın, ne bekliyordun?"
            rows={5}
            className="w-full resize-none rounded-xl border border-cream-line bg-cream px-3 py-3 text-sm text-espresso outline-none placeholder:text-taupe"
          />
          <button
            type="submit"
            className="mt-3 flex items-center gap-2 rounded-full bg-tan px-4 py-2 text-xs font-medium text-cream"
          >
            <Send size={14} />
            Gönder
          </button>
          <p className="mt-2 text-[11px] text-taupe">
            Bu form doğrudan bir destek sistemine kaydetmiyor — gönder
            butonu e-posta uygulamanı önceden doldurulmuş bir mesajla açar.
          </p>
        </form>
      </div>

      {/* SSS */}
      <div className="mt-6 px-5">
        <p className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-taupe">
          <HelpCircle size={14} />
          Sıkça Sorulanlar
        </p>
        <div className="overflow-hidden rounded-2xl border border-cream-line bg-sand/40">
          {FAQ_ITEMS.map((item, i) => (
            <div
              key={item.question}
              className={`flex gap-3 px-4 py-4 ${
                i !== FAQ_ITEMS.length - 1 ? 'border-b border-cream-line' : ''
              }`}
            >
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-sand text-tan-dark">
                <ShieldX size={16} />
              </span>
              <div>
                <p className="text-sm font-medium text-espresso">{item.question}</p>
                <p className="mt-1 text-xs text-taupe">{item.answer}</p>
              </div>
            </div>
          ))}
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
