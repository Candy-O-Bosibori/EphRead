import { useState, useRef } from 'react'

export default function UploadPage({ onUpload }) {
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null) // { doc_id, chunk_count, filename }
  const inputRef = useRef(null)

  async function uploadFile(file) {
    if (!file) return
    if (!file.name.endsWith('.pdf')) {
      setError('Only PDF files are accepted.')
      return
    }
    setError('')
    setLoading(true)
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await fetch('/api/upload', { method: 'POST', body: form })
      const data = await res.json()
      if (!res.ok) {
        setError(data.detail || 'Upload failed.')
        return
      }
      setResult({ doc_id: data.doc_id, chunk_count: data.chunk_count, filename: file.name })
    } catch {
      setError('Could not reach the server. Is it running?')
    } finally {
      setLoading(false)
    }
  }

  function handleDrop(e) {
    e.preventDefault()
    setDragging(false)
    uploadFile(e.dataTransfer.files[0])
  }

  return (
    <div className="min-h-screen bg-white dark:bg-brand-dark-bg flex flex-col">
      {/* Nav bar */}
      <nav className="bg-brand-purple px-6 py-4 flex items-center justify-between shadow-purple-md">
        <span className="text-white text-xl font-bold tracking-tight">RAG Chat</span>
        <span className="text-brand-gold text-sm font-medium">Powered by Claude</span>
      </nav>

      {/* Main */}
      <main className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-lg">
          {/* Card */}
          <div className="bg-white dark:bg-brand-dark-card rounded-2xl shadow-purple-md p-8 border border-purple-100 dark:border-brand-purple">
            <h1 className="text-2xl font-bold text-brand-purple dark:text-brand-gold mb-1">
              Upload a PDF
            </h1>
            <p className="text-gray-500 dark:text-gray-400 text-sm mb-6">
              Your document will be chunked, embedded, and stored — then you can chat with it.
            </p>

            {!result ? (
              <>
                {/* Drop zone */}
                <div
                  onClick={() => inputRef.current?.click()}
                  onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
                  onDragLeave={() => setDragging(false)}
                  onDrop={handleDrop}
                  className={`
                    cursor-pointer border-2 border-dashed rounded-xl p-10
                    flex flex-col items-center justify-center gap-3
                    transition-all duration-200
                    ${dragging
                      ? 'border-brand-gold bg-yellow-50 dark:bg-yellow-900/10 shadow-gold-glow'
                      : 'border-brand-purple/40 hover:border-brand-purple bg-purple-50/40 dark:bg-brand-purple/10'
                    }
                  `}
                >
                  <svg className={`w-10 h-10 ${dragging ? 'text-brand-gold' : 'text-brand-purple/60'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                      d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="text-brand-purple dark:text-gray-300 font-medium text-sm text-center">
                    {loading ? 'Uploading…' : 'Drop your PDF here, or click to browse'}
                  </p>
                  <p className="text-xs text-gray-400">PDF files only</p>
                </div>
                <input
                  ref={inputRef}
                  type="file"
                  accept=".pdf"
                  className="hidden"
                  onChange={(e) => uploadFile(e.target.files[0])}
                />

                {/* Error */}
                {error && (
                  <p className="mt-4 text-sm text-red-500 text-center">{error}</p>
                )}
              </>
            ) : (
              /* Success state */
              <div className="text-center">
                <div className="w-14 h-14 bg-brand-purple/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-7 h-7 text-brand-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <p className="font-semibold text-gray-800 dark:text-white">{result.filename}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  {result.chunk_count} chunks stored · doc #{result.doc_id}
                </p>
                <button
                  onClick={() => onUpload(result.doc_id, result.filename)}
                  className="mt-6 w-full bg-brand-gold hover:bg-brand-gold-light text-black font-semibold py-3 px-6 rounded-full shadow-gold-glow transition-all duration-200"
                >
                  Start chatting →
                </button>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
