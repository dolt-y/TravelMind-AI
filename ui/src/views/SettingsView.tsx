import { KeyRound, Settings } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { LanguageSwitcher } from '../components/common/LanguageSwitcher'

export function SettingsView() {
  const { t } = useTranslation()
  return (
    <div className="page-container settings-page">
      <header className="page-heading"><span className="eyebrow"><Settings size={15} />{t('settings.eyebrow')}</span><h1>{t('settings.title')}</h1><p>{t('settings.copy')}</p></header>
      <section className="settings-list">
        <article><div><strong>{t('settings.language')}</strong><span>{t('settings.languageCopy')}</span></div><LanguageSwitcher /></article>
        <article><div><strong>{t('settings.xhs')}</strong><span>{t('settings.xhsCopy')}</span></div><Link className="button button--secondary" to="/account/xhs"><KeyRound size={16} />{t('settings.manage')}</Link></article>
      </section>
    </div>
  )
}
