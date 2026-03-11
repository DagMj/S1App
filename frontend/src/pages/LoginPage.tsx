import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { getMe, login, register, saveIsAdmin } from '../services/api'

const DEV_USERS = [
  { label: 'Test Elev', email: 'elev@test.no', password: 'elev123' },
  { label: 'Test Admin', email: 'admin@test.no', password: 'admin123' },
]

async function loginAndSaveRole(email: string, password: string) {
  await login(email, password)
  const me = await getMe()
  saveIsAdmin(me.is_admin)
}

export function LoginPage() {
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('Elev')
  const [password, setPassword] = useState('')
  const [isRegister, setIsRegister] = useState(false)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const navigate = useNavigate()

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      if (isRegister) {
        await register(email, fullName, password)
      }
      await loginAndSaveRole(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  async function quickLogin(devEmail: string, devPassword: string) {
    setBusy(true)
    setError('')
    try {
      await loginAndSaveRole(devEmail, devPassword)
      navigate('/dashboard')
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="panel narrow">
      <h2>{isRegister ? 'Registrering' : 'Innlogging'}</h2>
      <form onSubmit={onSubmit} className="form-stack">
        {isRegister && (
          <input value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Fullt navn" />
        )}
        <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" placeholder="E-post" />
        <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" placeholder="Passord" />
        <button className="btn" type="submit" disabled={busy}>
          {busy ? 'Jobber...' : isRegister ? 'Registrer og logg inn' : 'Logg inn'}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
      <button className="ghost" onClick={() => setIsRegister((v) => !v)}>
        {isRegister ? 'Har allerede bruker' : 'Opprett ny bruker'}
      </button>

      {import.meta.env.DEV && (
        <div className="dev-quicklogin">
          <p className="dev-quicklogin__label">Hurtiginnlogging (kun i dev)</p>
          {DEV_USERS.map((u) => (
            <button
              key={u.email}
              className="ghost"
              disabled={busy}
              onClick={() => quickLogin(u.email, u.password)}
            >
              {u.label} — {u.email}
            </button>
          ))}
        </div>
      )}
    </section>
  )
}
