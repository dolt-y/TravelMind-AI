import { CalendarDays, MapPin, Users } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useTripStore } from '../../stores/tripStore'

export function PlannerSummary() {
  const { t } = useTranslation()
  const draft = useTripStore((state) => state.draft)

  return (
    <aside className="plan-summary" aria-label={t('plan.summaryTitle')}>
      <div className="plan-summary__image"><img src="/assets/travel/switzerland-lake.jpg" alt="" /></div>
      <div className="plan-summary__content">
        <span className="eyebrow">TRAVELMIND / PLAN</span>
        <h2>{t('plan.summaryTitle')}</h2>
        <dl>
          <div><dt><MapPin size={16} />{t('planner.destination')}</dt><dd>{draft.city || '—'}</dd></div>
          <div><dt><CalendarDays size={16} />{t('planner.startDate')}</dt><dd>{draft.startDate}</dd></div>
          <div><dt><CalendarDays size={16} />{t('planner.endDate')}</dt><dd>{draft.endDate}</dd></div>
          <div><dt><Users size={16} />{t('planner.travelers')}</dt><dd>{draft.travelers}</dd></div>
          <div><dt>{t('planner.transportation')}</dt><dd>{t(`planner.transport.${draft.transportation}`)}</dd></div>
          <div><dt>{t('planner.totalBudget')}</dt><dd>{draft.totalBudget ? `¥${draft.totalBudget.toLocaleString()}` : '—'}</dd></div>
        </dl>
      </div>
    </aside>
  )
}
