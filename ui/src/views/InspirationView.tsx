import { ArrowRight, Compass } from 'lucide-react'
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
      <header className="page-heading"><span className="eyebrow"><Compass size={15} />{t('inspiration.eyebrow')}</span><h1>{t('inspiration.title')}</h1><p>{t('inspiration.copy')}</p></header>
      <div className="inspiration-list">
        {destinationPresets.map((item, index) => (
          <article key={item.city}>
            <img src={item.image} alt="" />
            <span className="inspiration-list__index">0{index + 1}</span>
            <div><h2>{t(item.cityKey)}</h2><p>{t(item.keywordsKey)}</p></div>
            <button className="icon-button" type="button" title={t('inspiration.use')} onClick={() => { applyPreset(item.city, item.keywords); navigate('/plan') }}><ArrowRight /></button>
          </article>
        ))}
      </div>
    </div>
  )
}
