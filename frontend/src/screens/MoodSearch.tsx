import { useRef, useState, type FormEvent } from 'react'
import { QuoteDisplay } from '../components/QuoteDisplay'
import { ApiError, searchMood } from '../lib/api'
import { getRecentlyViewed, recordView, type ViewedQuote } from '../lib/recentlyViewed'
import type { MoodSearchResult } from '../types'

const SUGGESTIONS = ['overwhelmed', 'hopeful', 'restless', 'grateful']

const RANDOM_FEELINGS = [
  'overwhelmed',
  'hopeful',
  'restless',
  'grateful',
  'anxious',
  'motivated',
  'lonely',
  'inspired',
  'nostalgic',
  'uncertain',
  'proud',
  'exhausted',
  'curious',
  'content',
  'frustrated',
  'adventurous',
  'calm',
  'stuck',
  'excited',
  'melancholy',
  'determined',
  'vulnerable',
  'joyful',
  'conflicted',
  'peaceful',
  'homesick',
  'empowered',
  'reflective',
]

function pickRandomFeeling(): string {
  return RANDOM_FEELINGS[Math.floor(Math.random() * RANDOM_FEELINGS.length)]
}

type Status = 'idle' | 'loading' | 'result' | 'empty' | 'error' | 'offline'

interface MoodSearchProps {
  onNavigateToCapture: () => void
}

export function MoodSearch({ onNavigateToCapture }: MoodSearchProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [feeling, setFeeling] = useState('')
  const [isFocused, setIsFocused] = useState(false)
  const [result, setResult] = useState<MoodSearchResult | null>(null)
  const [offlineQuote, setOfflineQuote] = useState<ViewedQuote | null>(null)
  const [status, setStatus] = useState<Status>('idle')
  const [errorMessage, setErrorMessage] = useState('')

  async function runSearch(value: string) {
    const trimmed = value.trim()
    if (!trimmed) return
    inputRef.current?.blur()

    if (!navigator.onLine) {
      const recent = getRecentlyViewed()
      setOfflineQuote(recent[0] ?? null)
      setStatus('offline')
      return
    }

    setStatus('loading')
    try {
      const match = await searchMood(trimmed)
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
    void runSearch(feeling)
  }

  function handleSuggestion(word: string) {
    setFeeling(word)
    void runSearch(word)
  }

  function handleSurpriseMe() {
    const word = pickRandomFeeling()
    setFeeling(word)
    void runSearch(word)
  }

  return (
    <div className="flex flex-1 flex-col px-6 pt-8 pb-10">
      <form onSubmit={handleSubmit} className="mx-auto w-full max-w-md">
        <label htmlFor="feeling" className="block text-center text-sm text-muted">
          How are you feeling?
        </label>
        <input
          id="feeling"
          ref={inputRef}
          value={feeling}
          onChange={(event) => setFeeling(event.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="restless, hopeful, undone…"
          className="mt-3 w-full rounded-full border border-line bg-white px-6 py-4 text-center font-serif text-lg text-ink shadow-sm outline-none focus:border-accent"
        />
      </form>

      <div
        className={`mt-12 flex flex-1 flex-col items-center justify-center ${isFocused ? 'invisible' : ''}`}
      >
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
            <button
              onClick={handleSurpriseMe}
              type="button"
              className="mt-4 text-sm text-muted underline underline-offset-4"
            >
              not sure? surprise me
            </button>
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
