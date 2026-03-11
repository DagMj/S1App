import { Link } from 'react-router-dom'

export function ModesPage() {
  return (
    <section className="panel">
      <h2>S1 – Velg modus</h2>
      <div className="mode-cards" style={{ gridTemplateColumns: 'repeat(2, minmax(0, 1fr))' }}>
        <Link to="/exam" className="mode-card">
          <h3>Eksamensmodus</h3>
          <p>10 oppgaver satt sammen som en ekte eksamen, med vektet trekning fra alle temaer.</p>
        </Link>
        <Link to="/training" className="mode-card">
          <h3>Tren oppgavetyper</h3>
          <p>Velg ett eller flere temaer og øv så mye du vil.</p>
        </Link>
      </div>
    </section>
  )
}
