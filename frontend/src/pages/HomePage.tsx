import { Link } from 'react-router-dom'

export function HomePage() {
  return (
    <section className="hero">
      <h1>Eksamensplattform for matematikk S1</h1>
      <p>
        Øv med realistiske oppgaver, få robust svarvurdering og følg progresjon over tid.
      </p>
      <div className="hero-actions">
        <Link className="btn" to="/login">Kom i gang</Link>
        <Link className="btn secondary" to="/modes">Velg modus</Link>
      </div>
    </section>
  )
}
