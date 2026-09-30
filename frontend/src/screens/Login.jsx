import { ChevronLeft, Loader2, LogIn } from 'lucide-react'
import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/AuthContext.jsx'

export default function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const redirectTo = location.state?.from ?? '/profile'

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      await login({ email: email.trim(), password })
      navigate(redirectTo, { replace: true })
    } catch (err) {
      setError(err.message || 'Giriş yapılamadı.')
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

      <div className="mt-8 flex flex-1 flex-col justify-center gap-6">
        <div>
          <h1 className="font-display text-2xl font-medium text-espresso">Giriş Yap</h1>
          <p className="mt-1 text-sm text-taupe">Yorum ve durum paylaşmak için giriş yapmalısın.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
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
            placeholder="Şifre"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
            className="w-full rounded-lg border border-cream-line bg-cream px-3 py-2.5 text-sm text-espresso outline-none focus:border-tan"
          />

          {error && <p className="text-sm text-tan-dark">{error}</p>}

          <button
            type="submit"
            disabled={submitting}
            className="flex w-full items-center justify-center gap-2 rounded-full bg-tan px-4 py-3 text-sm font-medium text-cream disabled:opacity-60"
          >
            {submitting ? <Loader2 size={16} className="animate-spin" /> : <LogIn size={16} />}
            Giriş Yap
          </button>
        </form>

        <p className="text-center text-sm text-taupe">
          Hesabın yok mu?{' '}
          <button
            type="button"
            onClick={() => navigate('/register', { state: { from: redirectTo } })}
            className="font-medium text-tan-dark underline"
          >
            Kayıt ol
          </button>
        </p>
      </div>
    </div>
  )
}
