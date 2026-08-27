export interface Location {
  longitude: number
  latitude: number
}

export interface Attraction {
  name: string
  name_zh: string
  name_en: string
  reason: string
  duration: number
  reservation_required: boolean
  reservation_tips: string
  poi_id: string
  address: string
  location: Location | null
  rating: number | null
  photos: string[]
}

export interface AttractionResponse {
  extraction_id: string
  city: string
  keywords: string
  notes_count: number
  attractions: Attraction[]
}

export interface HealthResponse {
  configured: boolean
  vendor_present: boolean
  mode: string
}

export interface AttractionRequest {
  city: string
  keywords: string
  language: 'zh' | 'en' | 'ja'
  note_limit: number
}
