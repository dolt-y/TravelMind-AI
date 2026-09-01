import { CloudSun, Wind } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import type { WeatherResponse } from '../../types'

export function WeatherStrip({ weather }: { weather: WeatherResponse | null }) {
  const { t } = useTranslation()

  if (!weather?.data.length) {
    return <p className="data-empty">{t('results.weatherEmpty')}</p>
  }

  return (
    <div className="weather-strip">
      {weather.data.slice(0, 4).map((day) => (
        <article key={day.date}>
          <time>{day.date.slice(5)}</time>
          <CloudSun size={22} aria-hidden="true" />
          <strong>{day.day_weather}</strong>
          <span>{day.night_temperature ?? '--'}° / {day.day_temperature ?? '--'}°</span>
          <small><Wind size={12} />{day.day_wind_direction}{day.day_wind_power}</small>
        </article>
      ))}
    </div>
  )
}
