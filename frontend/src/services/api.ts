import type { ChatResponse, SourceItem, UploadResponse } from '../types'

const BASE_URL = 'http://127.0.0.1:8000'

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  let response: Response

  try {
    response = await fetch(`${BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    })
  } catch {
    throw new Error(
      'Cannot reach backend at http://127.0.0.1:8000. Make sure the FastAPI server is running.',
    )
  }

  if (!response.ok) {
    throw new Error(await extractErrorMessage(response, 'Upload failed.'))
  }

  return response.json() as Promise<UploadResponse>
}

export async function sendChatMessage(message: string): Promise<ChatResponse> {
  let response: Response

  try {
    response = await fetch(`${BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    })
  } catch {
    throw new Error(
      'Cannot reach backend at http://127.0.0.1:8000. Make sure the FastAPI server is running.',
    )
  }

  if (!response.ok) {
    throw new Error(await extractErrorMessage(response, 'Chat request failed.'))
  }

  const data = (await response.json()) as {
    answer: string
    sources?: Array<{
      source: string
      chunk_id: string | number
      score?: number
      similarity?: number
      preview?: string
      text_preview?: string
    }>
  }

  return {
    answer: data.answer,
    sources: (data.sources ?? []).map(normalizeSource),
  }
}

function normalizeSource(source: {
  source: string
  chunk_id: string | number
  score?: number
  similarity?: number
  preview?: string
  text_preview?: string
}): SourceItem {
  return {
    source: source.source,
    chunk_id: String(source.chunk_id),
    score: source.score ?? source.similarity ?? 0,
    preview: source.preview ?? source.text_preview ?? '',
  }
}

async function extractErrorMessage(response: Response, fallback: string): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: string }
    return data.detail || fallback
  } catch {
    return fallback
  }
}
