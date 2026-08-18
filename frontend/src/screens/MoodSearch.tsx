import { useEffect, useState, type FormEvent } from 'react'
import { QuoteDisplay } from '../components/QuoteDisplay'
import { ApiError, listTags, searchMood } from '../lib/api'
import { getRecentlyViewed, recordView, type ViewedQuote } from '../lib/recentlyViewed'
import type { MoodSearchResult, TagCount } from '../types'

const SUGGESTIONS = ['overwhelmed', 'hopeful', 'restless', 'grateful']

type Status = 'idle' | 'loading' | 'result' | 'empty' | 'error' | 'offline'

interface MoodSearchProps {
  onNavigateToCapture: () => void
}

export function MoodSearch({ onNavigateToCapture }: MoodSearchProps) {
  const [feeling, setFeeling] = useState('')
  const [tags, setTags] = useState<TagCount[]>([])
  const [activeTag, setActiveTag] = useState<string | null>(null)
  const [result, setResult] = useState<MoodSearchResult | null>(null)
  const [offlineQuote, setOfflineQuote] = useState<ViewedQuote | null>(null)
  const [status, setStatus] = useState<Status>('idle')
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    listTags()
      .then(setTags)
      .catch(() => setTags([]))
  }, [])

  async function runSearch(value: string, tag: string | null) {
    const trimmed = value.trim()
    if (!trimmed) return

    if (!navigator.onLine) {
      const recent = getRecentlyViewed()
      setOfflineQuote(recent[0] ?? null)
      setStatus('offline')
      return
    }

    setStatus('loading')
    try {
      const match = await searchMood(trimmed, tag ?? undefined)
      recordView(match)
      setResult(match)
      setStatus('result')
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) {
        setStatus('empty')
      } else {
        setErrorMessage(error instanceof Error ? error.message : 'Something went wrong')
        setStatus('error')
      }
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    void runSearch(feeling, activeTag)
  }

  function handleSuggestion(word: string) {
    setFeeling(word)
    void runSearch(word, activeTag)
  }

  function toggleTag(tag: string) {
    const next = activeTag === tag ? null : tag
    setActiveTag(next)
    if (feeling.trim()) void runSearch(feeling, next)
  }

  return (
    <div className="flex flex-1 flex-col px-6 pt-14 pb-10">
      <form onSubmit={handleSubmit} className="mx-auto w-full max-w-md">
        <label htmlFor="feeling" className="block text-center text-sm text-muted">
          How are you feeling?
        </label>
        <input
          id="feeling"
          value={feeling}
          onChange={(event) => setFeeling(event.target.value)}
          placeholder="restless, hopeful, undone…"
          autoFocus
          className="mt-3 w-full rounded-full border border-line bg-white px-6 py-4 text-center font-serif text-lg text-ink shadow-sm outline-none focus:border-accent"
        />
      </form>

      {tags.length > 0 && (
        <div className="mx-auto mt-4 flex max-w-md flex-wrap justify-center gap-x-3 gap-y-1">
          {tags.slice(0, 8).map(({ tag }) => (
            <button
              key={tag}
              onClick={() => toggleTag(tag)}
              type="button"
              className={`text-xs tracking-wide uppercase ${
                activeTag === tag ? 'text-accent' : 'text-muted'
              }`}
            >
              {tag}
            </button>
          ))}
        </div>
      )}

      <div className="mt-12 flex flex-1 flex-col items-center justify-center">
        {status === 'idle' && (
          <div className="text-center">
            <p className="text-sm text-muted">or try</p>
            <div className="mt-3 flex flex-wrap justify-center gap-2">
              {SUGGESTIONS.map((word) => (
                <button
                  key={word}
                  onClick={() => handleSuggestion(word)}
                  type="button"
                  className="rounded-full bg-accent-soft px-4 py-2 text-sm text-accent"
                >
                  {word}
                </button>
              ))}
            </div>
          </div>
        )}

        {status === 'loading' && <p className="text-sm text-muted">searching…</p>}

        {status === 'empty' && (
          <div className="text-center">
            <p className="text-sm text-muted">Nothing saved yet.</p>
            <button
              onClick={onNavigateToCapture}
              type="button"
              className="mt-3 text-sm text-accent underline underline-offset-4"
            >
              Save your first quote
            </button>
          </div>
        )}

        {status === 'error' && <p className="text-sm text-muted">{errorMessage}</p>}

        {status === 'offline' && (
          <div className="text-center">
            <p className="text-sm text-muted">
              You're offline — mood search needs a connection.
            </p>
            {offlineQuote ? (
              <div className="mt-6">
                <QuoteDisplay
                  text={offlineQuote.text}
                  author={offlineQuote.author}
                  source={offlineQuote.source}
                  tags={offlineQuote.tags}
                />
                <p className="mt-4 text-xs text-muted">from your recently viewed quotes</p>
              </div>
            ) : (
              <p className="mt-3 text-xs text-muted">
                Nothing cached yet for offline reading — view a few quotes while online first.
              </p>
            )}
          </div>
        )}

        {status === 'result' && result && (
          <div>
            <QuoteDisplay
              text={result.text}
              author={result.author}
              source={result.source}
              tags={result.tags}
            />
            {result.explanation && (
              <p className="mx-auto mt-6 max-w-[34ch] text-center text-sm text-ink-soft italic">
                {result.explanation}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
