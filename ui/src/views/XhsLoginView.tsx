import { KeyRound } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { XhsLoginPanel } from '../components/xhs/XhsLoginPanel'

export function XhsLoginView() {
  const { t } = useTranslation()
  return (
    <div className="page-container">
      <header className="page-heading"><span className="eyebrow"><KeyRound size={15} />{t('login.eyebrow')}</span><h1>{t('login.title')}</h1><p>{t('login.copy')}</p></header>
      <XhsLoginPanel />
    </div>
  )
}
