import { RefreshCw } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useAppStore } from '../../stores/appStore'

export function ServiceStatus({ compact = false }: { compact?: boolean }) {
  const { t } = useTranslation()
  const healthState = useAppStore((state) => state.healthState)
  const refreshHealth = useAppStore((state) => state.refreshHealth)
  const statusKey = healthState === 'idle' ? 'checking' : healthState

  return (
    <button
      className={`service-status service-status--${healthState}${compact ? ' service-status--compact' : ''}`}
      type="button"
      onClick={() => void refreshHealth()}
      title={t('status.refresh')}
    >
      <span className="service-status__dot" aria-hidden="true" />
      <span>{t(`status.${statusKey}`)}</span>
      {!compact && <RefreshCw size={14} aria-hidden="true" />}
    </button>
  )
}
