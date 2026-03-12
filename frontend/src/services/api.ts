export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

export type GeneratorConfig = {
  key: string
  name: string
  description: string
  tema: string
  part: 'del1' | 'del2'
  answer_type: string
  difficulty: number
  weight: number
  is_enabled: boolean
  updated_at: string
}

export type ProblemRead = {
  session_id: string
  session_item_id: string
  order_index: number
  generator_key: string
  generator_name?: string
  part: 'del1' | 'del2'
  prompt: string
  answer_type: string
  metadata: Record<string, unknown>
  assets: string[]
  max_points: number
  hint?: string
}

export type SubmitResponse = {
  is_correct: boolean
  score: number
  max_points: number
  confidence: number
  uncertain: boolean
  feedback: string
  normalized_answer: string
  details: Record<string, unknown>
  solution_short: string
  solution_steps: string[]
}

export type SessionSummary = {
  session_id: string
  mode: string
  status: string
  started_at: string
  solved: number
  correct: number
  score: number
}

export type ProgressOverview = {
  solved_total: number
  correct_total: number
  accuracy: number
  del1_solved: number
  del2_solved: number
}

export type ProgressPerGenerator = {
  generator_key: string
  solved: number
  correct: number
  accuracy: number
}

export type ProgressTimelinePoint = {
  date: string
  solved: number
  correct: number
  accuracy: number
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  })

  if (!res.ok) {
    const body = await res.text()
    let message = body || `Feil ${res.status}`
    try {
      const json = JSON.parse(body)
      if (json?.detail) message = json.detail
    } catch {
      // not JSON – use raw body
    }
    throw new Error(message)
  }

  return (await res.json()) as T
}

export async function listGenerators(): Promise<GeneratorConfig[]> {
  return request('/generators', { method: 'GET' })
}

export async function startExam(): Promise<{ session_id: string; mode: string; items: ProblemRead[] }> {
  return request('/modes/exam/start', { method: 'POST' })
}

export async function startTraining(
  mode: 'training_single' | 'training_multi',
  generatorKeys: string[],
): Promise<{ session_id: string; mode: string }> {
  return request('/modes/training/start', {
    method: 'POST',
    body: JSON.stringify({ mode, generator_keys: generatorKeys }),
  })
}

export async function nextTrainingProblem(sessionId: string): Promise<ProblemRead> {
  return request(`/modes/training/${sessionId}/next`, { method: 'POST' })
}

export async function submitAnswer(
  sessionId: string,
  sessionItemId: string,
  answer: string,
): Promise<SubmitResponse> {
  return request(`/modes/sessions/${sessionId}/submit`, {
    method: 'POST',
    body: JSON.stringify({ session_item_id: sessionItemId, answer }),
  })
}

export async function getSessionSummary(sessionId: string): Promise<SessionSummary> {
  return request(`/modes/sessions/${sessionId}/summary`, { method: 'GET' })
}

export async function getProgressOverview(): Promise<ProgressOverview> {
  return request('/progress/overview', { method: 'GET' })
}

export async function getProgressPerGenerator(): Promise<ProgressPerGenerator[]> {
  return request('/progress/generators', { method: 'GET' })
}

export async function getProgressTimeline(): Promise<ProgressTimelinePoint[]> {
  return request('/progress/timeline', { method: 'GET' })
}

export function toAssetUrl(assetPath: string): string {
  if (assetPath.startsWith('http://') || assetPath.startsWith('https://')) {
    return assetPath
  }
  const origin = API_BASE_URL.replace('/api/v1', '')
  return `${origin}${assetPath}`
}
