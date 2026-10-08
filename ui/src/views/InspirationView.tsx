import { useState } from 'react'
import { ArrowUpRight, Compass } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { destinationPresets } from '../data/destinations'
import { useTripStore } from '../stores/tripStore'

export function InspirationView() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const applyPreset = useTripStore((state) => state.applyPreset)
  const [selectedIndex, setSelectedIndex] = useState(0)
  const selected = destinationPresets[selectedIndex]

  function useDestination() {
    applyPreset(selected.city, selected.keywords)
    navigate('/plan')
  }

  return (
    <div className="page-container">
      <header className="page-heading page-heading--split">
        <div><span className="eyebrow"><Compass size={15} />{t('inspiration.eyebrow')}</span><h1>{t('inspiration.title')}</h1></div>
        <p>{t('inspiration.copy')}</p>
      </header>
      <div className="inspiration-stage">
        <section className="inspiration-feature" aria-label={t(selected.cityKey)}>
          <img src={selected.image} alt="" />
          <div className="inspiration-feature__content">
            <span className="eyebrow">0{selectedIndex + 1} / 0{destinationPresets.length}</span>
            <span>{t(selected.keywordsKey)}</span>
            <h2>{t(selected.cityKey)}</h2>
            <button className="button button--accent" type="button" onClick={useDestination}>{t('inspiration.use')}<ArrowUpRight size={18} /></button>
          </div>
        </section>
        <nav className="inspiration-choices" aria-label={t('inspiration.title')}>
          {destinationPresets.map((item, index) => (
            <button key={item.city} className={index === selectedIndex ? 'is-active' : ''} type="button" onClick={() => setSelectedIndex(index)} aria-current={index === selectedIndex ? 'true' : undefined}>
              <span>{String(index + 1).padStart(2, '0')}</span>
              <strong>{t(item.cityKey)}</strong>
              <small>{t(item.keywordsKey)}</small>
              <ArrowUpRight size={17} aria-hidden="true" />
            </button>
          ))}
        </nav>
      </div>
    </div>
  )
}
