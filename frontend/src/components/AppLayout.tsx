import { PropsWithChildren } from 'react'
import { Link, NavLink } from 'react-router-dom'

import { clearToken, getIsAdmin, getToken } from '../services/api'

export function AppLayout({ children }: PropsWithChildren) {
  const authed = Boolean(getToken())
  const isAdmin = getIsAdmin()

  return (
    <div className="app-shell">
      <header className="topbar">
        <Link to="/" className="brand">S1 Eksamenstrening</Link>
        <nav className="nav-links">
          <NavLink to="/dashboard">Oversikt</NavLink>
          <NavLink to="/modes">Modus</NavLink>
          <NavLink to="/progress">Progresjon</NavLink>
          {isAdmin && <NavLink to="/admin">Admin</NavLink>}
          {!authed ? (
            <NavLink to="/login">Innlogging</NavLink>
          ) : (
            <button
              className="ghost"
              onClick={() => {
                clearToken()
                window.location.href = '/login'
              }}
            >
              Logg ut
            </button>
          )}
        </nav>
      </header>

      <main className="main-content">{children}</main>
    </div>
  )
}
