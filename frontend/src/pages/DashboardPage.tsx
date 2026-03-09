import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { ProgressOverview, getProgressOverview } from '../services/api'

export function DashboardPage() {
  const [overview, setOverview] = useState<ProgressOverview | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    getProgressOverview().then(setOverview).catch((e) => setError((e as Error).message))
  }, [])

  return (
    <section className="grid-two">
      <article className="panel">
        <h2>Oversikt</h2>
        {error && <p className="error">{error}</p>}
        {!overview && !error && <p>Laster...</p>}
        {overview && (
          <div className="stats-grid">
            <div><strong>{overview.solved_total}</strong><span>Løst</span></div>
            <div><strong>{overview.correct_total}</strong><span>Riktige</span></div>
            <div><strong>{(overview.accuracy * 100).toFixed(1)}%</strong><span>Treffsikkerhet</span></div>
          </div>
        )}
      </article>

      <article className="panel">
        <h2>Snarveier</h2>
        <div className="quick-links">
          <Link className="btn" to="/modes">Velg modus</Link>
          <Link className="btn secondary" to="/exam">Start eksamen</Link>
          <Link className="btn secondary" to="/training">Start trening</Link>
          <Link className="btn secondary" to="/progress">Se progresjon</Link>
        </div>
      </article>
    </section>
  )
}
