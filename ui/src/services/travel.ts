import type {
  AttractionRequest,
  AttractionResponse,
  HotelSearchResponse,
  WeatherResponse,
} from '../types'
import { http } from './http'

export async function extractAttractions(request: AttractionRequest): Promise<AttractionResponse> {
  const { data } = await http.post<AttractionResponse>('/xhs/attractions', request)
  return data
}

export async function getWeather(city: string): Promise<WeatherResponse> {
  const { data } = await http.get<WeatherResponse>('/weather', { params: { city } })
  return data
}

export async function searchHotels(city: string): Promise<HotelSearchResponse> {
  const { data } = await http.get<HotelSearchResponse>('/hotels/search', {
    params: { city, limit: 6 },
  })
  return data
}
