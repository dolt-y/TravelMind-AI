import { useEffect, useState } from 'react'
import { Cookie, LoaderCircle, Phone, QrCode, ShieldCheck } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import {
  getXhsLoginStatus,
  getXhsQrImageUrl,
  loginWithXhsCookie,
  startXhsPhoneLogin,
  startXhsQrLogin,
  verifyXhsPhoneLogin,
} from '../../services/xhsLogin'
import type { XHSLoginMethod, XHSLoginStatusResponse } from '../../types'

const terminalStates = new Set(['success', 'expired', 'error'])

export function XhsLoginPanel() {
  const { t } = useTranslation()
  const [method, setMethod] = useState<XHSLoginMethod>('qrcode')
  const [task, setTask] = useState<XHSLoginStatusResponse | null>(null)
  const [phone, setPhone] = useState('')
  const [code, setCode] = useState('')
  const [cookie, setCookie] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!task?.login_id || terminalStates.has(task.state)) return

    const poll = window.setInterval(() => {
      void getXhsLoginStatus(task.login_id)
        .then((status) => {
          setTask(status)
        })
        .catch((pollError: unknown) => {
          setError(pollError instanceof Error ? pollError.message : t('login.error'))
        })
    }, 1_500)

    return () => window.clearInterval(poll)
  }, [task?.login_id, task?.state, t])

  function reset(nextMethod: XHSLoginMethod) {
    setMethod(nextMethod)
    setTask(null)
    setError(null)
    setBusy(false)
  }

  async function startQrCode() {
    setBusy(true)
    setError(null)
    try {
      const response = await startXhsQrLogin()
      setTask({ ...response, qr_url: null, user_nickname: null })
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : t('login.error'))
    } finally {
      setBusy(false)
    }
  }

  async function startPhone() {
    setBusy(true)
    setError(null)
    try {
      const response = await startXhsPhoneLogin(phone.trim())
      setTask({ ...response, qr_url: null, user_nickname: null })
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : t('login.error'))
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
      setTask({ ...response, qr_url: null, user_nickname: null })
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : t('login.error'))
    } finally {
      setBusy(false)
    }
  }

  async function submitCookie() {
    setBusy(true)
    setError(null)
    try {
      const response = await loginWithXhsCookie(cookie.trim())
      setTask({ ...response, qr_url: null, user_nickname: null })
      setCookie('')
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : t('login.error'))
    } finally {
      setBusy(false)
    }
  }

  const qrReady = task?.state === 'waiting_scan' || task?.state === 'waiting_confirm'

  return (
    <div className="login-workspace">
      <div className="segmented-control" aria-label={t('login.method')}>
        <button className={method === 'qrcode' ? 'is-active' : ''} onClick={() => reset('qrcode')} type="button"><QrCode size={17} />{t('login.qrcode')}</button>
        <button className={method === 'phone' ? 'is-active' : ''} onClick={() => reset('phone')} type="button"><Phone size={17} />{t('login.phone')}</button>
        <button className={method === 'cookie' ? 'is-active' : ''} onClick={() => reset('cookie')} type="button"><Cookie size={17} />Cookie</button>
      </div>

      <div className="login-panel">
        {method === 'qrcode' && (
          <div className="login-panel__center">
            {qrReady && task ? (
              <img className="qr-image" src={getXhsQrImageUrl(task.login_id)} alt={t('login.qrAlt')} />
            ) : (
              <div className="qr-placeholder"><QrCode size={46} strokeWidth={1.4} /><span>{t('login.qrReady')}</span></div>
            )}
            <button className="button button--primary" type="button" onClick={() => void startQrCode()} disabled={busy || (!!task && !terminalStates.has(task.state))}>
              {busy && <LoaderCircle className="spin" size={17} />}
              {task ? t('login.qrRestart') : t('login.qrStart')}
            </button>
          </div>
        )}

        {method === 'phone' && (
          <div className="login-form">
            <label className="field"><span>{t('login.phoneNumber')}</span><input value={phone} onChange={(event) => setPhone(event.target.value)} placeholder="138 0000 0000" /></label>
            <div className="phone-code-row">
              <label className="field"><span>{t('login.code')}</span><input value={code} onChange={(event) => setCode(event.target.value)} placeholder={t('login.codePlaceholder')} /></label>
              <button className="button button--secondary" type="button" onClick={() => void startPhone()} disabled={busy || !phone.trim()}>{t('login.sendCode')}</button>
            </div>
            <button className="button button--primary" type="button" onClick={() => void verifyPhone()} disabled={busy || !task?.login_id || !code.trim()}>
              {busy && <LoaderCircle className="spin" size={17} />}{t('login.verify')}
            </button>
          </div>
        )}

        {method === 'cookie' && (
          <div className="login-form">
            <label className="field"><span>{t('login.cookieLabel')}</span><textarea value={cookie} onChange={(event) => setCookie(event.target.value)} placeholder="a1=...; web_session=..." /></label>
            <p className="form-note"><ShieldCheck size={15} />{t('login.cookieNote')}</p>
            <button className="button button--primary" type="button" onClick={() => void submitCookie()} disabled={busy || !cookie.trim()}>
              {busy && <LoaderCircle className="spin" size={17} />}{t('login.cookieSubmit')}
            </button>
          </div>
        )}

        {task && (
          <div className={`login-status login-status--${task.state}`}>
            <strong>{t(`login.states.${task.state}`)}</strong>
            <span>{task.message}</span>
          </div>
        )}
        {error && <div className="inline-alert inline-alert--error">{error}</div>}
      </div>
    </div>
  )
}
