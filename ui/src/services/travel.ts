import type {
  TripCreateResponse,
  TripHistoryResponse,
  TripPlan,
  TripPlanRequest,
  TripTaskResponse,
} from '../types'
import { http } from './http'

export async function createTripPlan(request: TripPlanRequest): Promise<TripCreateResponse> {
  const { data } = await http.post<TripCreateResponse>('/trip/plan', request)
  return data
}

export async function getTripStatus(taskId: string): Promise<TripTaskResponse> {
  const { data } = await http.get<TripTaskResponse>(`/trip/status/${taskId}`)
  return data
}

export async function getTripHistory(page = 1, pageSize = 6): Promise<TripHistoryResponse> {
  const { data } = await http.get<TripHistoryResponse>('/trip/history', {
    params: { page, page_size: pageSize },
  })
  return data
}

export async function getTripPlan(planId: string): Promise<TripPlan> {
  const { data } = await http.get<TripPlan>(`/trip/plan/${planId}`)
  return data
}
