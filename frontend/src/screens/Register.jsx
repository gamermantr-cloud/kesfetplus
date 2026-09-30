import { ChevronLeft, Loader2, UserPlus } from 'lucide-react'
import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/AuthContext.jsx'

export default function Register() {
  const navigate = useNavigate()
  const location = useLocation()
  const { register } = useAuth()

  const [displayName, setDisplayName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [privacyAccepted, setPrivacyAccepted] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const redirectTo = location.state?.from ?? '/profile'

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      await register({ email: email.trim(), password, displayName: displayName.trim() })
      navigate(redirectTo, { replace: true })
    } catch (err) {
      setError(err.message || 'Kayıt olunamadı.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen flex-col px-6 pb-10 pt-6">
      <button
        type="button"
        aria-label="Geri"
        onClick={() => navigate(-1)}
        className="flex h-9 w-9 items-center justify-center rounded-full bg-sand text-espresso-soft"
      >
        <ChevronLeft size={20} />
      </button>

      <div className="mt-8">
        <h1 className="font-display text-2xl font-medium text-espresso">Kayıt Ol</h1>
        <p className="mt-1 text-sm text-taupe">
          Keşfet Plus'ta gerçek bir hesapla yorum yapabilir, durum paylaşabilirsin.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="mt-6 space-y-3">
        <input
          type="text"
          placeholder="Görünen isim"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          autoComplete="name"
          required
          className="w-full rounded-lg border border-cream-line bg-cream px-3 py-2.5 text-sm text-espresso outline-none focus:border-tan"
        />
        <input
          type="email"
          placeholder="E-posta"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="email"
          required
          className="w-full rounded-lg border border-cream-line bg-cream px-3 py-2.5 text-sm text-espresso outline-none focus:border-tan"
        />
        <input
          type="password"
          placeholder="Şifre (en az 8 karakter)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="new-password"
          minLength={8}
          required
          className="w-full rounded-lg border border-cream-line bg-cream px-3 py-2.5 text-sm text-espresso outline-none focus:border-tan"
        />

        <label className="flex items-start gap-2.5 pt-1 text-xs text-taupe">
          <input
            type="checkbox"
            checked={privacyAccepted}
            onChange={(e) => setPrivacyAccepted(e.target.checked)}
            required
            className="mt-0.5 h-4 w-4 shrink-0 rounded border-cream-line accent-tan"
          />
          <span>
            Kayıt olarak{' '}
            <button
              type="button"
              onClick={() => navigate('/privacy')}
              className="font-medium text-tan-dark underline"
            >
              Gizlilik Politikası
            </button>
            'nı okuduğumu ve kişisel verilerimin belirtilen amaçlarla
            işlenmesini kabul ediyorum.
          </span>
        </label>

        {error && <p className="text-sm text-tan-dark">{error}</p>}

        <button
          type="submit"
          disabled={submitting || !privacyAccepted}
          className="flex w-full items-center justify-center gap-2 rounded-full bg-tan px-4 py-3 text-sm font-medium text-cream disabled:opacity-60"
        >
          {submitting ? <Loader2 size={16} className="animate-spin" /> : <UserPlus size={16} />}
          Kayıt Ol
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-taupe">
        Zaten hesabın var mı?{' '}
        <button
          type="button"
          onClick={() => navigate('/login', { state: { from: redirectTo } })}
          className="font-medium text-tan-dark underline"
        >
          Giriş yap
        </button>
      </p>
    </div>
  )
}
