import { useEffect, useState } from 'react'

import { ProgressOverview, ProgressPerGenerator, ProgressTimelinePoint, getProgressOverview, getProgressPerGenerator, getProgressTimeline } from '../services/api'

function pct(n: number): string {
  return (n * 100).toFixed(1) + '%'
}

export function ProgressPage() {
  const [overview, setOverview] = useState<ProgressOverview | null>(null)
  const [perGen, setPerGen] = useState<ProgressPerGenerator[]>([])
  const [timeline, setTimeline] = useState<ProgressTimelinePoint[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([
      getProgressOverview(),
      getProgressPerGenerator(),
      getProgressTimeline(),
    ])
      .then(([ov, pg, tl]) => {
        setOverview(ov)
        setPerGen(pg)
        setTimeline(tl)
      })
      .catch((e) => setError((e as Error).message))
  }, [])

  return (
    <section className="panel">
      <h2>Fremgang</h2>
      {error && <p className="error">{error}</p>}
      {!overview && !error && <p>Laster statistikk...</p>}

      {overview && (
        <>
          <div className="stats-grid" style={{ marginBottom: '1.5rem' }}>
            <div><strong>{overview.solved_total}</strong><span>Besvarte</span></div>
            <div><strong>{overview.correct_total}</strong><span>Riktige</span></div>
            <div><strong>{pct(overview.accuracy)}</strong><span>Treffprosent</span></div>
            <div><strong>{overview.del1_solved}</strong><span>Del 1</span></div>
            <div><strong>{overview.del2_solved}</strong><span>Del 2</span></div>
          </div>

          {perGen.length > 0 && (
            <>
              <h3 style={{ margin: '0 0 0.5rem' }}>Per tema</h3>
              <table className="data-table" style={{ marginBottom: '1.5rem' }}>
                <thead>
                  <tr>
                    <th>Generator</th>
                    <th>Besvart</th>
                    <th>Riktig</th>
                    <th>Treff%</th>
                  </tr>
                </thead>
                <tbody>
                  {perGen.map((g) => (
                    <tr key={g.generator_key}>
                      <td>{g.generator_key}</td>
                      <td>{g.solved}</td>
                      <td>{g.correct}</td>
                      <td>{pct(g.accuracy)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}

          {timeline.length > 0 && (
            <>
              <h3 style={{ margin: '0 0 0.5rem' }}>Tidslinje</h3>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Dato</th>
                    <th>Besvart</th>
                    <th>Riktig</th>
                    <th>Treff%</th>
                  </tr>
                </thead>
                <tbody>
                  {timeline.map((t) => (
                    <tr key={t.date}>
                      <td>{t.date}</td>
                      <td>{t.solved}</td>
                      <td>{t.correct}</td>
                      <td>{pct(t.accuracy)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}

          {overview.solved_total === 0 && (
            <p style={{ color: 'var(--muted)' }}>Ingen oppgaver besvart ennå. Start trening eller eksamensøkt!</p>
          )}
        </>
      )}
    </section>
  )
}
