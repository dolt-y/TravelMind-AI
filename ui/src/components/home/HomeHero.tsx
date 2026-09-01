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
          <h1>{t('home.title')}</h1>
          {/* <p>{t('home.subtitle')}</p> */}
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
      <div className="home-hero__waves" aria-hidden="true">
        <svg className="home-hero__wave home-hero__wave--back" viewBox="0 0 1440 120" preserveAspectRatio="none">
          <path d="M0 55C120 20 240 20 360 55C480 90 600 90 720 55C840 20 960 20 1080 55C1200 90 1320 90 1440 55V120H0Z" />
        </svg>
        <svg className="home-hero__wave home-hero__wave--front" viewBox="0 0 1440 120" preserveAspectRatio="none">
          <path d="M0 55C120 20 240 20 360 55C480 90 600 90 720 55C840 20 960 20 1080 55C1200 90 1320 90 1440 55V120H0Z" />
        </svg>
      </div>
    </section>
  )
}
