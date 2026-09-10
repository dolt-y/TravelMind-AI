import { useEffect, useState } from 'react'
import { ArrowRight, Cookie, LoaderCircle, LogOut, Phone, QrCode, ShieldCheck } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import {
  clearXhsSession,
  getXhsLoginStatus,
  getXhsQrImage,
  loginXhsWithCookie,
  startXhsPhoneLogin,
  startXhsQrLogin,
  verifyXhsPhoneLogin,
} from '../../services/xhsLogin'
import type {
  XHSLoginMethod,
  XHSLoginStartResponse,
  XHSLoginStatusResponse,
} from '../../types'

const terminalStates = new Set(['success', 'expired', 'error'])

interface XhsAccountManagerProps {
  methods: XHSLoginMethod[]
  onContinue?: () => void
}

function taskFromStart(response: XHSLoginStartResponse): XHSLoginStatusResponse {
  return { ...response, qr_url: null, user_nickname: null }
}

export function XhsAccountManager({ methods, onContinue }: XhsAccountManagerProps) {
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
      void getXhsLoginStatus(task.login_id)
        .then(setTask)
        .catch((pollError: unknown) => {
          setError(pollError instanceof Error ? pollError.message : t('xhsAccount.errors.request'))
        })
    }, 1_500)

    return () => window.clearInterval(poll)
  }, [task?.login_id, task?.state, t])

  const qrReady = method === 'qrcode'
    && !!task
    && (task.state === 'waiting_scan' || task.state === 'waiting_confirm')
  const qrLoginId = qrReady ? task?.login_id : undefined

  // 二维码以临时 Blob 地址展示，任务重置或组件卸载时立即释放。
  useEffect(() => {
    if (!qrLoginId || qrImageUrl) return
    let disposed = false

    void getXhsQrImage(qrLoginId)
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
          setError(imageError instanceof Error ? imageError.message : t('xhsAccount.errors.qrcode'))
        }
      })

    return () => {
      disposed = true
    }
  }, [qrImageUrl, qrLoginId, t])

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
    if (!window.confirm(t('xhsAccount.logout.confirm'))) return
    setBusy(true)
    setError(null)
    setNotice(null)
    try {
      const response = await clearXhsSession(task?.login_id)
      if (qrImageUrl) URL.revokeObjectURL(qrImageUrl)
      setQrImageUrl(null)
      setTask(null)
      setCode('')
      setCookie('')
      setNotice(response.message || t('xhsAccount.logout.success'))
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : t('xhsAccount.errors.logout'))
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
      setTask(taskFromStart(await startXhsQrLogin()))
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : t('xhsAccount.errors.request'))
    } finally {
      setBusy(false)
    }
  }

  async function startPhone() {
    setBusy(true)
    setError(null)
    try {
      const response = await startXhsPhoneLogin(phone.trim(), zone.trim())
      setTask(taskFromStart(response))
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : t('xhsAccount.errors.request'))
    } finally {
      setBusy(false)
    }
  }

  async function verifyPhone() {
    if (!task?.login_id) return
    setBusy(true)
    setError(null)
    try {
      const response = await verifyXhsPhoneLogin(task.login_id, code.trim())
      setTask(taskFromStart(response))
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : t('xhsAccount.errors.request'))
    } finally {
      setBusy(false)
    }
  }

  async function submitCookie() {
    setBusy(true)
    setError(null)
    try {
      const response = await loginXhsWithCookie(cookie.trim())
      setTask(taskFromStart(response))
      setCookie('')
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : t('xhsAccount.errors.request'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="xhs-account-manager" aria-labelledby="xhs-account-title">
      <div className="xhs-account-heading">
        <div>
          <span className="eyebrow">{t('xhsAccount.account.eyebrow')}</span>
          <h2 id="xhs-account-title">{t('xhsAccount.account.title')}</h2>
          <p>{t('xhsAccount.account.copy')}</p>
        </div>
      </div>

      <div className="segmented-control" aria-label={t('xhsAccount.login.method')}>
        {methods.includes('qrcode') && <button className={method === 'qrcode' ? 'is-active' : ''} onClick={() => reset('qrcode')} type="button"><QrCode size={17} />{t('xhsAccount.login.qrcode')}</button>}
        {methods.includes('phone') && <button className={method === 'phone' ? 'is-active' : ''} onClick={() => reset('phone')} type="button"><Phone size={17} />{t('xhsAccount.login.phone')}</button>}
        {methods.includes('cookie') && <button className={method === 'cookie' ? 'is-active' : ''} onClick={() => reset('cookie')} type="button"><Cookie size={17} />Cookie</button>}
      </div>

      <div className="xhs-login-panel">
        {method === 'qrcode' && (
          <div className="xhs-login-panel__center">
            {qrImageUrl && qrReady ? (
              <img className="qr-image" src={qrImageUrl} alt={t('xhsAccount.login.qrAlt')} />
            ) : (
              <div className="qr-placeholder">
                {busy || (!!task && !terminalStates.has(task.state)) ? <LoaderCircle className="spin" size={40} /> : <QrCode size={46} strokeWidth={1.4} />}
                <span>{task?.message || t('xhsAccount.login.qrReady')}</span>
              </div>
            )}
            <button className="button button--primary" type="button" onClick={() => void startQrCode()} disabled={busy || (!!task && !terminalStates.has(task.state))}>
              {busy && <LoaderCircle className="spin" size={17} />}
              {task ? t('xhsAccount.login.qrRestart') : t('xhsAccount.login.qrStart')}
            </button>
          </div>
        )}

        {method === 'phone' && (
          <div className="xhs-login-form">
            <div className="xhs-phone-row">
              <label className="field xhs-zone-field"><span>{t('xhsAccount.login.zone')}</span><input inputMode="numeric" value={zone} onChange={(event) => setZone(event.target.value.replace(/\D/g, ''))} /></label>
              <label className="field"><span>{t('xhsAccount.login.phoneNumber')}</span><input autoComplete="tel" inputMode="tel" value={phone} onChange={(event) => setPhone(event.target.value.replace(/\D/g, ''))} placeholder="13800000000" /></label>
            </div>
            <div className="xhs-code-row">
              <label className="field"><span>{t('xhsAccount.login.code')}</span><input autoComplete="one-time-code" inputMode="numeric" value={code} onChange={(event) => setCode(event.target.value.replace(/\D/g, ''))} placeholder={t('xhsAccount.login.codePlaceholder')} /></label>
              <button className="button button--secondary" type="button" onClick={() => void startPhone()} disabled={busy || !zone.trim() || !phone.trim()}>{t('xhsAccount.login.sendCode')}</button>
            </div>
            <button className="button button--primary" type="button" onClick={() => void verifyPhone()} disabled={busy || !task?.login_id || !code.trim()}>
              {busy && <LoaderCircle className="spin" size={17} />}{t('xhsAccount.login.verify')}
            </button>
          </div>
        )}

        {method === 'cookie' && (
          <div className="xhs-login-form">
            <label className="field"><span>{t('xhsAccount.login.cookieLabel')}</span><textarea autoComplete="off" spellCheck={false} value={cookie} onChange={(event) => setCookie(event.target.value)} placeholder="a1=...; web_session=..." /></label>
            <p className="form-note"><ShieldCheck size={15} />{t('xhsAccount.login.cookieNote')}</p>
            <button className="button button--primary" type="button" onClick={() => void submitCookie()} disabled={busy || !cookie.trim()}>
              {busy && <LoaderCircle className="spin" size={17} />}{t('xhsAccount.login.cookieSubmit')}
            </button>
          </div>
        )}

        {task && (
          <div className={`login-status login-status--${task.state}`} role="status">
            <strong>{t(`xhsAccount.states.${task.state}`)}</strong>
            {task.state !== 'success' && <span>{task.message}</span>}
            {task.user_nickname && <span>{t('xhsAccount.login.currentUser', { name: task.user_nickname })}</span>}
            {task.state === 'success' && onContinue && (
              <button className="button button--primary login-status__action" type="button" onClick={onContinue}>
                {t('xhsAccount.login.continuePlanning')}<ArrowRight size={16} />
              </button>
            )}
          </div>
        )}
        {notice && <div className="login-status login-status--success" role="status"><strong>{notice}</strong></div>}
        {error && <div className="inline-alert inline-alert--error" role="alert">{error}</div>}
      </div>
      <div className="xhs-session-actions">
        <div><strong>{t('xhsAccount.logout.title')}</strong><span>{t('xhsAccount.logout.copy')}</span></div>
        <button className="button button--danger" type="button" onClick={() => void clearSession()} disabled={busy}>
          {busy ? <LoaderCircle className="spin" size={17} /> : <LogOut size={17} />}{t('xhsAccount.logout.action')}
        </button>
      </div>
    </section>
  )
}
