import { Clock3, Heart, MapPin, Star, TicketCheck } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import type { Attraction } from '../../types'

interface AttractionCardProps {
  attraction: Attraction
  favorite: boolean
  onToggleFavorite: () => void
}

function formatDuration(minutes: number, hourLabel: string, minuteLabel: string) {
  if (minutes < 60) return `${minutes}${minuteLabel}`
  const hours = Math.floor(minutes / 60)
  const remainder = minutes % 60
  return remainder ? `${hours}${hourLabel} ${remainder}${minuteLabel}` : `${hours}${hourLabel}`
}

export function AttractionCard({ attraction, favorite, onToggleFavorite }: AttractionCardProps) {
  const { t } = useTranslation()
  const title = attraction.name_zh || attraction.name || attraction.name_en
  const image = attraction.photos[0] || '/assets/travel/travelmind-hero.jpg'

  return (
    <article className="attraction-card">
      <div className="attraction-card__media">
        <img src={image} alt="" loading="lazy" />
        <button
          className={`icon-button attraction-card__favorite${favorite ? ' is-active' : ''}`}
          type="button"
          onClick={onToggleFavorite}
          title={favorite ? t('results.unfavorite') : t('results.favorite')}
        >
          <Heart size={18} fill={favorite ? 'currentColor' : 'none'} aria-hidden="true" />
        </button>
      </div>
      <div className="attraction-card__body">
        <div className="attraction-card__heading">
          <h3>{title}</h3>
          {attraction.rating !== null && (
            <span className="rating"><Star size={14} fill="currentColor" />{attraction.rating}</span>
          )}
        </div>
        <p>{attraction.reason}</p>
        <div className="attraction-card__meta">
          <span><Clock3 size={14} />{formatDuration(attraction.duration, t('common.hour'), t('common.minute'))}</span>
          {attraction.reservation_required && <span><TicketCheck size={14} />{t('results.reservation')}</span>}
        </div>
        <div className="attraction-card__address">
          <MapPin size={14} />
          <span>{attraction.address || t('results.addressPending')}</span>
        </div>
      </div>
    </article>
  )
}
