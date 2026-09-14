import { CircleAlert, MapPinned, RotateCcw } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { EmptyState } from '../components/common/EmptyState'
import { AttractionCard } from '../components/planner/AttractionCard'
import { BudgetChart } from '../components/planner/BudgetChart'
import { TripMap } from '../components/planner/TripMap'
import { useTripStore } from '../stores/tripStore'

export function ResultsView() {
  const { t } = useTranslation()
  const plan = useTripStore((state) => state.plan)
  const favorites = useTripStore((state) => state.favoritePoiIds)
  const toggleFavorite = useTripStore((state) => state.toggleFavorite)

  if (!plan) {
    return <div className="page-container"><EmptyState icon={MapPinned} title={t('results.emptyTitle')} description={t('results.emptyCopy')} actionLabel={t('results.start')} actionTo="/plan" /></div>
  }

  return (
    <div className="page-container result-page">
      <header className="result-header">
        <div><span className="eyebrow">{t('results.saved')}</span><h1>{t('results.title', { city: plan.cities.join(' · ') })}</h1><p>{t('results.summary', { start: plan.start_date, end: plan.end_date, days: plan.days.length })}</p></div>
        <Link className="button button--secondary" to="/plan"><RotateCcw size={17} />{t('results.retry')}</Link>
      </header>
      {!!plan.warnings.length && (
        <section className="result-notices" aria-label={t('results.notices')}>
          <CircleAlert size={18} aria-hidden="true" />
          <div>
            <strong>{t('results.notices')}</strong>
            <ul>{plan.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul>
          </div>
        </section>
      )}

      <div className="result-visual-grid">
        <TripMap days={plan.days} />
        <BudgetChart budget={plan.budget} />
      </div>

      <section className="result-section">
        <div className="section-heading section-heading--compact"><div><span className="eyebrow">{t('results.itineraryEyebrow')}</span><h2>{t('results.itinerary')}</h2></div><span className="result-day-count">{t('results.dayCount', { count: plan.days.length })}</span></div>
        <div className="day-plan-list">
          {plan.days.map((day) => (
            <article className="day-plan" key={day.date}>
              <header className="day-plan__header">
                <div className="day-plan__identity">
                  <span className="day-plan__number" aria-hidden="true">{String(day.day_index).padStart(2, '0')}</span>
                  <div><span>{t('results.day', { day: day.day_index })}</span><h3>{day.city}</h3><p>{day.date}{day.is_transfer_day ? ` · ${t('results.transferDay')}` : ''}</p></div>
                </div>
                {day.weather && <div className="day-weather"><strong>{day.weather.day_weather}</strong><span>{day.weather.night_temperature ?? '--'}° / {day.weather.day_temperature ?? '--'}°</span></div>}
              </header>
              <p className="day-plan__description">{day.description}</p>
              {day.transfer_info && <p className="transfer-note">{day.transfer_info}</p>}
              <div className="attraction-grid">
                {day.attractions.map((attraction, index) => {
                  const identity = attraction.poi_id || `${day.date}-${attraction.name}-${index}`
                  return <AttractionCard key={identity} attraction={attraction} favorite={favorites.includes(identity)} onToggleFavorite={() => toggleFavorite(identity)} />
                })}
              </div>
              <div className="day-plan__support">
                {!!day.routes.length && <div className="route-list"><h4>{t('results.routes')}</h4>{day.routes.map((segment) => <div key={`${segment.origin_name}-${segment.destination_name}`}><strong>{segment.origin_name} → {segment.destination_name}</strong><span>{(segment.route.distance_meters / 1000).toFixed(1)} km · {Math.ceil(segment.route.duration_seconds / 60)} {t('common.minute')}</span></div>)}</div>}
                <div className="day-plan__detail-block"><h4>{t('results.meals')}</h4>{day.meals.map((meal) => <p key={meal.type}><strong>{t(`results.mealTypes.${meal.type}`)}</strong><span>{meal.name}{meal.estimated_cost ? ` · ¥${meal.estimated_cost}` : ''}</span></p>)}</div>
                <div className="day-plan__detail-block"><h4>{t('results.stay')}</h4>{day.hotel ? <p className="stay-summary"><strong>{day.hotel.name}</strong><span>{day.hotel.address || t('results.addressPending')}</span></p> : <p>{t('results.hotelEmpty')}</p>}</div>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="trip-advice">
        <div><h2>{t('results.advice')}</h2><p>{plan.overall_suggestions}</p></div>
      </section>
      <small className="record-id">ID: {plan.plan_id}</small>
    </div>
  )
}
