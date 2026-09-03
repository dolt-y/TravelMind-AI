import axios from 'axios'

interface ApiErrorDetail {
  code?: string
  message?: string
}

interface ApiErrorPayload {
  detail?: string | { msg?: string }[] | ApiErrorDetail
  message?: string
}

export class ApiError extends Error {
  readonly code?: string
  readonly status?: number

  constructor(message: string, code?: string, status?: number) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
  }
}

export const http = axios.create({
  baseURL: '/api',
  // 规划任务提交和状态查询均为轻量请求，耗时工作由服务端后台执行。
  timeout: 30_000,
  headers: { 'Content-Type': 'application/json' },
})

http.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (!axios.isAxiosError<ApiErrorPayload>(error)) {
      return Promise.reject(error)
    }

    const detail = error.response?.data?.detail
    const validationMessage = Array.isArray(detail)
      ? detail.map((item) => item.msg).filter(Boolean).join('；')
      : undefined
    const businessDetail = detail && typeof detail === 'object' && !Array.isArray(detail)
      ? detail
      : undefined
    const message = validationMessage
      || (typeof detail === 'string' ? detail : undefined)
      || businessDetail?.message
      || error.response?.data?.message
      || (error.code === 'ECONNABORTED' ? '请求处理超时，请稍后重试' : error.message)

    return Promise.reject(new ApiError(
      message || '请求失败，请稍后重试',
      businessDetail?.code,
      error.response?.status,
    ))
  },
)
