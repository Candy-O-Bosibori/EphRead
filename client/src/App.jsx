import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import UploadPage from './components/UploadPage'
import ChatWindow from './components/ChatWindow'

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
  const [docs, setDocs] = useState([])
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const [docId, setDocId] = useState(() => {
    const saved = localStorage.getItem('docId')
    return saved ? Number(saved) : null
  })
  const [filename, setFilename] = useState(
    () => localStorage.getItem('docFilename') || ''
  )
  const [view, setView] = useState(() =>
    localStorage.getItem('docId') ? 'chat' : 'upload'
  )

  function refreshDocs() {
    fetch('/api/documents')
      .then(r => r.ok ? r.json() : Promise.reject(new Error(`${r.status}`)))
      .then(docs => Array.isArray(docs) ? setDocs(docs) : setDocs([]))
      .catch(() => setDocs([]))
  }

  useEffect(() => { refreshDocs() }, [])

  function openDoc(id, name) {
    setDocId(id)
    setFilename(name)
    setView('chat')
    localStorage.setItem('docId', id)
    localStorage.setItem('docFilename', name)
    refreshDocs()
    setSidebarOpen(false)
  }

  function newChat() {
    setDocId(null)
    setFilename('')
    setView('upload')
    localStorage.removeItem('docId')
    localStorage.removeItem('docFilename')
    setSidebarOpen(false)
  }

  function selectDoc(id, name) {
    setDocId(id)
    setFilename(name)
    setView('chat')
    localStorage.setItem('docId', id)
    localStorage.setItem('docFilename', name)
    setSidebarOpen(false)
  }

  async function deleteDoc(id) {
    await fetch(`/api/documents/${id}`, { method: 'DELETE' })
    refreshDocs()
    if (id === docId) {
      setDocId(null)
      setFilename('')
      setView('upload')
      localStorage.removeItem('docId')
      localStorage.removeItem('docFilename')
    }
  }

  return (
    <div className="flex h-screen bg-white dark:bg-brand-dark-bg overflow-hidden">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/50 z-20"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <Sidebar
        docs={docs}
        activeDocId={docId}
        onNewChat={newChat}
        onSelectDoc={selectDoc}
        onDeleteDoc={deleteDoc}
        dark={dark}
        onToggleDark={() => setDark(d => !d)}
        open={sidebarOpen}
      />

      {/* Main area */}
      <div className="flex-1 min-w-0 flex flex-col overflow-hidden relative">
        {/* Mobile hamburger */}
        <button
          className="md:hidden absolute top-3 left-3 z-10 bg-brand-purple text-white w-8 h-8 rounded-lg flex items-center justify-center shadow-purple-sm"
          onClick={() => setSidebarOpen(true)}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        {view === 'chat' && docId ? (
          <ChatWindow docId={docId} filename={filename} />
        ) : (
          <UploadPage onUpload={openDoc} />
        )}
      </div>
    </div>
  )
}
