import { Languages } from 'lucide-react'
import { useTranslation } from 'react-i18next'

export function LanguageSwitcher() {
  const { i18n, t } = useTranslation()

  return (
    <label className="language-switcher">
      <Languages size={16} aria-hidden="true" />
      <span className="sr-only">{t('common.language')}</span>
      <select
        value={i18n.resolvedLanguage ?? 'zh'}
        onChange={(event) => void i18n.changeLanguage(event.target.value)}
        aria-label={t('common.language')}
      >
        <option value="zh">中文</option>
        <option value="en">English</option>
        <option value="ja">日本語</option>
      </select>
    </label>
  )
}
