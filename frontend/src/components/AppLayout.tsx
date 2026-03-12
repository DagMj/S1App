import { PropsWithChildren } from 'react'
import { NavLink } from 'react-router-dom'

export function AppLayout({ children }: PropsWithChildren) {
  return (
    <div className="app-shell">
      <header className="topbar">
        <NavLink to="/" className="brand">Eksamenstrening</NavLink>
        <nav className="nav-links">
          <NavLink to="/s1">S1</NavLink>
          <NavLink to="/progress">Fremgang</NavLink>
        </nav>
      </header>
      <main className="main-content">{children}</main>
    </div>
  )
}
