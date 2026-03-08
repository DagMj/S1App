import { Link } from 'react-router-dom'

export function ModesPage() {
  return (
    <section className="panel">
      <h2>Velg modus</h2>
      <div className="mode-cards">
        <Link to="/exam" className="mode-card">
          <h3>Eksamensmodus</h3>
          <p>6 del 1 + 4 del 2 med vektet trekning uten tilbakelegging.</p>
        </Link>
        <Link to="/training" className="mode-card">
          <h3>Trening: én generator</h3>
          <p>Uendelig trening på én oppgavetype.</p>
        </Link>
        <Link to="/training" className="mode-card">
          <h3>Trening: flere generatorer</h3>
          <p>Veksle mellom valgte oppgavetyper.</p>
        </Link>
      </div>
    </section>
  )
}
