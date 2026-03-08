import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'

import { SessionSummary, getSessionSummary } from '../services/api'

function modeLabel(mode: string): string {
  if (mode === 'exam') return 'Eksamensmodus'
  if (mode === 'training_single') return 'Trening: én generator'
  if (mode === 'training_multi') return 'Trening: flere generatorer'
  return mode
}

export function ResultsPage() {
  const { sessionId } = useParams()
  const [summary, setSummary] = useState<SessionSummary | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!sessionId) return
    getSessionSummary(sessionId).then(setSummary).catch((e) => setError((e as Error).message))
  }, [sessionId])

  return (
    <section className="panel">
      <h2>Resultat</h2>
      {error && <p className="error">{error}</p>}
      {!summary && !error && <p>Laster oppsummering...</p>}
      {summary && (
        <div className="stats-grid">
          <div><strong>{summary.solved}</strong><span>Besvarte</span></div>
          <div><strong>{summary.correct}</strong><span>Riktige</span></div>
          <div><strong>{summary.score.toFixed(1)}</strong><span>Poeng</span></div>
          <div><strong>{modeLabel(summary.mode)}</strong><span>Modus</span></div>
        </div>
      )}
    </section>
  )
}
