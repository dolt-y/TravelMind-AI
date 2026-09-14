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

/** 按页读取已完成的行程摘要，分页总数以服务端持久化数据为准。 */
export async function getTripHistory(page = 1, pageSize = 6): Promise<TripHistoryResponse> {
  const { data } = await http.get<TripHistoryResponse>('/trip/history', {
    params: { page, page_size: pageSize },
  })
  return data
}

/** 按计划 ID 恢复完整行程，进入结果页前替换当前查看内容。 */
export async function getTripPlan(planId: string): Promise<TripPlan> {
  const { data } = await http.get<TripPlan>(`/trip/plan/${planId}`)
  return data
}
