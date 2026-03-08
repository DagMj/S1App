import { useEffect, useState } from 'react'

import {
  GeneratorConfig,
  adminListGenerators,
  adminSampleGenerator,
  adminStressGenerator,
  adminUpdateGenerator,
  toAssetUrl,
} from '../services/api'
import { MathText } from '../components/MathText'

export function AdminPage() {
  const [rows, setRows] = useState<GeneratorConfig[]>([])
  const [error, setError] = useState('')
  const [status, setStatus] = useState('')
  const [sample, setSample] = useState<{
    key: string
    prompt: string
    assets: string[]
    solution_short: string
  } | null>(null)

  async function load() {
    try {
      const data = await adminListGenerators()
      setRows(data)
    } catch (e) {
      setError((e as Error).message)
    }
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <section className="panel">
      <h2>Admin / utviklerverktøy</h2>
      {error && <p className="error">{error}</p>}
      {status && <p>{status}</p>}

      <table className="data-table">
        <thead>
          <tr>
            <th>Nøkkel</th>
            <th>Del</th>
            <th>Vekt</th>
            <th>Aktiv</th>
            <th>Handling</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.key}>
              <td>{row.key}</td>
              <td>
                <select
                  value={row.part}
                  onChange={async (e) => {
                    await adminUpdateGenerator(row.key, { part: e.target.value as 'del1' | 'del2' })
                    await load()
                  }}
                >
                  <option value="del1">del1</option>
                  <option value="del2">del2</option>
                </select>
              </td>
              <td>
                <input
                  type="number"
                  defaultValue={row.weight}
                  step="0.1"
                  onBlur={async (e) => {
                    const weight = Number(e.target.value)
                    await adminUpdateGenerator(row.key, { weight })
                    await load()
                  }}
                />
              </td>
              <td>
                <input
                  type="checkbox"
                  checked={row.is_enabled}
                  onChange={async (e) => {
                    await adminUpdateGenerator(row.key, { is_enabled: e.target.checked })
                    await load()
                  }}
                />
              </td>
              <td>
                <div className="row-actions">
                  <button
                    className="ghost"
                    onClick={async () => {
                      const s = await adminSampleGenerator(row.key)
                      setSample({
                        key: row.key,
                        prompt: s.prompt,
                        assets: s.assets,
                        solution_short: s.solution_short,
                      })
                    }}
                  >
                    Eksempel
                  </button>
                  <button
                    className="ghost"
                    onClick={async () => {
                      setStatus(`Kjører stress-test for ${row.key}...`)
                      const res = await adminStressGenerator(row.key, 1000)
                      setStatus(res.ok ? `${row.key}: OK (1000/1000)` : `${row.key}: FEIL (${res.failures.length})`)
                    }}
                  >
                    Stress-test
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {sample && (
        <article className="panel" style={{ marginTop: '1rem' }}>
          <h3>Eksempel: {sample.key}</h3>
          <MathText text={sample.prompt} />
          {sample.assets.map((asset) => (
            <img key={asset} src={toAssetUrl(asset)} alt="Eksempelfigur" className="problem-asset" />
          ))}
          <p><strong>Løsning:</strong> {sample.solution_short}</p>
        </article>
      )}
    </section>
  )
}
