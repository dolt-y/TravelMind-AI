import type {
  XHSLoginStartResponse,
  XHSLoginStatusResponse,
  XHSLogoutResponse,
} from '../types'
import { http } from './http'

const XHS_LOGIN_PATH = '/xhs/login'

// 退出时同时取消未完成的登录任务。
export async function clearXhsSession(loginId?: string): Promise<XHSLogoutResponse> {
  const { data } = await http.delete<XHSLogoutResponse>(`${XHS_LOGIN_PATH}/session`, {
    params: loginId ? { login_id: loginId } : undefined,
  })
  return data
}

export async function startXhsQrLogin(): Promise<XHSLoginStartResponse> {
  const { data } = await http.post<XHSLoginStartResponse>(`${XHS_LOGIN_PATH}/qrcode/start`)
  return data
}

export async function getXhsQrImage(loginId: string): Promise<Blob> {
  const { data } = await http.get<Blob>(
    `${XHS_LOGIN_PATH}/${encodeURIComponent(loginId)}/qrcode`,
    { responseType: 'blob' },
  )
  return data
}

export async function getXhsLoginStatus(loginId: string): Promise<XHSLoginStatusResponse> {
  const { data } = await http.get<XHSLoginStatusResponse>(
    `${XHS_LOGIN_PATH}/${encodeURIComponent(loginId)}/status`,
  )
  return data
}

export async function startXhsPhoneLogin(
  phone: string,
  zone = '86',
): Promise<XHSLoginStartResponse> {
  const { data } = await http.post<XHSLoginStartResponse>(
    `${XHS_LOGIN_PATH}/phone/start`,
    { phone, zone },
  )
  return data
}

export async function verifyXhsPhoneLogin(
  loginId: string,
  code: string,
): Promise<XHSLoginStartResponse> {
  const { data } = await http.post<XHSLoginStartResponse>(
    `${XHS_LOGIN_PATH}/phone/verify`,
    { login_id: loginId, code },
  )
  return data
}

export async function loginXhsWithCookie(cookie: string): Promise<XHSLoginStartResponse> {
  const { data } = await http.post<XHSLoginStartResponse>(
    `${XHS_LOGIN_PATH}/cookie`,
    { cookie },
  )
  return data
}
