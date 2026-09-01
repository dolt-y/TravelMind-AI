import { BedDouble, Bookmark, CloudSun, MapPinned, RotateCcw } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { EmptyState } from '../components/common/EmptyState'
import { AttractionCard } from '../components/planner/AttractionCard'
import { HotelList } from '../components/planner/HotelList'
import { WeatherStrip } from '../components/planner/WeatherStrip'
import { useTripStore } from '../stores/tripStore'

export function ResultsView() {
  const { t } = useTranslation()
  const result = useTripStore((state) => state.result)
  const weather = useTripStore((state) => state.weather)
  const hotels = useTripStore((state) => state.hotels)
  const warning = useTripStore((state) => state.enrichmentWarning)
  const favorites = useTripStore((state) => state.favoritePoiIds)
  const toggleFavorite = useTripStore((state) => state.toggleFavorite)

  if (!result) {
    return <div className="page-container"><EmptyState icon={MapPinned} title={t('results.emptyTitle')} description={t('results.emptyCopy')} actionLabel={t('results.start')} actionTo="/plan" /></div>
  }

  return (
    <div className="page-container result-page">
      <header className="result-header">
        <div><span className="eyebrow"><Bookmark size={15} />{t('results.saved')}</span><h1>{t('results.title', { city: result.city })}</h1><p>{t('results.summary', { notes: result.notes_count, places: result.attractions.length })}</p></div>
        <Link className="button button--secondary" to="/plan"><RotateCcw size={17} />{t('results.retry')}</Link>
      </header>
      {warning && <div className="inline-alert">{warning}</div>}

      <section className="result-section">
        <div className="section-heading section-heading--compact"><div><span className="eyebrow">{t('results.placesEyebrow')}</span><h2>{t('results.places')}</h2></div><span>{result.attractions.length}</span></div>
        {result.attractions.length ? (
          <div className="attraction-grid">
            {result.attractions.map((attraction, index) => {
              const identity = attraction.poi_id || `${attraction.name}-${index}`
              return <AttractionCard key={identity} attraction={attraction} favorite={favorites.includes(identity)} onToggleFavorite={() => toggleFavorite(identity)} />
            })}
          </div>
        ) : <p className="data-empty">{t('results.noPlaces')}</p>}
      </section>

      <div className="result-data-grid">
        <section className="data-section"><div className="data-section__heading"><CloudSun /><div><span>{t('results.liveData')}</span><h2>{t('results.weather')}</h2></div></div><WeatherStrip weather={weather} /></section>
        <section className="data-section"><div className="data-section__heading"><BedDouble /><div><span>{t('results.liveData')}</span><h2>{t('results.hotels')}</h2></div></div><HotelList hotels={hotels} /></section>
      </div>
      <small className="record-id">ID: {result.extraction_id}</small>
    </div>
  )
}
