export interface Quote {
  id: number
  text: string
  source: string | null
  author: string | null
  tags: string[] | null
  created_at: string
}

export interface SearchResult {
  id: number
  text: string
  source: string | null
  author: string | null
  tags: string[] | null
  similarity: number
}

export interface MoodSearchResult extends SearchResult {
  explanation: string | null
}

export interface TagCount {
  tag: string
  count: number
}
