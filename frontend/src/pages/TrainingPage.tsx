import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { ProblemCard } from '../components/ProblemCard'
import {
  GeneratorConfig,
  ProblemRead,
  SubmitResponse,
  listGenerators,
  nextTrainingProblem,
  startTraining,
  submitAnswer,
} from '../services/api'

export function TrainingPage() {
  const [generators, setGenerators] = useState<GeneratorConfig[]>([])
  const [selectedKeys, setSelectedKeys] = useState<string[]>([])
  const [mode, setMode] = useState<'training_single' | 'training_multi'>('training_single')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [problem, setProblem] = useState<ProblemRead | null>(null)
  const [feedback, setFeedback] = useState<SubmitResponse | null>(null)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    listGenerators()
      .then((rows) => {
        setGenerators(rows.filter((g) => g.is_enabled))
      })
      .catch((e) => setError((e as Error).message))
  }, [])

  const canStart = useMemo(() => {
    if (mode === 'training_single') return selectedKeys.length === 1
    return selectedKeys.length >= 1
  }, [mode, selectedKeys])

  async function begin() {
    setError('')
    try {
      const start = await startTraining(mode, selectedKeys)
      setSessionId(start.session_id)
      const next = await nextTrainingProblem(start.session_id)
      setProblem(next)
      setFeedback(null)
    } catch (err) {
      setError((err as Error).message)
    }
  }

  async function submit(answer: string) {
    if (!sessionId || !problem) return
    const res = await submitAnswer(sessionId, problem.session_item_id, answer)
    setFeedback(res)
  }

  async function next() {
    if (!sessionId) return
    const nxt = await nextTrainingProblem(sessionId)
    setProblem(nxt)
    setFeedback(null)
  }

  function goNext() {
    void next()
  }

  return (
    <section className="panel">
      <h2>Treningsmodus</h2>
      {!sessionId && (
        <>
          <div className="switcher">
            <button
              className={mode === 'training_single' ? 'btn' : 'btn secondary'}
              onClick={() => {
                setMode('training_single')
                setSelectedKeys([])
              }}
            >
              Én generator
            </button>
            <button
              className={mode === 'training_multi' ? 'btn' : 'btn secondary'}
              onClick={() => {
                setMode('training_multi')
                setSelectedKeys([])
              }}
            >
              Flere generatorer
            </button>
          </div>

          <div className="generator-list">
            {generators.map((g) => {
              const selected = selectedKeys.includes(g.key)
              return (
                <label key={g.key} className={`gen-item ${selected ? 'selected' : ''}`}>
                  <input
                    type={mode === 'training_single' ? 'radio' : 'checkbox'}
                    checked={selected}
                    onChange={(e) => {
                      if (mode === 'training_single') {
                        setSelectedKeys(e.target.checked ? [g.key] : [])
                      } else {
                        setSelectedKeys((prev) =>
                          e.target.checked ? [...prev, g.key] : prev.filter((k) => k !== g.key),
                        )
                      }
                    }}
                  />
                  <div>
                    <strong>{g.name}</strong>
                    <p>{g.tema} - {g.part}</p>
                  </div>
                </label>
              )
            })}
          </div>

          <button className="btn" disabled={!canStart} onClick={begin}>Start trening</button>
          {error && <p className="error">{error}</p>}
        </>
      )}

      {sessionId && problem && (
        <>
          <ProblemCard problem={problem} onSubmit={submit} feedback={feedback} onAdvance={goNext} />
          <div className="row-actions">
            <button className="btn secondary" onClick={goNext}>Neste oppgave</button>
            <button className="btn" onClick={() => navigate(`/results/${sessionId}`)}>Se resultat</button>
          </div>
        </>
      )}
    </section>
  )
}
