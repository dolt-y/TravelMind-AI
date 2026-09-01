import axios from 'axios'

interface ApiErrorPayload {
  detail?: string | { msg?: string }[]
  message?: string
}

export const http = axios.create({
  baseURL: '/api',
  // 景点提取包含笔记抓取和大模型处理，使用长超时覆盖完整业务链。
  timeout: 200_000,
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
      : detail
    const message = validationMessage
      || error.response?.data?.message
      || (error.code === 'ECONNABORTED' ? '请求处理超时，请稍后重试' : error.message)

    return Promise.reject(new Error(message || '请求失败，请稍后重试'))
  },
)
