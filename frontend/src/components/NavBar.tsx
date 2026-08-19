import { useRef } from 'react'
import { checkOwnerStatus } from '../lib/api'
import { setOwnerKey } from '../lib/ownerKey'

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

// Tap "Tags" 5 times quickly to paste in the owner access key — no URL or
// link ever carries the secret, avoiding it lingering in browser history.
const UNLOCK_TAP_COUNT = 5
const UNLOCK_TAP_WINDOW_MS = 2000

function now(): number {
  return Date.now()
}

export function NavBar({ active, onChange }: NavBarProps) {
  const tapTimestamps = useRef<number[]>([])

  function registerSecretTap() {
    const timestamp = now()
    const recent = [...tapTimestamps.current, timestamp].filter(
      (t) => timestamp - t < UNLOCK_TAP_WINDOW_MS,
    )
    tapTimestamps.current = recent
    if (recent.length < UNLOCK_TAP_COUNT) return

    tapTimestamps.current = []
    const key = window.prompt('Owner access key:')
    if (!key?.trim()) return

    setOwnerKey(key.trim())
    checkOwnerStatus()
      .then(({ is_owner }) => {
        window.alert(is_owner ? 'Owner key accepted.' : "That key didn't match — try again.")
      })
      .catch(() => window.alert('Could not verify the key — check your connection and retry.'))
  }

  return (
    <nav
      className="sticky top-0 z-10 flex justify-around border-b border-line bg-paper/95 backdrop-blur"
      style={{ paddingTop: 'env(safe-area-inset-top)' }}
    >
      {TABS.map((tab) => (
        <button
          key={tab.id}
          onClick={() => {
            onChange(tab.id)
            if (tab.id === 'tags') registerSecretTap()
          }}
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
