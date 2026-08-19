import { useEffect, useState } from 'react'

export const supportsReadAloud =
  typeof window !== 'undefined' && 'speechSynthesis' in window

export function useReadAloud(utteranceText: string) {
  const [speaking, setSpeaking] = useState(false)

  useEffect(() => {
    return () => {
      if (supportsReadAloud) window.speechSynthesis.cancel()
    }
  }, [])

  function toggle() {
    if (!supportsReadAloud) return
    if (speaking) {
      window.speechSynthesis.cancel()
      setSpeaking(false)
      return
    }
    const utterance = new SpeechSynthesisUtterance(utteranceText)
    utterance.onend = () => setSpeaking(false)
    utterance.onerror = () => setSpeaking(false)
    window.speechSynthesis.cancel()
    window.speechSynthesis.speak(utterance)
    setSpeaking(true)
  }

  return { speaking, toggle }
}
