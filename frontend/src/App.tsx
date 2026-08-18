import { useState } from 'react'
import { BottomNav, type Tab } from './components/BottomNav'
import { MoodSearch } from './screens/MoodSearch'
import { QuickCapture } from './screens/QuickCapture'
import { TagBrowse } from './screens/TagBrowse'

function App() {
  const [tab, setTab] = useState<Tab>('mood')

  return (
    <div className="mx-auto flex min-h-dvh max-w-lg flex-col bg-paper">
      {tab === 'mood' && <MoodSearch onNavigateToCapture={() => setTab('capture')} />}
      {tab === 'capture' && <QuickCapture />}
      {tab === 'tags' && <TagBrowse />}
      <BottomNav active={tab} onChange={setTab} />
    </div>
  )
}

export default App
