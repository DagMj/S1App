import { PropsWithChildren } from 'react'
import { Link } from 'react-router-dom'

export function AppLayout({ children }: PropsWithChildren) {
  return (
    <div className="app-shell">
      <header className="topbar">
        <Link to="/" className="brand">Eksamenstrening</Link>
      </header>
      <main className="main-content">{children}</main>
    </div>
  )
}
