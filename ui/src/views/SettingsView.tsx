import { RefreshCw } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { XhsAccountManager } from '../components/settings/XhsAccountManager'
import type { XHSLoginMethod } from '../types'

const allowedReturnPaths = new Set(['/plan', '/plan/running', '/results'])
const xhsLoginMethods: XHSLoginMethod[] = ['qrcode', 'phone', 'cookie']

function safeReturnPath(value: string | null): string | null {
  // 只允许回跳到站内业务页面。
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
      <div className="settings-workspace">
        <section className="settings-account" aria-label={t('xhsAccount.account.title')}>
          {returnTo && (
            <div className="inline-alert settings-account__alert" role="status"><RefreshCw size={16} />{t('xhsAccount.authRequired')}</div>
          )}
          <XhsAccountManager
            methods={xhsLoginMethods}
            onSuccess={() => navigate(returnTo || '/', { replace: true })}
          />
        </section>
      </div>
    </div>
  )
}
