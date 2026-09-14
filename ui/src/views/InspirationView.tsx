import { ArrowUpRight, Compass } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { destinationPresets } from '../data/destinations'
import { useTripStore } from '../stores/tripStore'

export function InspirationView() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const applyPreset = useTripStore((state) => state.applyPreset)

  return (
    <div className="page-container">
      <header className="page-heading page-heading--split">
        <div><span className="eyebrow"><Compass size={15} />{t('inspiration.eyebrow')}</span><h1>{t('inspiration.title')}</h1></div>
        <p>{t('inspiration.copy')}</p>
      </header>
      <div className="inspiration-list">
        {destinationPresets.map((item) => (
          <button className="inspiration-card" key={item.city} type="button" onClick={() => { applyPreset(item.city, item.keywords); navigate('/plan') }}>
            <img src={item.image} alt="" />
            <span className="inspiration-card__shade" aria-hidden="true" />
            <span className="inspiration-card__copy"><small>{t(item.keywordsKey)}</small><strong>{t(item.cityKey)}</strong></span>
            <span className="inspiration-card__action" title={t('inspiration.use')}><ArrowUpRight size={19} /></span>
          </button>
        ))}
      </div>
    </div>
  )
}
