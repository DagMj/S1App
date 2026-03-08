import { ReactNode } from 'react'
import 'katex/dist/katex.min.css'
import { BlockMath, InlineMath } from 'react-katex'

function normalizeText(text: string): string {
  return text.replace(/\r\n/g, '\n').replace(/`n/g, '\n')
}

function renderPlainTextWithLineBreaks(text: string, keyPrefix: string) {
  const lines = text.split('\n')
  return lines.map((line, idx) => (
    <span key={`${keyPrefix}-${idx}`}>
      {line}
      {idx < lines.length - 1 && <br />}
    </span>
  ))
}

function renderSegment(segment: string, index: string) {
  if (segment.startsWith('$$') && segment.endsWith('$$')) {
    const latex = segment.slice(2, -2)
    return <BlockMath key={index} math={latex} />
  }

  const inlineParts = segment.split(/(\$[^$]+\$)/g)
  return (
    <p key={index}>
      {inlineParts.map((part, i) => {
        if (part.startsWith('$') && part.endsWith('$')) {
          return <InlineMath key={`${index}-${i}`} math={part.slice(1, -1)} />
        }
        return (
          <span key={`${index}-${i}`}>
            {renderPlainTextWithLineBreaks(part, `${index}-${i}`)}
          </span>
        )
      })}
    </p>
  )
}

function renderTextBlocks(text: string, keyPrefix: string): ReactNode[] {
  return text
    .split(/(\$\$[\s\S]*?\$\$)/g)
    .filter(Boolean)
    .map((segment, idx) => renderSegment(segment, `${keyPrefix}-${idx}`))
}

function parseList(line: string): string[] {
  return line
    .split(',')
    .map((part) => part.trim())
    .filter(Boolean)
}

function renderValueTableFromText(text: string, key: string): { before: string; table: ReactNode; after: string } | null {
  const xyMatch = text.match(/Verditabell:\s*\n\s*x:\s*([^\n]+)\n\s*y:\s*([^\n]+)/)
  if (xyMatch?.index !== undefined) {
    const before = text.slice(0, xyMatch.index).trimEnd()
    const after = text.slice(xyMatch.index + xyMatch[0].length).trimStart()
    const xVals = parseList(xyMatch[1])
    const yVals = parseList(xyMatch[2])
    const maxLen = Math.max(xVals.length, yVals.length)

    const table = (
      <table className="data-table" key={key}>
        <thead>
          <tr>
            <th>x</th>
            {Array.from({ length: maxLen }).map((_, i) => (
              <th key={`hx-${i}`}>{xVals[i] ?? ''}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          <tr>
            <th>y</th>
            {Array.from({ length: maxLen }).map((_, i) => (
              <td key={`hy-${i}`}>{yVals[i] ?? ''}</td>
            ))}
          </tr>
        </tbody>
      </table>
    )

    return { before, table, after }
  }

  const pairBlockMatch = text.match(/Verditabell:\s*\n((?:\s*x\s*=\s*[^,\n]+,\s*y\s*=\s*[^\n]+\n?){2,})/)
  if (pairBlockMatch?.index !== undefined) {
    const before = text.slice(0, pairBlockMatch.index).trimEnd()
    const after = text.slice(pairBlockMatch.index + pairBlockMatch[0].length).trimStart()

    const rows = pairBlockMatch[1]
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => {
        const m = line.match(/^x\s*=\s*([^,\n]+),\s*y\s*=\s*([^\n]+)$/)
        return m ? { x: m[1].trim(), y: m[2].trim() } : null
      })
      .filter((row): row is { x: string; y: string } => Boolean(row))

    if (rows.length > 0) {
      const table = (
        <table className="data-table" key={key}>
          <thead>
            <tr>
              <th>x</th>
              <th>y</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr key={`r-${idx}`}>
                <td>{row.x}</td>
                <td>{row.y}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )

      return { before, table, after }
    }
  }

  return null
}

export function MathText({ text }: { text: string }) {
  const normalized = normalizeText(text)
  const parsed = renderValueTableFromText(normalized, 'prompt-table')

  if (!parsed) {
    return <div className="math-text">{renderTextBlocks(normalized, 'segment')}</div>
  }

  return (
    <div className="math-text">
      {parsed.before && renderTextBlocks(parsed.before, 'before')}
      {parsed.table}
      {parsed.after && renderTextBlocks(parsed.after, 'after')}
    </div>
  )
}
