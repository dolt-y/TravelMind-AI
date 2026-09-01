import { MapPin, Star } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import type { HotelSearchResponse } from '../../types'

export function HotelList({ hotels }: { hotels: HotelSearchResponse | null }) {
  const { t } = useTranslation()

  if (!hotels?.data.length) {
    return <p className="data-empty">{t('results.hotelEmpty')}</p>
  }

  return (
    <div className="hotel-list">
      {hotels.data.slice(0, 6).map((hotel) => (
        <article key={hotel.id}>
          <img src={hotel.photos[0] || '/assets/travel/amalfi-coast.jpg'} alt="" loading="lazy" />
          <div>
            <h3>{hotel.name}</h3>
            <p><MapPin size={13} />{hotel.address || t('results.addressPending')}</p>
          </div>
          <div className="hotel-list__aside">
            {hotel.rating !== null && <span><Star size={13} fill="currentColor" />{hotel.rating}</span>}
            {hotel.average_price !== null && <strong>¥{hotel.average_price}<small>{t('results.perNight')}</small></strong>}
          </div>
        </article>
      ))}
    </div>
  )
}
