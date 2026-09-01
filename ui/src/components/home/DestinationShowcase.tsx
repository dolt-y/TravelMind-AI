import { ArrowRight } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { destinationPresets } from '../../data/destinations'
import { useTripStore } from '../../stores/tripStore'

export function DestinationShowcase() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const applyPreset = useTripStore((state) => state.applyPreset)

  function choosePreset(city: string, keywords: string) {
    applyPreset(city, keywords)
    navigate('/plan')
  }

  return (
    <section className="destination-showcase" id="destinations">
      <header className="home-section-title">
        <span>{t('home.popularEyebrow')}</span>
        <h2>{t('home.popularTitle')}</h2>
        <i aria-hidden="true" />
      </header>
      <div className="destination-showcase__list">
        {destinationPresets.map((item) => (
          <button key={item.city} type="button" onClick={() => choosePreset(item.city, item.keywords)}>
            <img src={item.image} alt="" />
            <span>
              <strong>{t(item.cityKey)}</strong>
              <small>{t(item.keywordsKey)}</small>
            </span>
          </button>
        ))}
        <button className="destination-showcase__more" type="button" onClick={() => navigate('/inspiration')} title={t('common.viewAll')}>
          <ArrowRight size={22} aria-hidden="true" />
        </button>
      </div>
    </section>
  )
}
