import { ArrowUpRight, BookOpen, CalendarDays, ChevronLeft, ChevronRight, LoaderCircle, RefreshCw, Users } from 'lucide-react'
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
  const historyErrorPage = useTripStore((state) => state.historyErrorPage)
  const historyPage = useTripStore((state) => state.historyPage)
  const historyPageSize = useTripStore((state) => state.historyPageSize)
  const historyTotal = useTripStore((state) => state.historyTotal)
  const historyTotalPages = useTripStore((state) => state.historyTotalPages)
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

  const visiblePages = getVisiblePages(historyPage, historyTotalPages)

  if (!historyLoading && !historyErrorPage && !history.length) {
    return <div className="page-container library-page library-page--empty"><EmptyState icon={BookOpen} title={t('library.emptyTitle')} description={t('library.emptyCopy')} actionLabel={t('library.start')} actionTo="/plan" /></div>
  }

  return (
    <div className="page-container library-page">
      <header className="page-heading page-heading--split library-heading">
        <div>
          <span className="eyebrow"><BookOpen size={15} />{t('library.eyebrow')}</span>
          <h1>{t('library.title')}</h1>
        </div>
        {!!historyTotal && (
          <p>{historyLoading && <LoaderCircle className="spin" size={14} />}{t('libraryHistory.summary', { total: historyTotal })}</p>
        )}
      </header>

      {historyLoading && !history.length && (
        <div className="library-state" role="status"><LoaderCircle className="spin" size={24} />{t('libraryHistory.loading')}</div>
      )}

      {historyErrorPage && !history.length && (
        <div className="library-state library-state--error" role="alert">
          <span>{t('libraryHistory.loadFailed')}</span>
          <button className="button button--secondary" type="button" onClick={() => void loadTripHistory(historyErrorPage)}><RefreshCw size={16} />{t('libraryHistory.retry')}</button>
        </div>
      )}

      {!!history.length && (
        <div className={`library-history${historyLoading ? ' is-loading' : ''}`} aria-busy={historyLoading}>
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
                <span className="library-history__index">{String((historyPage - 1) * historyPageSize + index + 1).padStart(2, '0')}</span>
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

      {historyTotalPages > 1 && (
        <nav className="library-pagination" aria-label={t('libraryHistory.pagination')}>
          <span>{t('libraryHistory.pageStatus', { page: historyPage, totalPages: historyTotalPages })}</span>
          <div>
            <button className="icon-button" type="button" disabled={historyLoading || historyPage === 1} onClick={() => void loadTripHistory(historyPage - 1)} title={t('libraryHistory.previous')} aria-label={t('libraryHistory.previous')}><ChevronLeft size={17} /></button>
            {visiblePages.map((page) => (
              <button className={`library-pagination__page${page === historyPage ? ' is-active' : ''}`} key={page} type="button" disabled={historyLoading} onClick={() => void loadTripHistory(page)} aria-current={page === historyPage ? 'page' : undefined} aria-label={t('libraryHistory.pageLabel', { page })}>{page}</button>
            ))}
            <button className="icon-button" type="button" disabled={historyLoading || historyPage === historyTotalPages} onClick={() => void loadTripHistory(historyPage + 1)} title={t('libraryHistory.next')} aria-label={t('libraryHistory.next')}><ChevronRight size={17} /></button>
          </div>
        </nav>
      )}

      {historyErrorPage && !!history.length && (
        <div className="inline-alert inline-alert--error library-pagination-error" role="alert">
          <span>{t('libraryHistory.loadFailed')}</span>
          <button className="button button--secondary" type="button" onClick={() => void loadTripHistory(historyErrorPage)}><RefreshCw size={16} />{t('libraryHistory.retry')}</button>
        </div>
      )}

      {openError && <div className="inline-alert inline-alert--error" role="alert">{t('libraryHistory.openFailed')}</div>}
    </div>
  )
}

function getVisiblePages(currentPage: number, totalPages: number): number[] {
  if (totalPages <= 5) return Array.from({ length: totalPages }, (_, index) => index + 1)
  const start = Math.min(Math.max(currentPage - 2, 1), totalPages - 4)
  return Array.from({ length: 5 }, (_, index) => start + index)
}
