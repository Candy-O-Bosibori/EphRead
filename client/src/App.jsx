import { useState, useEffect } from 'react'
import UploadPage from './components/UploadPage'

// Dark mode: persisted in localStorage, applied via 'dark' class on <html>
function useDarkMode() {
  const [dark, setDark] = useState(() => localStorage.getItem('darkMode') === 'true')
  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem('darkMode', dark)
  }, [dark])
  return [dark, setDark]
}

export default function App() {
  const [dark, setDark] = useDarkMode()
  const [docId, setDocId] = useState(null)
  const [filename, setFilename] = useState('')

  function handleUpload(id, name) {
    setDocId(id)
    setFilename(name)
  }

  // Dark mode toggle button — visible on every screen
  const DarkToggle = (
    <button
      onClick={() => setDark(d => !d)}
      className="fixed bottom-4 right-4 z-50 bg-brand-purple dark:bg-brand-gold text-white dark:text-black w-10 h-10 rounded-full shadow-purple-md flex items-center justify-center text-lg transition-all"
      title="Toggle dark mode"
    >
      {dark ? '☀️' : '🌙'}
    </button>
  )

  if (!docId) {
    return (
      <>
        <UploadPage onUpload={handleUpload} />
        {DarkToggle}
      </>
    )
  }

  // Placeholder — ChatWindow comes in 7c
  return (
    <div className="min-h-screen bg-white dark:bg-brand-dark-bg flex flex-col">
      <nav className="bg-brand-purple px-6 py-4 flex items-center justify-between shadow-purple-md">
        <span className="text-white text-xl font-bold tracking-tight">RAG Chat</span>
        <button
          onClick={() => { setDocId(null); setFilename('') }}
          className="text-brand-gold text-sm font-medium hover:underline"
        >
          ← Upload new
        </button>
      </nav>
      <main className="flex-1 flex items-center justify-center">
        <p className="text-brand-purple dark:text-brand-gold font-semibold text-lg">
          Chat coming in 7c — doc #{docId} ({filename}) ready
        </p>
      </main>
      {DarkToggle}
    </div>
  )
}
