import { useEffect, useState } from 'react'

import { getProgressOverview, getProgressPerGenerator, getProgressTimeline } from '../services/api'

function humanizeGeneratorKey(value: string): string {
  return value
    .split('_')
    .filter(Boolean)
    .map((word) => word[0].toUpperCase() + word.slice(1))
    .join(' ')
}

export function ProgressPage() {
  const [overview, setOverview] = useState<{
    solved_total: number
    correct_total: number
    accuracy: number
    del1_solved: number
    del2_solved: number
  } | null>(null)
  const [perGenerator, setPerGenerator] = useState<
    Array<{ generator_key: string; solved: number; correct: number; accuracy: number }>
  >([])
  const [timeline, setTimeline] = useState<
    Array<{ date: string; solved: number; correct: number; accuracy: number }>
  >([])
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([getProgressOverview(), getProgressPerGenerator(), getProgressTimeline()])
      .then(([o, g, t]) => {
        setOverview(o)
        setPerGenerator(g)
        setTimeline(t)
      })
      .catch((e) => setError((e as Error).message))
  }, [])

  return (
    <section className="panel">
      <h2>Progresjon</h2>
      {error && <p className="error">{error}</p>}
      {overview && (
        <div className="stats-grid">
          <div><strong>{overview.solved_total}</strong><span>Løst totalt</span></div>
          <div><strong>{overview.correct_total}</strong><span>Riktige totalt</span></div>
          <div><strong>{(overview.accuracy * 100).toFixed(1)}%</strong><span>Treffsikkerhet</span></div>
        </div>
      )}

      <h3>Per generator</h3>
      <table className="data-table">
        <thead>
          <tr>
            <th>Generator</th>
            <th>Løst</th>
            <th>Riktige</th>
            <th>Treff</th>
          </tr>
        </thead>
        <tbody>
          {perGenerator.map((row) => (
            <tr key={row.generator_key}>
              <td>{humanizeGeneratorKey(row.generator_key)}</td>
              <td>{row.solved}</td>
              <td>{row.correct}</td>
              <td>{(row.accuracy * 100).toFixed(1)}%</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Tidslinje</h3>
      <table className="data-table">
        <thead>
          <tr>
            <th>Dato</th>
            <th>Løst</th>
            <th>Riktige</th>
            <th>Treff</th>
          </tr>
        </thead>
        <tbody>
          {timeline.map((row) => (
            <tr key={row.date}>
              <td>{row.date}</td>
              <td>{row.solved}</td>
              <td>{row.correct}</td>
              <td>{(row.accuracy * 100).toFixed(1)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}
