import type {
  AttractionRequest,
  AttractionResponse,
  HealthResponse,
  HotelSearchResponse,
  WeatherResponse,
  XHSLoginStartResponse,
  XHSLoginStatusResponse,
} from './types'

async function parseResponse<T>(response: Response): Promise<T> {
  if (response.ok) {
    return response.json() as Promise<T>
  }

  let message = `请求失败（${response.status}）`
  try {
    const body = (await response.json()) as { detail?: string }
    if (body.detail) message = body.detail
  } catch {
    // 非 JSON 错误响应保留 HTTP 状态，避免遮盖真实请求结果。
  }
  throw new Error(message)
}

export async function getHealth(): Promise<HealthResponse> {
  return parseResponse<HealthResponse>(await fetch('/api/xhs/health'))
}

export async function extractAttractions(
  request: AttractionRequest,
): Promise<AttractionResponse> {
  const response = await fetch('/api/xhs/attractions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })
  return parseResponse<AttractionResponse>(response)
}

export async function getWeather(city: string): Promise<WeatherResponse> {
  const params = new URLSearchParams({ city })
  return parseResponse<WeatherResponse>(await fetch(`/api/weather?${params.toString()}`))
}

export async function searchHotels(city: string): Promise<HotelSearchResponse> {
  const params = new URLSearchParams({ city, limit: '6' })
  return parseResponse<HotelSearchResponse>(await fetch(`/api/hotels/search?${params.toString()}`))
}

export async function startXhsQrLogin(): Promise<XHSLoginStartResponse> {
  return parseResponse<XHSLoginStartResponse>(await fetch('/api/xhs/login/qrcode/start', { method: 'POST' }))
}

export async function startXhsPhoneLogin(phone: string, zone = '86'): Promise<XHSLoginStartResponse> {
  const response = await fetch('/api/xhs/login/phone/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone, zone }),
  })
  return parseResponse<XHSLoginStartResponse>(response)
}

export async function verifyXhsPhoneLogin(loginId: string, code: string): Promise<XHSLoginStartResponse> {
  const response = await fetch('/api/xhs/login/phone/verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ login_id: loginId, code }),
  })
  return parseResponse<XHSLoginStartResponse>(response)
}

export async function getXhsLoginStatus(loginId: string): Promise<XHSLoginStatusResponse> {
  return parseResponse<XHSLoginStatusResponse>(await fetch(`/api/xhs/login/${encodeURIComponent(loginId)}/status`))
}

export async function loginWithXhsCookie(cookie: string): Promise<XHSLoginStartResponse> {
  const response = await fetch('/api/xhs/login/cookie', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cookie }),
  })
  return parseResponse<XHSLoginStartResponse>(response)
}
