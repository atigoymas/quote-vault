import { useEffect, useState } from 'react'
import { BottomNav, type Tab } from './components/BottomNav'
import { MoodSearch } from './screens/MoodSearch'
import { QuickCapture, type SharedDraft } from './screens/QuickCapture'
import { TagBrowse } from './screens/TagBrowse'

function readSharedDraft(): SharedDraft | null {
  if (window.location.pathname !== '/share-target') return null
  const params = new URLSearchParams(window.location.search)
  const text = params.get('text')?.trim() ?? ''
  const title = params.get('title')?.trim() ?? ''
  const url = params.get('url')?.trim() ?? ''
  if (!text && !title && !url) return null
  return { text, source: title || url }
}

function App() {
  const [tab, setTab] = useState<Tab>('mood')
  const [sharedDraft, setSharedDraft] = useState<SharedDraft | null>(null)

  useEffect(() => {
    const draft = readSharedDraft()
    if (draft) {
      setSharedDraft(draft)
      setTab('capture')
      window.history.replaceState(null, '', '/')
    }
  }, [])

  return (
    <div className="mx-auto flex min-h-dvh max-w-lg flex-col bg-paper">
      {tab === 'mood' && <MoodSearch onNavigateToCapture={() => setTab('capture')} />}
      {tab === 'capture' && (
        <QuickCapture initialDraft={sharedDraft} onDraftConsumed={() => setSharedDraft(null)} />
      )}
      {tab === 'tags' && <TagBrowse />}
      <BottomNav active={tab} onChange={setTab} />
    </div>
  )
}

export default App
