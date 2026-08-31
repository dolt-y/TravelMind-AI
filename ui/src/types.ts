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

export interface WeatherForecast {
  provider: string
  city: string
  province: string
  adcode: string
  date: string
  day_weather: string
  night_weather: string
  day_temperature: number | null
  night_temperature: number | null
  day_wind_direction: string
  night_wind_direction: string
  day_wind_power: string
  night_wind_power: string
}

export interface WeatherResponse {
  success: boolean
  message: string
  provider: string
  city: string
  cached: boolean
  data: WeatherForecast[]
}

export interface HotelLocation {
  longitude: number
  latitude: number
}

export interface Hotel {
  provider: string
  id: string
  name: string
  city: string
  address: string | null
  location: HotelLocation | null
  type: string | null
  rating: number | null
  average_price: number | null
  price_range: string | null
  tel: string | null
  photos: string[]
}

export interface HotelSearchResponse {
  success: boolean
  message: string
  provider: string
  cached: boolean
  criteria: {
    city: string
    accommodation: string
    area: string
    budget_min: number | null
    budget_max: number | null
    limit: number
  }
  data: Hotel[]
}

export interface AttractionRequest {
  city: string
  keywords: string
  language: 'zh' | 'en' | 'ja'
  note_limit: number
}
