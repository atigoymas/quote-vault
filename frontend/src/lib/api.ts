import type { MoodSearchResult, Quote, SearchResult, TagCount } from '../types'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new ApiError(response.status, body?.detail ?? `Request failed (${response.status})`)
  }

  return response.json() as Promise<T>
}

export function createQuote(payload: {
  text: string
  author?: string
  source?: string
}): Promise<Quote> {
  return request<Quote>('/quotes', { method: 'POST', body: JSON.stringify(payload) })
}

export function listTags(): Promise<TagCount[]> {
  return request<TagCount[]>('/tags')
}

export function listQuotes(tag?: string): Promise<Quote[]> {
  const query = tag ? `?tag=${encodeURIComponent(tag)}` : ''
  return request<Quote[]>(`/quotes${query}`)
}

export function searchMood(feeling: string, tag?: string): Promise<MoodSearchResult> {
  return request<MoodSearchResult>('/search/mood', {
    method: 'POST',
    body: JSON.stringify({ feeling, tag: tag ?? null }),
  })
}

export function searchTopic(query: string, tag?: string): Promise<SearchResult[]> {
  return request<SearchResult[]>('/search/topic', {
    method: 'POST',
    body: JSON.stringify({ query, tag: tag ?? null }),
  })
}
