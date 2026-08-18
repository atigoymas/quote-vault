interface QuoteDisplayProps {
  text: string
  author?: string | null
  source?: string | null
  tags?: string[] | null
  size?: 'lg' | 'md'
}

export function QuoteDisplay({ text, author, source, tags, size = 'lg' }: QuoteDisplayProps) {
  const attribution = [author, source].filter(Boolean).join(', ')

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
