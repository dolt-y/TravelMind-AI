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

export type ExportLanguage = 'zh' | 'en' | 'ja'

export async function exportTripPlanPdf(planId: string, language: ExportLanguage): Promise<string> {
  // 后端会下载并内嵌景点图片，给导出单独放宽超时。
  const response = await http.get<Blob>(`/trip/plan/${planId}/export.pdf`, {
    params: { language },
    responseType: 'blob',
    timeout: 90_000,
  })
  const filename = resolveFilename(
    response.headers['content-disposition'],
    `TravelMind-${planId}.pdf`,
  )
  saveBlob(response.data, filename)
  return filename
}

function resolveFilename(disposition: unknown, fallback: string): string {
  if (typeof disposition !== 'string') return fallback
  const encoded = /filename\*=UTF-8''([^;]+)/i.exec(disposition)
  if (encoded?.[1]) {
    try {
      return decodeURIComponent(encoded[1])
    } catch {
      return fallback
    }
  }
  return /filename="?([^";]+)"?/i.exec(disposition)?.[1] ?? fallback
}

function saveBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.append(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}
