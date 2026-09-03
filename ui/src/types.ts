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

export interface Hotel {
  provider: string
  id: string
  name: string
  city: string
  address: string | null
  location: Location | null
  type: string | null
  rating: number | null
  average_price: number | null
  price_range: string | null
  tel: string | null
  photos: string[]
}

export interface TripPlanRequest {
  city: string
  start_date: string
  end_date: string
  transportation: 'walking' | 'driving' | 'transit'
  accommodation: string
  preferences: string[]
  free_text_input: string
  language: 'zh' | 'en' | 'ja'
  note_limit: number
  travelers: number
  total_budget: number | null
  hotel_budget_max: number | null
}

export interface TripMeal {
  type: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  name: string
  description: string
  estimated_cost: number
}

export interface RouteEndpoint {
  name: string
  address: string
  city: string
  location: Location
}

export interface RouteStep {
  instruction: string
  road: string
  distance_meters: number
  duration_seconds: number
  action: string
  polyline: Location[]
}

export interface RoutePlan {
  provider: string
  provider_route_id: string
  origin: RouteEndpoint
  destination: RouteEndpoint
  mode: 'walking' | 'driving' | 'transit'
  distance_meters: number
  duration_seconds: number
  description: string
  steps: RouteStep[]
}

export interface TripRouteSegment {
  origin_name: string
  destination_name: string
  route: RoutePlan
}

export interface TripDay {
  day_index: number
  date: string
  city: string
  is_transfer_day: boolean
  transfer_info: string
  description: string
  transportation: 'walking' | 'driving' | 'transit'
  attractions: Attraction[]
  meals: TripMeal[]
  hotel: Hotel | null
  weather: WeatherForecast | null
  routes: TripRouteSegment[]
}

export interface TripBudget {
  currency: string
  attractions: number
  hotels: number
  meals: number
  transportation: number
  total: number
  target: number | null
}

export interface TripPlan {
  plan_id: string
  cities: string[]
  start_date: string
  end_date: string
  travelers: number
  days: TripDay[]
  recommended_hotels: Hotel[]
  budget: TripBudget
  overall_suggestions: string
  warnings: string[]
  source_extraction_ids: string[]
  created_at: string
}

export interface TripCreateResponse {
  task_id: string
  status: 'submitted'
  status_url: string
  ws_url: string
  message: string
}

export interface TripTaskResponse {
  task_id: string
  status: 'submitted' | 'processing' | 'completed' | 'failed'
  stage: string
  progress: number
  message: string
  error_code: string | null
  error: string | null
  plan_id: string | null
  result: TripPlan | null
  created_at: string
  updated_at: string
}

export interface TripHistoryItem {
  plan_id: string
  cities: string[]
  start_date: string
  end_date: string
  travelers: number
  days_count: number
  created_at: string
}

export interface TripHistoryResponse {
  items: TripHistoryItem[]
}

export type XHSLoginMethod = 'cookie' | 'qrcode' | 'phone'
export type XHSLoginState = 'preparing' | 'waiting_scan' | 'waiting_confirm' | 'code_sent' | 'authenticating' | 'success' | 'expired' | 'error'

export interface XHSLoginMethodsResponse {
  methods: XHSLoginMethod[]
}

export interface XHSLoginStartResponse {
  login_id: string
  method: XHSLoginMethod
  state: XHSLoginState
  message: string
  expires_in: number
}

export interface XHSLoginStatusResponse {
  login_id: string
  method: XHSLoginMethod
  state: XHSLoginState
  message: string
  qr_url: string | null
  user_nickname: string | null
}
