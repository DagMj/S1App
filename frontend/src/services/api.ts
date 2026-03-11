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

const TOKEN_KEY = 's1_token'

export function saveToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

function authHeaders(): HeadersInit {
  const token = getToken()
  if (!token) return {}
  return { Authorization: `Bearer ${token}` }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
      ...authHeaders(),
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

export async function register(email: string, fullName: string, password: string): Promise<void> {
  await request('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, full_name: fullName, password }),
  })
}

export async function login(email: string, password: string): Promise<void> {
  const body = new URLSearchParams()
  body.set('username', email)
  body.set('password', password)

  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body,
  })

  if (!res.ok) {
    const t = await res.text()
    throw new Error(t || 'Innlogging feilet')
  }

  const data = (await res.json()) as { access_token: string }
  saveToken(data.access_token)
}

export async function getMe(): Promise<{ id: string; email: string; full_name: string }> {
  return request('/auth/me', { method: 'GET' })
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
  return request('/progress/me/overview', { method: 'GET' })
}

export async function getProgressPerGenerator(): Promise<
  Array<{ generator_key: string; solved: number; correct: number; accuracy: number }>
> {
  return request('/progress/me/per-generator', { method: 'GET' })
}

export async function getProgressTimeline(): Promise<
  Array<{ date: string; solved: number; correct: number; accuracy: number }>
> {
  return request('/progress/me/timeline', { method: 'GET' })
}

export async function adminListGenerators(): Promise<GeneratorConfig[]> {
  return request('/admin/generators', { method: 'GET' })
}

export async function adminUpdateGenerator(
  key: string,
  payload: Partial<Pick<GeneratorConfig, 'part' | 'weight' | 'is_enabled'>>,
): Promise<GeneratorConfig> {
  return request(`/admin/generators/${key}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export async function adminSampleGenerator(key: string): Promise<{
  generator_key: string
  generator_name?: string
  prompt: string
  answer_type: string
  metadata: Record<string, unknown>
  assets: string[]
  solution_short: string
  solution_steps: string[]
}> {
  return request(`/admin/generators/${key}/sample`, { method: 'GET' })
}

export async function adminStressGenerator(
  key: string,
  count = 1000,
): Promise<{ ok: boolean; failures: string[] }> {
  return request(`/admin/generators/${key}/stress?count=${count}`, { method: 'POST' })
}

export function toAssetUrl(assetPath: string): string {
  if (assetPath.startsWith('http://') || assetPath.startsWith('https://')) {
    return assetPath
  }
  const origin = API_BASE_URL.replace('/api/v1', '')
  return `${origin}${assetPath}`
}

