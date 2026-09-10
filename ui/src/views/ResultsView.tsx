import { BedDouble, Bookmark, CalendarDays, CloudSun, Lightbulb, MapPinned, Route, RotateCcw, Soup } from 'lucide-react'
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
        <div><span className="eyebrow"><Bookmark size={15} />{t('results.saved')}</span><h1>{t('results.title', { city: plan.cities.join(' · ') })}</h1><p>{t('results.summary', { start: plan.start_date, end: plan.end_date, days: plan.days.length })}</p></div>
        <Link className="button button--secondary" to="/plan"><RotateCcw size={17} />{t('results.retry')}</Link>
      </header>
      {plan.warnings.map((warning) => <div className="inline-alert" key={warning}>{warning}</div>)}

      <div className="result-visual-grid">
        <TripMap days={plan.days} />
        <BudgetChart budget={plan.budget} />
      </div>

      <section className="result-section">
        <div className="section-heading section-heading--compact"><div><span className="eyebrow">{t('results.itineraryEyebrow')}</span><h2>{t('results.itinerary')}</h2></div><span>{plan.days.length}</span></div>
        <div className="day-plan-list">
          {plan.days.map((day) => (
            <article className="day-plan" key={day.date}>
              <header className="day-plan__header">
                <div><span>{t('results.day', { day: day.day_index })}</span><h3>{day.city}</h3><p><CalendarDays size={14} />{day.date}{day.is_transfer_day ? ` · ${t('results.transferDay')}` : ''}</p></div>
                {day.weather && <div className="day-weather"><CloudSun size={21} /><strong>{day.weather.day_weather}</strong><span>{day.weather.night_temperature ?? '--'}° / {day.weather.day_temperature ?? '--'}°</span></div>}
              </header>
              <p className="day-plan__description">{day.description}</p>
              {day.transfer_info && <p className="transfer-note"><Route size={15} />{day.transfer_info}</p>}
              <div className="attraction-grid">
                {day.attractions.map((attraction, index) => {
                  const identity = attraction.poi_id || `${day.date}-${attraction.name}-${index}`
                  return <AttractionCard key={identity} attraction={attraction} favorite={favorites.includes(identity)} onToggleFavorite={() => toggleFavorite(identity)} />
                })}
              </div>
              {!!day.routes.length && <div className="route-list"><h4><Route size={16} />{t('results.routes')}</h4>{day.routes.map((segment) => <div key={`${segment.origin_name}-${segment.destination_name}`}><strong>{segment.origin_name} → {segment.destination_name}</strong><span>{(segment.route.distance_meters / 1000).toFixed(1)} km · {Math.ceil(segment.route.duration_seconds / 60)} {t('common.minute')}</span></div>)}</div>}
              <div className="day-plan__details">
                <div><h4><Soup size={16} />{t('results.meals')}</h4>{day.meals.map((meal) => <p key={meal.type}><strong>{t(`results.mealTypes.${meal.type}`)}</strong><span>{meal.name}{meal.estimated_cost ? ` · ¥${meal.estimated_cost}` : ''}</span></p>)}</div>
                <div><h4><BedDouble size={16} />{t('results.stay')}</h4>{day.hotel ? <p><strong>{day.hotel.name}</strong><span>{day.hotel.address || t('results.addressPending')}</span></p> : <p>{t('results.hotelEmpty')}</p>}</div>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="trip-advice">
        <Lightbulb size={22} aria-hidden="true" />
        <div><h2>{t('results.advice')}</h2><p>{plan.overall_suggestions}</p></div>
      </section>
      <small className="record-id">ID: {plan.plan_id}</small>
    </div>
  )
}
