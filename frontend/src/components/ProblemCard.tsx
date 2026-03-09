import { KeyboardEvent, useEffect, useMemo, useState } from 'react'
import { InlineMath } from 'react-katex'

import { MathText } from './MathText'
import { ProblemRead, SubmitResponse, toAssetUrl } from '../services/api'

const answerTypeLabels: Record<string, string> = {
  number: 'Tall',
  expression: 'Uttrykk',
  solution_set: 'Løsningsmengde',
  function: 'Funksjon',
  multiple_choice: 'Flervalg',
  model_choice: 'Modellvalg',
}

function humanize(value: string): string {
  return value
    .split('_')
    .filter(Boolean)
    .map((word) => word[0].toUpperCase() + word.slice(1))
    .join(' ')
}

function stripOuterParens(token: string): string {
  const trimmed = token.trim()
  if (trimmed.startsWith('(') && trimmed.endsWith(')')) {
    return trimmed.slice(1, -1)
  }
  return trimmed
}

function toInlineLatex(raw: string): string {
  let expr = raw.trim()
  if (!expr) return ''

  for (let i = 0; i < 4; i += 1) {
    const next = expr.replace(/\(([^()]+)\)\s*\/\s*\(([^()]+)\)/g, (_, left: string, right: string) => {
      return `\\frac{${left.trim()}}{${right.trim()}}`
    })
    if (next === expr) break
    expr = next
  }

  expr = expr.replace(/(^|[^A-Za-z\\])(-?\d+(?:[.,]\d+)?)\s*\/\s*(-?\d+(?:[.,]\d+)?)(?=$|[^A-Za-z])/g, (_, prefix: string, left: string, right: string) => {
    const l = left.replace(',', '.')
    const r = right.replace(',', '.')
    return `${prefix}\\frac{${l}}{${r}}`
  })

  expr = expr.replace(/([A-Za-z]+)\s*\/\s*(-?\d+(?:[.,]\d+)?)/g, (_, left: string, right: string) => {
    const r = right.replace(',', '.')
    return `\\frac{${left}}{${r}}`
  })

  expr = expr.replace(/\^\s*(\([^()]+\)|-?\d+(?:[.,]\d+)?|[A-Za-z])/g, (_, token: string) => {
    const exp = stripOuterParens(token).replace(',', '.')
    return `^{${exp}}`
  })

  expr = expr.replace(/\*/g, '\\cdot ')
  return expr
}

export function ProblemCard({
  problem,
  onSubmit,
  feedback,
  allowEnterSubmit = true,
  submitLabel = 'Send svar',
  onAdvance,
  isLocked = false,
}: {
  problem: ProblemRead
  onSubmit: (answer: string) => Promise<void>
  feedback?: SubmitResponse | null
  allowEnterSubmit?: boolean
  submitLabel?: string
  onAdvance?: () => void
  isLocked?: boolean
}) {
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [showHint, setShowHint] = useState(false)

  useEffect(() => {
    setAnswer('')
    setShowHint(false)
  }, [problem.session_item_id])

  const generatorLabel = problem.generator_name?.trim() || humanize(problem.generator_key)
  const answerTypeLabel = answerTypeLabels[problem.answer_type] ?? humanize(problem.answer_type)
  const hint = problem.hint?.trim()
  const canAdvanceWithEnter = Boolean(feedback && onAdvance)
  const previewLatex = useMemo(() => toInlineLatex(answer), [answer])

  async function handleSubmit() {
    if (isLocked || loading || answer.trim().length === 0) return
    setLoading(true)
    try {
      await onSubmit(answer)
    } finally {
      setLoading(false)
    }
  }

  function handleAdvance() {
    if (!onAdvance) return
    setAnswer('')
    onAdvance()
  }

  function onKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key !== 'Enter' || !allowEnterSubmit || loading) return
    event.preventDefault()

    if (canAdvanceWithEnter) {
      handleAdvance()
      return
    }

    void handleSubmit()
  }

  return (
    <section className="problem-card">
      <div className="problem-meta">
        <span>{generatorLabel}</span>
        <span>{answerTypeLabel}</span>
      </div>
      <MathText text={problem.prompt} />

      {problem.assets.length > 0 && (
        <div className="asset-grid">
          {problem.assets.map((asset) => (
            <img key={asset} src={toAssetUrl(asset)} alt="Figur" className="problem-asset" />
          ))}
        </div>
      )}

      {hint && (
        <div className="row-actions">
          <button className="ghost" onClick={() => setShowHint((v) => !v)}>
            {showHint ? 'Skjul hint' : 'Vis hint'}
          </button>
          {showHint && <p><strong>Tips:</strong> {hint}</p>}
        </div>
      )}

      <div className="answer-area">
        <div className="answer-input-wrap">
          <input
            className="answer-input"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Skriv svaret ditt"
            disabled={isLocked && !canAdvanceWithEnter}
          />

          {answer.trim().length > 0 && (
            <div className="answer-preview-box">
              <span className="answer-preview-label">Mattevisning:</span>
              <span className="answer-preview-math">
                <InlineMath math={previewLatex} renderError={() => <span>{answer}</span>} />
              </span>
            </div>
          )}
        </div>

        <button
          onClick={() => {
            if (canAdvanceWithEnter) {
              handleAdvance()
              return
            }
            void handleSubmit()
          }}
          disabled={loading || (!canAdvanceWithEnter && (answer.trim().length === 0 || isLocked))}
        >
          {loading ? 'Vurderer...' : canAdvanceWithEnter ? 'Neste oppgave' : submitLabel}
        </button>
      </div>

      {feedback && (
        <div className={`feedback ${feedback.is_correct ? 'ok' : 'bad'}`}>
          <p>{feedback.feedback}</p>
          <p>Poeng: {feedback.score}/{feedback.max_points}</p>
          <p>Sikkerhet: {feedback.confidence.toFixed(2)} {feedback.uncertain ? '(usikker)' : ''}</p>
          <div className="solution-sketch">
            <strong>Løsningsskisse:</strong>
            {feedback.solution_steps && feedback.solution_steps.length > 0 && (
              <ol className="solution-steps">
                {feedback.solution_steps.map((step, i) => (
                  <li key={i}><MathText text={step} /></li>
                ))}
              </ol>
            )}
            <div className="solution-answer"><MathText text={feedback.solution_short} /></div>
          </div>
          {isLocked && <p>Oppgaven er allerede levert i denne eksamensøkten.</p>}
        </div>
      )}
    </section>
  )
}
