export type Tab = 'mood' | 'capture' | 'tags'

interface NavBarProps {
  active: Tab
  onChange: (tab: Tab) => void
}

const TABS: { id: Tab; label: string }[] = [
  { id: 'mood', label: 'Mood' },
  { id: 'capture', label: 'Save' },
  { id: 'tags', label: 'Tags' },
]

export function NavBar({ active, onChange }: NavBarProps) {
  return (
    <nav
      className="sticky top-0 z-10 flex justify-around border-b border-line bg-paper/95 backdrop-blur"
      style={{ paddingTop: 'env(safe-area-inset-top)' }}
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
