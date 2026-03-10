import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { getMe, login, register, saveIsAdmin } from '../services/api'

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
      await login(email, password)
      const me = await getMe()
      saveIsAdmin(me.is_admin)
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
    </section>
  )
}
