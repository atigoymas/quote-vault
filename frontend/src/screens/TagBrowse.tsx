import { useEffect, useState } from 'react'
import { QuoteDisplay } from '../components/QuoteDisplay'
import { listQuotes, listTags } from '../lib/api'
import { recordView } from '../lib/recentlyViewed'
import { groupTagsByCategory } from '../lib/tagCategories'
import type { Quote, TagCount } from '../types'

export function TagBrowse() {
  const [tags, setTags] = useState<TagCount[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [quotes, setQuotes] = useState<Quote[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listTags()
      .then(setTags)
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!selected) return
    listQuotes(selected).then((fetched) => {
      setQuotes(fetched)
      fetched.forEach(recordView)
    })
  }, [selected])

  const grouped = groupTagsByCategory(tags)

  if (selected) {
    return (
      <div className="flex-1 px-6 pt-14 pb-10">
        <button
          onClick={() => setSelected(null)}
          type="button"
          className="text-sm text-muted underline underline-offset-4"
        >
          ← all tags
        </button>
        <p className="mt-4 text-center text-xs tracking-wide text-accent uppercase">{selected}</p>
        <div className="mt-8 divide-y divide-line">
          {quotes.map((quote) => (
            <div key={quote.id} className="py-8 first:pt-0">
              <QuoteDisplay
                text={quote.text}
                author={quote.author}
                source={quote.source}
                size="md"
              />
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 px-6 pt-14 pb-10">
      <p className="text-center text-sm text-muted">tags</p>
      {loading ? (
        <p className="mt-8 text-center text-sm text-muted">loading…</p>
      ) : tags.length === 0 ? (
        <p className="mt-8 text-center text-sm text-muted">
          No tags yet — save a few quotes first.
        </p>
      ) : (
        <div className="mx-auto mt-8 max-w-md space-y-8">
          {grouped.map(({ label, items }) => {
            const maxCount = Math.max(1, ...items.map((t) => t.count))
            return (
              <div key={label}>
                <p className="text-center text-xs tracking-wide text-muted uppercase">{label}</p>
                <div className="mt-3 flex flex-wrap justify-center gap-x-4 gap-y-3">
                  {items.map(({ tag, count }) => {
                    const scale = 0.85 + (count / maxCount) * 0.5
                    return (
                      <button
                        key={tag}
                        onClick={() => setSelected(tag)}
                        type="button"
                        className="font-serif text-ink transition-opacity hover:opacity-70"
                        style={{ fontSize: `${scale}rem` }}
                      >
                        {tag}
                        <span className="ml-1 align-super text-xs text-muted">{count}</span>
                      </button>
                    )
                  })}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
