import { Compass } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { EmptyState } from '../components/common/EmptyState'

export function NotFoundView() {
  const { t } = useTranslation()
  return <div className="page-container"><EmptyState icon={Compass} title="404" description={t('notFound.copy')} actionLabel={t('notFound.home')} actionTo="/" /></div>
}
