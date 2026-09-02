import { useState } from 'react'
import { ArrowLeft, Eye, EyeOff, KeyRound, LoaderCircle, LogOut, Mountain, ShieldCheck } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { XhsAccountManager } from '../components/admin/XhsAccountManager'
import { LanguageSwitcher } from '../components/common/LanguageSwitcher'
import { getXhsAdminMethods } from '../services/xhsAdmin'
import type { XHSLoginMethod } from '../types'

export function XhsAdminView() {
  const { t } = useTranslation()
  const [keyInput, setKeyInput] = useState('')
  const [adminKey, setAdminKey] = useState<string | null>(null)
  const [methods, setMethods] = useState<XHSLoginMethod[]>([])
  const [showKey, setShowKey] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function authorize() {
    const candidate = keyInput.trim()
    if (!candidate) return
    setBusy(true)
    setError(null)
    try {
      const response = await getXhsAdminMethods(candidate)
      setMethods(response.methods)
      setAdminKey(candidate)
      setKeyInput('')
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : t('adminXhs.errors.access'))
    } finally {
      setBusy(false)
    }
  }

  function leaveAdmin() {
    setAdminKey(null)
    setMethods([])
    setKeyInput('')
    setError(null)
  }

  return (
    <div className="admin-shell">
      <header className="admin-header">
        <div className="admin-header__inner">
          <div className="admin-brand"><span className="brand__mark"><Mountain size={20} /></span><span>TravelMind</span><small>{t('adminXhs.shell.label')}</small></div>
          <div className="admin-header__actions">
            <LanguageSwitcher />
            {adminKey ? (
              <button className="button button--secondary" type="button" onClick={leaveAdmin}><LogOut size={16} />{t('adminXhs.shell.exit')}</button>
            ) : (
              <Link className="button button--secondary" to="/"><ArrowLeft size={16} />{t('adminXhs.shell.back')}</Link>
            )}
          </div>
        </div>
      </header>

      <main className="admin-main">
        <header className="admin-page-heading">
          <span className="eyebrow"><ShieldCheck size={15} />{t('adminXhs.eyebrow')}</span>
          <h1>{t('adminXhs.title')}</h1>
          <p>{t('adminXhs.copy')}</p>
        </header>

        {!adminKey ? (
          <section className="admin-access-panel" aria-labelledby="admin-access-title">
            <div className="admin-access-panel__intro">
              <span><KeyRound size={20} /></span>
              <div><h2 id="admin-access-title">{t('adminXhs.access.title')}</h2><p>{t('adminXhs.access.copy')}</p></div>
            </div>
            <form onSubmit={(event) => { event.preventDefault(); void authorize() }}>
              <label className="field">
                <span>{t('adminXhs.access.keyLabel')}</span>
                <span className="admin-secret-control">
                  <input
                    autoComplete="new-password"
                    name="travelmind-internal-access-key"
                    type={showKey ? 'text' : 'password'}
                    value={keyInput}
                    onChange={(event) => setKeyInput(event.target.value)}
                    placeholder={t('adminXhs.access.keyPlaceholder')}
                  />
                  <button className="icon-button" type="button" onClick={() => setShowKey((visible) => !visible)} title={showKey ? t('adminXhs.access.hideKey') : t('adminXhs.access.showKey')}>
                    {showKey ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </span>
              </label>
              <p className="form-note"><ShieldCheck size={15} />{t('adminXhs.access.memoryOnly')}</p>
              <button className="button button--primary" type="submit" disabled={busy || !keyInput.trim()}>
                {busy ? <LoaderCircle className="spin" size={17} /> : <KeyRound size={17} />}{t('adminXhs.access.submit')}
              </button>
            </form>
            {error && <div className="inline-alert inline-alert--error" role="alert">{error}</div>}
          </section>
        ) : (
          <XhsAccountManager adminKey={adminKey} methods={methods} />
        )}
      </main>
    </div>
  )
}
