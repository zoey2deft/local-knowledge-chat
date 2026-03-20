import { useState } from 'react'
import type { FormEvent } from 'react'
import './App.css'
import { sendChatMessage, uploadDocument } from './services/api'
import type { ChatResponse } from './types'

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadMessage, setUploadMessage] = useState<string | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)

  const [message, setMessage] = useState('')
  const [chatResult, setChatResult] = useState<ChatResponse | null>(null)
  const [chatError, setChatError] = useState<string | null>(null)
  const [isChatting, setIsChatting] = useState(false)

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!selectedFile) {
      setUploadError('Select a .txt file before uploading.')
      setUploadMessage(null)
      return
    }

    setIsUploading(true)
    setUploadError(null)
    setUploadMessage(null)

    try {
      const result = await uploadDocument(selectedFile)
      setUploadMessage(`Uploaded ${result.filename} with ${result.chunks} chunks.`)
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : 'Upload failed.')
    } finally {
      setIsUploading(false)
    }
  }

  async function handleChatSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const trimmedMessage = message.trim()
    if (!trimmedMessage) {
      setChatError('Enter a question before sending.')
      return
    }

    setIsChatting(true)
    setChatError(null)

    try {
      const response = await sendChatMessage(trimmedMessage)
      setChatResult(response)
    } catch (error) {
      setChatError(error instanceof Error ? error.message : 'Chat request failed.')
    } finally {
      setIsChatting(false)
    }
  }

  return (
    <main className="app-shell">
      <header className="page-header">
        <p className="eyebrow">Local Knowledge Chat</p>
        <h1>Upload notes and ask questions</h1>
        <p className="intro">
          Send text files to the backend, then query your local knowledge base.
        </p>
      </header>

      <section className="panel">
        <div className="section-heading">
          <h2>Upload .txt file</h2>
          <p>POSTs to `/upload` on the FastAPI backend.</p>
        </div>

        <form className="stack" onSubmit={handleUpload}>
          <input
            accept=".txt"
            type="file"
            onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
          />
          <button disabled={isUploading} type="submit">
            {isUploading ? 'Uploading...' : 'Upload'}
          </button>
        </form>

        {uploadMessage ? <p className="status success">{uploadMessage}</p> : null}
        {uploadError ? <p className="status error">{uploadError}</p> : null}
      </section>

      <section className="panel">
        <div className="section-heading">
          <h2>Chat</h2>
          <p>Ask a question and review the retrieved sources.</p>
        </div>

        <form className="chat-form" onSubmit={handleChatSubmit}>
          <textarea
            placeholder="Ask something about your uploaded documents..."
            rows={4}
            value={message}
            onChange={(event) => setMessage(event.target.value)}
          />
          <button disabled={isChatting} type="submit">
            {isChatting ? 'Thinking...' : 'Send'}
          </button>
        </form>

        {chatError ? <p className="status error">{chatError}</p> : null}

        <div className="result-block">
          <h3>Answer</h3>
          <div className="result-card">
            {chatResult?.answer ?? 'Your answer will appear here after you send a message.'}
          </div>
        </div>

        <div className="result-block">
          <h3>Sources</h3>
          {chatResult?.sources.length ? (
            <div className="sources-list">
              {chatResult.sources.map((source, index) => (
                <article className="source-card" key={`${source.source}-${source.chunk_id}-${index}`}>
                  <p className="source-row">
                    <strong>Source:</strong> <span>{source.source}</span>
                  </p>
                  <p className="source-row">
                    <strong>Chunk ID:</strong> <span>{source.chunk_id}</span>
                  </p>
                  <p className="source-row">
                    <strong>Score:</strong> <span>{source.score.toFixed(4)}</span>
                  </p>
                  <p className="source-preview">{source.preview}</p>
                </article>
              ))}
            </div>
          ) : (
            <div className="result-card">No sources yet.</div>
          )}
        </div>
      </section>
    </main>
  )
}

export default App
