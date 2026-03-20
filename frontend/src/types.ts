export type UploadResponse = {
  filename: string
  chunks: number
  output: string
}

export type SourceItem = {
  source: string
  chunk_id: string
  score: number
  preview: string
}

export type ChatResponse = {
  answer: string
  sources: SourceItem[]
}
