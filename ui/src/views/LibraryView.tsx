import { ArrowUpRight, BookOpen, CalendarDays, LoaderCircle, RefreshCw, Users } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { EmptyState } from '../components/common/EmptyState'
import { useTripStore } from '../stores/tripStore'

export function LibraryView() {
  const { i18n, t } = useTranslation()
  const navigate = useNavigate()
  const history = useTripStore((state) => state.history)
  const historyLoading = useTripStore((state) => state.historyLoading)
  const historyError = useTripStore((state) => state.historyError)
  const loadTripHistory = useTripStore((state) => state.loadTripHistory)
  const restoreTripPlan = useTripStore((state) => state.restoreTripPlan)
  const [openingPlanId, setOpeningPlanId] = useState<string | null>(null)
  const [openError, setOpenError] = useState(false)

  useEffect(() => {
    void loadTripHistory()
  }, [loadTripHistory])

  const openPlan = async (planId: string) => {
    setOpeningPlanId(planId)
    setOpenError(false)
    try {
      await restoreTripPlan(planId)
      navigate('/results')
    } catch {
      setOpenError(true)
    } finally {
      setOpeningPlanId(null)
    }
  }

  const formatCreatedAt = (value: string) => new Intl.DateTimeFormat(i18n.language, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(value))

  if (!historyLoading && !historyError && !history.length) {
    return <div className="page-container"><EmptyState icon={BookOpen} title={t('library.emptyTitle')} description={t('library.emptyCopy')} actionLabel={t('library.start')} actionTo="/plan" /></div>
  }

  return (
    <div className="page-container library-page">
      <header className="page-heading">
        <span className="eyebrow"><BookOpen size={15} />{t('library.eyebrow')}</span>
        <h1>{t('library.title')}</h1>
        {!!history.length && <small>{t('libraryHistory.count', { count: history.length })}</small>}
      </header>

      {historyLoading && !history.length && (
        <div className="library-state" role="status"><LoaderCircle className="spin" size={24} />{t('libraryHistory.loading')}</div>
      )}

      {historyError && !history.length && (
        <div className="library-state library-state--error" role="alert">
          <span>{t('libraryHistory.loadFailed')}</span>
          <button className="button button--secondary" type="button" onClick={() => void loadTripHistory()}><RefreshCw size={16} />{t('libraryHistory.retry')}</button>
        </div>
      )}

      {!!history.length && (
        <div className="library-history">
          {history.map((item, index) => {
            const city = item.cities.join(' · ')
            const opening = openingPlanId === item.plan_id
            return (
              <button
                className="library-history__item"
                key={item.plan_id}
                type="button"
                disabled={openingPlanId !== null}
                aria-label={t('libraryHistory.openNamed', { city })}
                onClick={() => void openPlan(item.plan_id)}
              >
                <span className="library-history__index">{String(index + 1).padStart(2, '0')}</span>
                <span className="library-history__content">
                  <strong>{city}</strong>
                  <span className="library-history__meta">
                    <span><CalendarDays size={14} />{item.start_date} - {item.end_date}</span>
                    <span>{t('libraryHistory.days', { count: item.days_count })}</span>
                    <span><Users size={14} />{t('libraryHistory.travelers', { count: item.travelers })}</span>
                    <span>{t('libraryHistory.created', { date: formatCreatedAt(item.created_at) })}</span>
                  </span>
                </span>
                {opening ? <LoaderCircle className="spin" size={19} /> : <ArrowUpRight size={19} />}
              </button>
            )
          })}
        </div>
      )}

      {openError && <div className="inline-alert inline-alert--error" role="alert">{t('libraryHistory.openFailed')}</div>}
    </div>
  )
}
