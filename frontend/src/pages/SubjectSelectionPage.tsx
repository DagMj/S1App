import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const subjects = [
  { id: '1p', label: '1P', available: false },
  { id: '2p', label: '2P', available: false },
  { id: '1t', label: '1T', available: false },
  { id: 's1', label: 'S1', available: true },
  { id: 's2', label: 'S2', available: false },
  { id: 'r1', label: 'R1', available: false },
  { id: 'r2', label: 'R2', available: false },
]

export function SubjectSelectionPage() {
  const navigate = useNavigate()
  const [showMessage, setShowMessage] = useState(false)

  function handleClick(subject: typeof subjects[0]) {
    if (subject.available) {
      navigate('/s1')
    } else {
      setShowMessage(true)
      setTimeout(() => setShowMessage(false), 3000)
    }
  }

  return (
    <div className="subject-selection">
      <div className="hero" style={{ marginBottom: '1.5rem' }}>
        <h1>Velg fag</h1>
        <p style={{ margin: 0, opacity: 0.9 }}>
          Øv til eksamen med oppgaver tilpasset hvert fag.
        </p>
      </div>

      <div className="subject-grid">
        {subjects.map((s) => (
          <button
            key={s.id}
            className={`subject-card ${s.available ? 'subject-card--available' : 'subject-card--unavailable'}`}
            onClick={() => handleClick(s)}
          >
            <span className="subject-label">{s.label}</span>
            {s.available && <span className="subject-badge">Klar</span>}
          </button>
        ))}
      </div>

      {showMessage && (
        <div className="subject-coming-soon">
          Bare S1 har innhold foreløpig – de andre fagene kommer snart!
        </div>
      )}
    </div>
  )
}
