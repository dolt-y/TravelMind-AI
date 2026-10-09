import { CircleAlert, Download, LoaderCircle, MapPinned, RotateCcw } from 'lucide-react'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { EmptyState } from '../components/common/EmptyState'
import { BudgetChart } from '../components/planner/BudgetChart'
import { TripDaySection } from '../components/planner/TripDaySection'
import { TripMap } from '../components/planner/TripMap'
import { exportTripPlanPdf, type ExportLanguage } from '../services/travel'
import { useTripStore } from '../stores/tripStore'

const EXPORT_LANGUAGES: ExportLanguage[] = ['zh', 'en', 'ja']

export function ResultsView() {
  const { t, i18n } = useTranslation()
  const plan = useTripStore((state) => state.plan)
  const favorites = useTripStore((state) => state.favoritePoiIds)
  const toggleFavorite = useTripStore((state) => state.toggleFavorite)
  const [selectedDayIndex, setSelectedDayIndex] = useState(0)
  const [exporting, setExporting] = useState(false)
  const [exportFailed, setExportFailed] = useState(false)

  if (!plan) {
    return <div className="page-container"><EmptyState icon={MapPinned} title={t('results.emptyTitle')} description={t('results.emptyCopy')} actionLabel={t('results.start')} actionTo="/plan" /></div>
  }

  const cover = plan.days[0]?.attractions[0]?.photos[0] || '/assets/travel/travelmind-hero.jpg'
  const currentIndex = Math.min(selectedDayIndex, Math.max(plan.days.length - 1, 0))
  const selectedDay = plan.days[currentIndex]
  const planId = plan.plan_id

  const downloadPdf = async () => {
    if (exporting) return
    const language = EXPORT_LANGUAGES.includes(i18n.language as ExportLanguage)
      ? (i18n.language as ExportLanguage)
      : 'zh'
    setExporting(true)
    setExportFailed(false)
    try {
      await exportTripPlanPdf(planId, language)
    } catch {
      setExportFailed(true)
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="page-container result-page">
      <header className="result-banner">
        <img src={cover} alt="" />
        <div className="result-banner__content">
          <span className="eyebrow">{t('results.saved')}</span>
          <h1>{t('results.title', { city: plan.cities.join(' · ') })}</h1>
          <p>{t('results.summary', { start: plan.start_date, end: plan.end_date, days: plan.days.length })}</p>
          <div className="result-banner__actions">
            <span>{t('libraryHistory.travelers', { count: plan.travelers })}</span>
            <button className="button button--secondary" type="button" disabled={exporting} onClick={() => void downloadPdf()}>
              {exporting ? <LoaderCircle className="spin" size={17} /> : <Download size={17} />}
              {t(exporting ? 'results.exporting' : 'results.exportPdf')}
            </button>
            <Link className="button button--secondary" to="/plan"><RotateCcw size={17} />{t('results.retry')}</Link>
          </div>
        </div>
      </header>
      {exportFailed && <div className="inline-alert inline-alert--error" role="alert">{t('results.exportFailed')}</div>}
      {!!plan.warnings.length && (
        <section className="result-notices" aria-label={t('results.notices')}>
          <CircleAlert size={18} aria-hidden="true" />
          <div>
            <strong>{t('results.notices')}</strong>
            <ul>{plan.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul>
          </div>
        </section>
      )}
      <div className="result-workspace">
        <section className="result-workspace__main" aria-label={t('results.itinerary')}>
          <div className="section-heading section-heading--compact"><div><span className="eyebrow">{t('results.itineraryEyebrow')}</span><h2>{t('results.itinerary')}</h2></div><span className="result-day-count">{t('results.dayCount', { count: plan.days.length })}</span></div>
          <nav className="result-day-nav" aria-label={t('tripVisuals.map.days')}>
            {plan.days.map((day, index) => <button className={index === currentIndex ? 'is-active' : ''} key={day.date} type="button" onClick={() => setSelectedDayIndex(index)} aria-current={index === currentIndex ? 'true' : undefined}><span>{String(day.day_index).padStart(2, '0')}</span>{day.city}<small>{day.date.slice(5)}</small></button>)}
          </nav>
          {selectedDay && <TripDaySection key={selectedDay.date} day={selectedDay} favorites={favorites} onToggleFavorite={toggleFavorite} />}
        </section>
        <aside className="result-workspace__aside">
          <TripMap days={plan.days} selectedDayIndex={currentIndex} />
          <BudgetChart budget={plan.budget} />
        </aside>
      </div>

      <section className="trip-advice">
        <div><h2>{t('results.advice')}</h2><p>{plan.overall_suggestions}</p></div>
      </section>
      <small className="record-id">ID: {plan.plan_id}</small>
    </div>
  )
}
