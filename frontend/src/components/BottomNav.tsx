export type Tab = 'mood' | 'capture' | 'tags'

interface BottomNavProps {
  active: Tab
  onChange: (tab: Tab) => void
}

const TABS: { id: Tab; label: string }[] = [
  { id: 'mood', label: 'Mood' },
  { id: 'capture', label: 'Save' },
  { id: 'tags', label: 'Tags' },
]

export function BottomNav({ active, onChange }: BottomNavProps) {
  return (
    <nav
      className="sticky bottom-0 flex justify-around border-t border-line bg-paper/95 backdrop-blur"
      style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}
    >
      {TABS.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          type="button"
          className={`flex-1 py-4 text-sm tracking-wide transition-colors ${
            active === tab.id ? 'text-accent' : 'text-muted'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  )
}
