import type { Quote } from '../types'

const STORAGE_KEY = 'quote-vault:recently-viewed'
const MAX_ENTRIES = 20

export type ViewedQuote = Pick<Quote, 'id' | 'text' | 'author' | 'source' | 'tags'>

export function recordView(quote: ViewedQuote): void {
  const deduped = getRecentlyViewed().filter((q) => q.id !== quote.id)
  const next = [quote, ...deduped].slice(0, MAX_ENTRIES)
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
  } catch {
    // storage unavailable (private browsing, quota) — offline reading just skips this entry
  }
}

export function getRecentlyViewed(): ViewedQuote[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as ViewedQuote[]) : []
  } catch {
    return []
  }
}
