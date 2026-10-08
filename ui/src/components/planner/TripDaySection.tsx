import { useTranslation } from 'react-i18next'
import type { TripDay } from '../../types'
import { AttractionCard } from './AttractionCard'

interface TripDaySectionProps {
  day: TripDay
  favorites: string[]
  onToggleFavorite: (poiId: string) => void
}

export function TripDaySection({ day, favorites, onToggleFavorite }: TripDaySectionProps) {
  const { t } = useTranslation()

  return (
    <article className="day-plan" id={`day-${day.day_index}`}>
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
          return <AttractionCard key={identity} attraction={attraction} favorite={favorites.includes(identity)} onToggleFavorite={() => onToggleFavorite(identity)} />
        })}
      </div>
      <div className="day-plan__support">
        {!!day.routes.length && <div className="route-list"><h4>{t('results.routes')}</h4>{day.routes.map((segment) => <div key={`${segment.origin_name}-${segment.destination_name}`}><strong>{segment.origin_name} → {segment.destination_name}</strong><span>{(segment.route.distance_meters / 1000).toFixed(1)} km · {Math.ceil(segment.route.duration_seconds / 60)} {t('common.minute')}</span></div>)}</div>}
        <div className="day-plan__detail-block"><h4>{t('results.meals')}</h4>{day.meals.map((meal) => <p key={meal.type}><strong>{t(`results.mealTypes.${meal.type}`)}</strong><span>{meal.name}{meal.estimated_cost ? ` · ¥${meal.estimated_cost}` : ''}</span></p>)}</div>
        <div className="day-plan__detail-block"><h4>{t('results.stay')}</h4>{day.hotel ? <p className="stay-summary"><strong>{day.hotel.name}</strong><span>{day.hotel.address || t('results.addressPending')}</span></p> : <p>{t('results.hotelEmpty')}</p>}</div>
      </div>
    </article>
  )
}
