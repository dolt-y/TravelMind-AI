import { RefreshCw } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { XhsAccountManager } from '../components/settings/XhsAccountManager'
import { LanguageSwitcher } from '../components/common/LanguageSwitcher'
import type { XHSLoginMethod } from '../types'

const allowedReturnPaths = new Set(['/plan', '/plan/running', '/results'])
const xhsLoginMethods: XHSLoginMethod[] = ['qrcode', 'phone', 'cookie']

function safeReturnPath(value: string | null): string | null {
  // NOTE: 回跳地址只接受固定业务页面，查询参数不能跳出本站。
  return value && allowedReturnPaths.has(value) ? value : null
}

export function SettingsView() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const returnTo = safeReturnPath(searchParams.get('returnTo'))
  return (
    <div className="page-container settings-page">
      <header className="page-heading"><h1>{t('settings.title')}</h1></header>
      <section className="settings-list">
        <article><div><strong>{t('settings.language')}</strong><span>{t('settings.languageCopy')}</span></div><LanguageSwitcher /></article>
      </section>

      <section className="settings-account" aria-label={t('xhsAccount.account.title')}>
        {returnTo && (
          <div className="inline-alert settings-account__alert" role="status"><RefreshCw size={16} />{t('xhsAccount.authRequired')}</div>
        )}
        <XhsAccountManager
          methods={xhsLoginMethods}
          onContinue={returnTo ? () => navigate(returnTo, { replace: true }) : undefined}
        />
      </section>
    </div>
  )
}
