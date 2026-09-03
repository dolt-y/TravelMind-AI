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

/** 读取最近完成的行程摘要，供“我的行程”列表展示。 */
export async function getTripHistory(limit = 20): Promise<TripHistoryResponse> {
  const { data } = await http.get<TripHistoryResponse>('/trip/history', { params: { limit } })
  return data
}

/** 按计划 ID 恢复完整行程，进入结果页前替换当前查看内容。 */
export async function getTripPlan(planId: string): Promise<TripPlan> {
  const { data } = await http.get<TripPlan>(`/trip/plan/${planId}`)
  return data
}
