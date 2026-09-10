import type {
  XHSLoginStartResponse,
  XHSLoginStatusResponse,
  XHSLogoutResponse,
} from '../types'
import { http } from './http'

const XHS_LOGIN_PATH = '/xhs/login'

/** 清除当前浏览器会话，并取消该页面仍在进行的登录挑战。 */
export async function clearXhsSession(loginId?: string): Promise<XHSLogoutResponse> {
  const { data } = await http.delete<XHSLogoutResponse>(`${XHS_LOGIN_PATH}/session`, {
    params: loginId ? { login_id: loginId } : undefined,
  })
  return data
}

/** 创建当前浏览器的二维码登录任务。 */
export async function startXhsQrLogin(): Promise<XHSLoginStartResponse> {
  const { data } = await http.post<XHSLoginStartResponse>(`${XHS_LOGIN_PATH}/qrcode/start`)
  return data
}

/** 获取当前登录任务生成的二维码图片。 */
export async function getXhsQrImage(loginId: string): Promise<Blob> {
  const { data } = await http.get<Blob>(
    `${XHS_LOGIN_PATH}/${encodeURIComponent(loginId)}/qrcode`,
    { responseType: 'blob' },
  )
  return data
}

/** 查询二维码或手机号登录任务的实时状态。 */
export async function getXhsLoginStatus(loginId: string): Promise<XHSLoginStatusResponse> {
  const { data } = await http.get<XHSLoginStatusResponse>(
    `${XHS_LOGIN_PATH}/${encodeURIComponent(loginId)}/status`,
  )
  return data
}

/** 发送当前浏览器发起的手机号登录验证码。 */
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

/** 提交验证码并完成当前浏览器的会话验证。 */
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

/** 验证 Cookie，并为当前浏览器签发独立的加密会话。 */
export async function loginXhsWithCookie(cookie: string): Promise<XHSLoginStartResponse> {
  const { data } = await http.post<XHSLoginStartResponse>(
    `${XHS_LOGIN_PATH}/cookie`,
    { cookie },
  )
  return data
}
