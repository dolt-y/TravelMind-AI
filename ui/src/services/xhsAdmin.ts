import type {
  XHSLoginMethodsResponse,
  XHSLoginStartResponse,
  XHSLoginStatusResponse,
} from '../types'
import { http } from './http'

const ADMIN_XHS_PATH = '/admin/integrations/xhs'
const ADMIN_KEY_HEADER = 'X-TravelMind-Admin-Key'

function adminHeaders(adminKey: string) {
  return { [ADMIN_KEY_HEADER]: adminKey }
}

/** 验证管理密钥，并返回当前系统账号支持的维护方式。 */
export async function getXhsAdminMethods(adminKey: string): Promise<XHSLoginMethodsResponse> {
  const { data } = await http.get<XHSLoginMethodsResponse>(`${ADMIN_XHS_PATH}/methods`, {
    headers: adminHeaders(adminKey),
  })
  return data
}

/** 创建系统账号二维码登录任务。 */
export async function startXhsAdminQrLogin(adminKey: string): Promise<XHSLoginStartResponse> {
  const { data } = await http.post<XHSLoginStartResponse>(
    `${ADMIN_XHS_PATH}/qrcode/start`,
    undefined,
    { headers: adminHeaders(adminKey) },
  )
  return data
}

/** 带管理员鉴权读取二维码，返回仅供当前页面展示的临时图片。 */
export async function getXhsAdminQrImage(adminKey: string, loginId: string): Promise<Blob> {
  const { data } = await http.get<Blob>(
    `${ADMIN_XHS_PATH}/${encodeURIComponent(loginId)}/qrcode`,
    { headers: adminHeaders(adminKey), responseType: 'blob' },
  )
  return data
}

/** 查询二维码或手机号登录任务的实时状态。 */
export async function getXhsAdminLoginStatus(
  adminKey: string,
  loginId: string,
): Promise<XHSLoginStatusResponse> {
  const { data } = await http.get<XHSLoginStatusResponse>(
    `${ADMIN_XHS_PATH}/${encodeURIComponent(loginId)}/status`,
    { headers: adminHeaders(adminKey) },
  )
  return data
}

/** 发送系统账号手机号验证码。 */
export async function startXhsAdminPhoneLogin(
  adminKey: string,
  phone: string,
  zone = '86',
): Promise<XHSLoginStartResponse> {
  const { data } = await http.post<XHSLoginStartResponse>(
    `${ADMIN_XHS_PATH}/phone/start`,
    { phone, zone },
    { headers: adminHeaders(adminKey) },
  )
  return data
}

/** 提交验证码并完成系统账号会话验证。 */
export async function verifyXhsAdminPhoneLogin(
  adminKey: string,
  loginId: string,
  code: string,
): Promise<XHSLoginStartResponse> {
  const { data } = await http.post<XHSLoginStartResponse>(
    `${ADMIN_XHS_PATH}/phone/verify`,
    { login_id: loginId, code },
    { headers: adminHeaders(adminKey) },
  )
  return data
}

/** 验证 Cookie 并更新系统内容账号的运行会话。 */
export async function loginXhsAdminWithCookie(
  adminKey: string,
  cookie: string,
): Promise<XHSLoginStartResponse> {
  const { data } = await http.post<XHSLoginStartResponse>(
    `${ADMIN_XHS_PATH}/cookie`,
    { cookie },
    { headers: adminHeaders(adminKey) },
  )
  return data
}
