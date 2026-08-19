import { supportsReadAloud, useReadAloud } from '../lib/useReadAloud'

interface QuoteDisplayProps {
  text: string
  author?: string | null
  source?: string | null
  tags?: string[] | null
  size?: 'lg' | 'md'
}

function SpeakerIcon({ active }: { active: boolean }) {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <polygon points="3 9 3 15 8 15 13 20 13 4 8 9 3 9" />
      {active && <path d="M17 8a5 5 0 0 1 0 8" />}
      {active && <path d="M19.5 5.5a9 9 0 0 1 0 13" />}
    </svg>
  )
}

export function QuoteDisplay({ text, author, source, tags, size = 'lg' }: QuoteDisplayProps) {
  const attribution = [author, source].filter(Boolean).join(', ')
  const { speaking, toggle } = useReadAloud(author ? `${text} — ${author}` : text)

  return (
    <div className="mx-auto max-w-[36ch] text-center">
      <p
        className={
          size === 'lg'
            ? 'font-serif text-[1.65rem] leading-[1.5] text-ink'
            : 'font-serif text-xl leading-[1.55] text-ink'
        }
      >
        {text}
      </p>
      {attribution && (
        <p className="mt-4 text-sm tracking-wide text-muted uppercase">{attribution}</p>
      )}
      {supportsReadAloud && (
        <button
          onClick={toggle}
          type="button"
          aria-label={speaking ? 'Stop reading aloud' : 'Read aloud'}
          className="mt-3 inline-flex items-center gap-1.5 text-xs text-muted hover:text-accent"
        >
          <SpeakerIcon active={speaking} />
          {speaking ? 'stop' : 'listen'}
        </button>
      )}
      {tags && tags.length > 0 && (
        <div className="mt-4 flex flex-wrap justify-center gap-2">
          {tags.map((tag) => (
            <span key={tag} className="text-xs text-muted">
              #{tag}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
