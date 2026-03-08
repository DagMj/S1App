import { Link } from 'react-router-dom'

export function ProblemPage() {
  return (
    <section className="panel">
      <h2>Oppgavevisning</h2>
      <p>Denne siden brukes som dedikert oppgavevisning i videre utvidelser.</p>
      <p>Start en økt fra <Link to="/modes">modusvalg</Link> for å vise oppgaver.</p>
    </section>
  )
}
