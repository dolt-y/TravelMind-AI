import { useEffect, useState } from 'react'
import { ArrowRight, Cookie, LoaderCircle, LogOut, Phone, QrCode, ShieldCheck } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import {
  clearXhsAdminSession,
  getXhsAdminLoginStatus,
  getXhsAdminQrImage,
  loginXhsAdminWithCookie,
  startXhsAdminPhoneLogin,
  startXhsAdminQrLogin,
  verifyXhsAdminPhoneLogin,
} from '../../services/xhsAdmin'
import type {
  XHSLoginMethod,
  XHSLoginStartResponse,
  XHSLoginStatusResponse,
} from '../../types'

const terminalStates = new Set(['success', 'expired', 'error'])

interface XhsAccountManagerProps {
  adminKey: string
  methods: XHSLoginMethod[]
  onContinue?: () => void
}

function taskFromStart(response: XHSLoginStartResponse): XHSLoginStatusResponse {
  return { ...response, qr_url: null, user_nickname: null }
}

export function XhsAccountManager({ adminKey, methods, onContinue }: XhsAccountManagerProps) {
  const { t } = useTranslation()
  const defaultMethod = methods.includes('qrcode') ? 'qrcode' : (methods[0] || 'cookie')
  const [method, setMethod] = useState<XHSLoginMethod>(defaultMethod)
  const [task, setTask] = useState<XHSLoginStatusResponse | null>(null)
  const [qrImageUrl, setQrImageUrl] = useState<string | null>(null)
  const [zone, setZone] = useState('86')
  const [phone, setPhone] = useState('')
  const [code, setCode] = useState('')
  const [cookie, setCookie] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)

  // 登录状态由后台任务推进，页面只在任务有效期间轮询。
  useEffect(() => {
    if (!task?.login_id || terminalStates.has(task.state)) return

    const poll = window.setInterval(() => {
      void getXhsAdminLoginStatus(adminKey, task.login_id)
        .then(setTask)
        .catch((pollError: unknown) => {
          setError(pollError instanceof Error ? pollError.message : t('adminXhs.errors.request'))
        })
    }, 1_500)

    return () => window.clearInterval(poll)
  }, [adminKey, task?.login_id, task?.state, t])

  const qrReady = method === 'qrcode'
    && !!task
    && (task.state === 'waiting_scan' || task.state === 'waiting_confirm')
  const qrLoginId = qrReady ? task?.login_id : undefined

  // NOTE: 二维码接口同样需要管理密钥，不能交给 img 标签直接公开请求。
  useEffect(() => {
    if (!qrLoginId || qrImageUrl) return
    let disposed = false

    void getXhsAdminQrImage(adminKey, qrLoginId)
      .then((blob) => {
        const objectUrl = URL.createObjectURL(blob)
        if (disposed) {
          URL.revokeObjectURL(objectUrl)
          return
        }
        setQrImageUrl(objectUrl)
      })
      .catch((imageError: unknown) => {
        if (!disposed) {
          setError(imageError instanceof Error ? imageError.message : t('adminXhs.errors.qrcode'))
        }
      })

    return () => {
      disposed = true
    }
  }, [adminKey, qrImageUrl, qrLoginId, t])

  useEffect(() => () => {
    if (qrImageUrl) URL.revokeObjectURL(qrImageUrl)
  }, [qrImageUrl])

  function reset(nextMethod: XHSLoginMethod) {
    if (qrImageUrl) URL.revokeObjectURL(qrImageUrl)
    setQrImageUrl(null)
    setMethod(nextMethod)
    setTask(null)
    setCode('')
    setError(null)
    setNotice(null)
    setBusy(false)
  }

  async function clearSession() {
    if (!window.confirm(t('adminXhs.logout.confirm'))) return
    setBusy(true)
    setError(null)
    setNotice(null)
    try {
      const response = await clearXhsAdminSession(adminKey)
      if (qrImageUrl) URL.revokeObjectURL(qrImageUrl)
      setQrImageUrl(null)
      setTask(null)
      setCode('')
      setCookie('')
      setNotice(response.message || t('adminXhs.logout.success'))
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : t('adminXhs.errors.logout'))
    } finally {
      setBusy(false)
    }
  }

  async function startQrCode() {
    setBusy(true)
    setError(null)
    if (qrImageUrl) URL.revokeObjectURL(qrImageUrl)
    setQrImageUrl(null)
    try {
      setTask(taskFromStart(await startXhsAdminQrLogin(adminKey)))
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : t('adminXhs.errors.request'))
    } finally {
      setBusy(false)
    }
  }

  async function startPhone() {
    setBusy(true)
    setError(null)
    try {
      const response = await startXhsAdminPhoneLogin(adminKey, phone.trim(), zone.trim())
      setTask(taskFromStart(response))
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : t('adminXhs.errors.request'))
    } finally {
      setBusy(false)
    }
  }

  async function verifyPhone() {
    if (!task?.login_id) return
    setBusy(true)
    setError(null)
    try {
      const response = await verifyXhsAdminPhoneLogin(adminKey, task.login_id, code.trim())
      setTask(taskFromStart(response))
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : t('adminXhs.errors.request'))
    } finally {
      setBusy(false)
    }
  }

  async function submitCookie() {
    setBusy(true)
    setError(null)
    try {
      const response = await loginXhsAdminWithCookie(adminKey, cookie.trim())
      setTask(taskFromStart(response))
      setCookie('')
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : t('adminXhs.errors.request'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="admin-account-manager" aria-labelledby="xhs-account-title">
      <div className="admin-section-heading">
        <div>
          <span className="eyebrow">{t('adminXhs.account.eyebrow')}</span>
          <h2 id="xhs-account-title">{t('adminXhs.account.title')}</h2>
          <p>{t('adminXhs.account.copy')}</p>
        </div>
        <span className="admin-access-state"><ShieldCheck size={15} />{t('adminXhs.access.verified')}</span>
      </div>

      <div className="segmented-control" aria-label={t('adminXhs.login.method')}>
        {methods.includes('qrcode') && <button className={method === 'qrcode' ? 'is-active' : ''} onClick={() => reset('qrcode')} type="button"><QrCode size={17} />{t('adminXhs.login.qrcode')}</button>}
        {methods.includes('phone') && <button className={method === 'phone' ? 'is-active' : ''} onClick={() => reset('phone')} type="button"><Phone size={17} />{t('adminXhs.login.phone')}</button>}
        {methods.includes('cookie') && <button className={method === 'cookie' ? 'is-active' : ''} onClick={() => reset('cookie')} type="button"><Cookie size={17} />Cookie</button>}
      </div>

      <div className="admin-login-panel">
        {method === 'qrcode' && (
          <div className="admin-login-panel__center">
            {qrImageUrl && qrReady ? (
              <img className="qr-image" src={qrImageUrl} alt={t('adminXhs.login.qrAlt')} />
            ) : (
              <div className="qr-placeholder">
                {busy || (!!task && !terminalStates.has(task.state)) ? <LoaderCircle className="spin" size={40} /> : <QrCode size={46} strokeWidth={1.4} />}
                <span>{task?.message || t('adminXhs.login.qrReady')}</span>
              </div>
            )}
            <button className="button button--primary" type="button" onClick={() => void startQrCode()} disabled={busy || (!!task && !terminalStates.has(task.state))}>
              {busy && <LoaderCircle className="spin" size={17} />}
              {task ? t('adminXhs.login.qrRestart') : t('adminXhs.login.qrStart')}
            </button>
          </div>
        )}

        {method === 'phone' && (
          <div className="admin-login-form">
            <div className="admin-phone-row">
              <label className="field admin-zone-field"><span>{t('adminXhs.login.zone')}</span><input inputMode="numeric" value={zone} onChange={(event) => setZone(event.target.value.replace(/\D/g, ''))} /></label>
              <label className="field"><span>{t('adminXhs.login.phoneNumber')}</span><input autoComplete="tel" inputMode="tel" value={phone} onChange={(event) => setPhone(event.target.value.replace(/\D/g, ''))} placeholder="13800000000" /></label>
            </div>
            <div className="admin-code-row">
              <label className="field"><span>{t('adminXhs.login.code')}</span><input autoComplete="one-time-code" inputMode="numeric" value={code} onChange={(event) => setCode(event.target.value.replace(/\D/g, ''))} placeholder={t('adminXhs.login.codePlaceholder')} /></label>
              <button className="button button--secondary" type="button" onClick={() => void startPhone()} disabled={busy || !zone.trim() || !phone.trim()}>{t('adminXhs.login.sendCode')}</button>
            </div>
            <button className="button button--primary" type="button" onClick={() => void verifyPhone()} disabled={busy || !task?.login_id || !code.trim()}>
              {busy && <LoaderCircle className="spin" size={17} />}{t('adminXhs.login.verify')}
            </button>
          </div>
        )}

        {method === 'cookie' && (
          <div className="admin-login-form">
            <label className="field"><span>{t('adminXhs.login.cookieLabel')}</span><textarea autoComplete="off" spellCheck={false} value={cookie} onChange={(event) => setCookie(event.target.value)} placeholder="a1=...; web_session=..." /></label>
            <p className="form-note"><ShieldCheck size={15} />{t('adminXhs.login.cookieNote')}</p>
            <button className="button button--primary" type="button" onClick={() => void submitCookie()} disabled={busy || !cookie.trim()}>
              {busy && <LoaderCircle className="spin" size={17} />}{t('adminXhs.login.cookieSubmit')}
            </button>
          </div>
        )}

        {task && (
          <div className={`login-status login-status--${task.state}`} role="status">
            <strong>{t(`adminXhs.states.${task.state}`)}</strong>
            <span>{task.message}</span>
            {task.user_nickname && <span>{t('adminXhs.login.currentUser', { name: task.user_nickname })}</span>}
            {task.state === 'success' && onContinue && (
              <button className="button button--primary login-status__action" type="button" onClick={onContinue}>
                {t('adminXhs.login.continuePlanning')}<ArrowRight size={16} />
              </button>
            )}
          </div>
        )}
        {notice && <div className="login-status login-status--success" role="status"><strong>{notice}</strong></div>}
        {error && <div className="inline-alert inline-alert--error" role="alert">{error}</div>}
      </div>
      <div className="admin-session-actions">
        <div><strong>{t('adminXhs.logout.title')}</strong><span>{t('adminXhs.logout.copy')}</span></div>
        <button className="button button--danger" type="button" onClick={() => void clearSession()} disabled={busy}>
          {busy ? <LoaderCircle className="spin" size={17} /> : <LogOut size={17} />}{t('adminXhs.logout.action')}
        </button>
      </div>
    </section>
  )
}
