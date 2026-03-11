import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { ProblemCard } from '../components/ProblemCard'
import { ProblemRead, SubmitResponse, startExam, submitAnswer } from '../services/api'

export function ExamPage() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [items, setItems] = useState<ProblemRead[]>([])
  const [index, setIndex] = useState(0)
  const [feedback, setFeedback] = useState<SubmitResponse | null>(null)
  const [answered, setAnswered] = useState<Record<string, SubmitResponse>>({})
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const current = items[index]
  const isLastQuestion = items.length > 0 && index + 1 === items.length
  const currentLocked = useMemo(() => {
    if (!current) return false
    return Boolean(answered[current.session_item_id])
  }, [answered, current])

  useEffect(() => {
    if (!current) {
      setFeedback(null)
      return
    }
    setFeedback(answered[current.session_item_id] ?? null)
  }, [current, answered])

  async function createExam() {
    setError('')
    for (let attempt = 0; attempt < 2; attempt++) {
      try {
        const res = await startExam()
        setSessionId(res.session_id)
        setItems(res.items)
        setIndex(0)
        setAnswered({})
        setFeedback(null)
        return
      } catch (err) {
        if (attempt === 0) {
          await new Promise((r) => setTimeout(r, 1500))
          continue
        }
        setError((err as Error).message)
      }
    }
  }

  async function onSubmit(answer: string) {
    if (!sessionId || !current || currentLocked) return

    setError('')
    try {
      const result = await submitAnswer(sessionId, current.session_item_id, answer)
      setAnswered((prev) => ({ ...prev, [current.session_item_id]: result }))
      setFeedback(result)
    } catch (err) {
      setError((err as Error).message)
    }
  }

  function goNext() {
    if (!sessionId) return
    if (index + 1 < items.length) {
      setIndex((i) => i + 1)
      return
    }
    navigate(`/results/${sessionId}`)
  }

  return (
    <section className="panel">
      <h2>Eksamensmodus</h2>
      {!sessionId && <button className="btn" onClick={createExam}>Start eksamensøkt</button>}
      {error && <p className="error">{error}</p>}

      {sessionId && current && (
        <>
          <p>Oppgave {index + 1} av {items.length}</p>
          <ProblemCard
            problem={current}
            onSubmit={onSubmit}
            feedback={feedback}
            allowEnterSubmit={!isLastQuestion}
            submitLabel={isLastQuestion ? 'Lever svar' : 'Send svar'}
            onAdvance={!isLastQuestion ? goNext : undefined}
            isLocked={currentLocked}
          />
          <div className="row-actions">
            <button
              className="btn secondary"
              disabled={index === 0}
              onClick={() => {
                setIndex((i) => Math.max(0, i - 1))
              }}
            >
              Forrige
            </button>
            <button className="btn" onClick={goNext}>
              {index + 1 < items.length ? 'Neste' : 'Lever besvarelse'}
            </button>
          </div>
        </>
      )}
    </section>
  )
}
