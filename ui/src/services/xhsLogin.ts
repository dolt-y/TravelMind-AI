import type {
  XHSLoginStartResponse,
  XHSLoginStatusResponse,
} from '../types'
import { http } from './http'

export async function startXhsQrLogin(): Promise<XHSLoginStartResponse> {
  const { data } = await http.post<XHSLoginStartResponse>('/xhs/login/qrcode/start')
  return data
}

export function getXhsQrImageUrl(loginId: string): string {
  return `/api/xhs/login/${encodeURIComponent(loginId)}/qrcode`
}

export async function getXhsLoginStatus(loginId: string): Promise<XHSLoginStatusResponse> {
  const { data } = await http.get<XHSLoginStatusResponse>(
    `/xhs/login/${encodeURIComponent(loginId)}/status`,
  )
  return data
}

export async function startXhsPhoneLogin(
  phone: string,
  zone = '86',
): Promise<XHSLoginStartResponse> {
  const { data } = await http.post<XHSLoginStartResponse>('/xhs/login/phone/start', {
    phone,
    zone,
  })
  return data
}

export async function verifyXhsPhoneLogin(
  loginId: string,
  code: string,
): Promise<XHSLoginStartResponse> {
  const { data } = await http.post<XHSLoginStartResponse>('/xhs/login/phone/verify', {
    login_id: loginId,
    code,
  })
  return data
}

export async function loginWithXhsCookie(cookie: string): Promise<XHSLoginStartResponse> {
  const { data } = await http.post<XHSLoginStartResponse>('/xhs/login/cookie', { cookie })
  return data
}
