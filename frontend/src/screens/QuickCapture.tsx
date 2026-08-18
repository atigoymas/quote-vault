import { useEffect, useState, type FormEvent } from 'react'
import { ApiError, createQuote } from '../lib/api'
import { recordView } from '../lib/recentlyViewed'
import type { Quote } from '../types'

type Status = 'idle' | 'saving' | 'saved' | 'error'

export interface SharedDraft {
  text: string
  source: string
}

interface QuickCaptureProps {
  initialDraft?: SharedDraft | null
  onDraftConsumed?: () => void
}

export function QuickCapture({ initialDraft, onDraftConsumed }: QuickCaptureProps) {
  const [text, setText] = useState(initialDraft?.text ?? '')
  const [showDetails, setShowDetails] = useState(Boolean(initialDraft?.source))
  const [author, setAuthor] = useState('')
  const [source, setSource] = useState(initialDraft?.source ?? '')
  const [status, setStatus] = useState<Status>('idle')
  const [saved, setSaved] = useState<Quote | null>(null)
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    if (initialDraft) onDraftConsumed?.()
    // consume the shared draft once, on mount — later re-mounts shouldn't reapply it
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const trimmed = text.trim()
    if (!trimmed) return
    setStatus('saving')
    try {
      const quote = await createQuote({
        text: trimmed,
        author: author.trim() || undefined,
        source: source.trim() || undefined,
      })
      recordView(quote)
      setSaved(quote)
      setStatus('saved')
    } catch (error) {
      setErrorMessage(error instanceof ApiError ? error.message : 'Could not save that quote')
      setStatus('error')
    }
  }

  function reset() {
    setText('')
    setAuthor('')
    setSource('')
    setShowDetails(false)
    setSaved(null)
    setStatus('idle')
  }

  if (status === 'saved' && saved) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-6 px-6 text-center">
        <p className="max-w-[34ch] font-serif text-2xl leading-snug text-ink">"{saved.text}"</p>
        {saved.tags && saved.tags.length > 0 ? (
          <div className="flex flex-wrap justify-center gap-2">
            {saved.tags.map((tag) => (
              <span
                key={tag}
                className="rounded-full bg-accent-soft px-3 py-1 text-xs text-accent"
              >
                {tag}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted">Saved — tags will follow shortly.</p>
        )}
        <button
          onClick={reset}
          type="button"
          className="mt-2 rounded-full bg-ink px-6 py-3 text-sm text-paper"
        >
          Save another
        </button>
      </div>
    )
  }

  return (
    <div className="flex flex-1 flex-col px-6 pt-14 pb-10">
      <form onSubmit={handleSubmit} className="mx-auto flex w-full max-w-md flex-1 flex-col">
        <textarea
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder="Paste or type a quote…"
          autoFocus
          rows={6}
          className="flex-1 resize-none rounded-2xl border border-line bg-white p-5 font-serif text-lg leading-relaxed text-ink outline-none focus:border-accent"
        />

        {showDetails ? (
          <div className="mt-4 space-y-3">
            <input
              value={author}
              onChange={(event) => setAuthor(event.target.value)}
              placeholder="Author"
              className="w-full rounded-xl border border-line bg-white px-4 py-3 text-sm outline-none focus:border-accent"
            />
            <input
              value={source}
              onChange={(event) => setSource(event.target.value)}
              placeholder="Source"
              className="w-full rounded-xl border border-line bg-white px-4 py-3 text-sm outline-none focus:border-accent"
            />
          </div>
        ) : (
          <button
            onClick={() => setShowDetails(true)}
            type="button"
            className="mt-3 self-start text-sm text-muted underline underline-offset-4"
          >
            add author or source
          </button>
        )}

        {status === 'error' && <p className="mt-3 text-sm text-red-700">{errorMessage}</p>}

        <button
          type="submit"
          disabled={!text.trim() || status === 'saving'}
          className="mt-6 rounded-full bg-ink py-4 text-center text-sm font-medium tracking-wide text-paper disabled:opacity-40"
        >
          {status === 'saving' ? 'Saving…' : 'Save quote'}
        </button>
      </form>
    </div>
  )
}
