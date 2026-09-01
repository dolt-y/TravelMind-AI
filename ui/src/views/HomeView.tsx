import { ArrowRight, Database, MapPinned, NotebookTabs, Sparkles } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Link, useNavigate } from 'react-router-dom'
import { PlannerForm } from '../components/planner/PlannerForm'
import { destinationPresets } from '../data/destinations'
import { useTripStore } from '../stores/tripStore'

export function HomeView() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const applyPreset = useTripStore((state) => state.applyPreset)

  function choosePreset(city: string, keywords: string) {
    applyPreset(city, keywords)
    navigate('/plan')
  }

  return (
    <>
      <section className="home-hero">
        <div className="home-hero__overlay" />
        <div className="home-hero__content">
          <span className="eyebrow eyebrow--light"><Sparkles size={15} />{t('home.eyebrow')}</span>
          <h1>TravelMind AI</h1>
          <p>{t('home.subtitle')}</p>
          <PlannerForm mode="hero" onSubmit={() => navigate('/plan/running')} />
          <small>{t('home.sourceNote')}</small>
        </div>
        <a className="home-hero__scroll" href="#destinations">{t('home.explore')}<ArrowRight size={16} /></a>
      </section>

      <section className="section section--destinations" id="destinations">
        <div className="section-heading">
          <div><span className="eyebrow">{t('home.popularEyebrow')}</span><h2>{t('home.popularTitle')}</h2></div>
          <Link to="/inspiration">{t('common.viewAll')}<ArrowRight size={16} /></Link>
        </div>
        <div className="destination-grid">
          {destinationPresets.map((item) => (
            <button key={item.city} type="button" onClick={() => choosePreset(item.city, item.keywords)}>
              <img src={item.image} alt="" />
              <span><strong>{t(item.cityKey)}</strong><small>{t(item.keywordsKey)}</small></span>
              <ArrowRight size={18} />
            </button>
          ))}
        </div>
      </section>

      <section className="workflow-band">
        <div className="workflow-band__intro"><span className="eyebrow">{t('home.workflowEyebrow')}</span><h2>{t('home.workflowTitle')}</h2><p>{t('home.workflowCopy')}</p></div>
        <ol>
          <li><NotebookTabs /><span>01</span><strong>{t('home.workflowNotes')}</strong></li>
          <li><Sparkles /><span>02</span><strong>{t('home.workflowExtract')}</strong></li>
          <li><MapPinned /><span>03</span><strong>{t('home.workflowPoi')}</strong></li>
          <li><Database /><span>04</span><strong>{t('home.workflowSave')}</strong></li>
        </ol>
      </section>
    </>
  )
}
