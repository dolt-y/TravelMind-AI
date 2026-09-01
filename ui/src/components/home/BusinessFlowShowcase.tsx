import {
  BookmarkCheck,
  ChevronRight,
  CloudSun,
  MapPinned,
  NotebookText,
  Route,
  Search,
  SlidersHorizontal,
} from 'lucide-react'
import { useTranslation } from 'react-i18next'

const flowSteps = [
  { key: 'needs', icon: SlidersHorizontal },
  { key: 'inspiration', icon: Search },
  { key: 'places', icon: MapPinned },
  { key: 'details', icon: CloudSun },
  { key: 'itinerary', icon: Route },
  { key: 'refine', icon: BookmarkCheck },
] as const

export function BusinessFlowShowcase() {
  const { t } = useTranslation()

  return (
    <section className="business-flow">
      <header className="business-flow__heading">
        <span>{t('home.flowEyebrow')}</span>
        <h2>{t('home.flowTitle')}</h2>
        <i aria-hidden="true" />
        <p>{t('home.flowCopy')}</p>
        <div className="business-flow__source"><NotebookText aria-hidden="true" />{t('home.flowSource')}</div>
      </header>

      <ol className="business-flow__steps">
        {flowSteps.map(({ key, icon: Icon }, index) => (
          <li key={key}>
            <span className="business-flow__index">{String(index + 1).padStart(2, '0')}</span>
            <span className="business-flow__icon"><Icon aria-hidden="true" /></span>
            <div>
              <strong>{t(`home.flowSteps.${key}`)}</strong>
              <small>{t(`home.flowSteps.${key}Copy`)}</small>
            </div>
            {index < flowSteps.length - 1 && <ChevronRight className="business-flow__arrow" aria-hidden="true" />}
          </li>
        ))}
      </ol>
    </section>
  )
}
