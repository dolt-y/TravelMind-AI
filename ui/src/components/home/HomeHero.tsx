import { Flame } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { PlannerForm } from '../planner/PlannerForm'
import { destinationPresets } from '../../data/destinations'
import { useTripStore } from '../../stores/tripStore'

export function HomeHero() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const applyPreset = useTripStore((state) => state.applyPreset)

  function choosePreset(city: string, keywords: string) {
    applyPreset(city, keywords)
    navigate('/plan')
  }

  return (
    <section className="home-hero">
      <div className="home-hero__overlay" />
      <div className="home-hero__inner">
        <div className="home-hero__content">
          <span className="home-hero__eyebrow">TRAVELMIND / JOURNEY PLANNER</span>
          <h1>TravelMind</h1>
          <p>{t('home.title')}</p>
          <PlannerForm mode="hero" onSubmit={() => navigate('/plan')} />
          <div className="home-hot-searches">
            <span><Flame size={14} aria-hidden="true" />{t('home.hotSearch')}</span>
            {destinationPresets.map((item) => (
              <button key={item.city} type="button" onClick={() => choosePreset(item.city, item.keywords)}>
                {t(item.cityKey)}
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
