import { CalendarCheck, CloudSun, MapPinned, NotebookTabs, Route, Sparkles } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { PlannerForm } from '../components/planner/PlannerForm'

export function PlanView() {
  const { t } = useTranslation()
  const navigate = useNavigate()

  return (
    <div className="page-container plan-page">
      <header className="page-heading"><span className="eyebrow"><Sparkles size={15} />{t('plan.eyebrow')}</span><h1>{t('plan.title')}</h1><p>{t('plan.copy')}</p></header>
      <div className="plan-layout">
        <section className="form-surface"><PlannerForm onSubmit={() => navigate('/plan/running')} /></section>
        <aside className="pipeline-panel">
          <h2>{t('plan.pipelineTitle')}</h2>
          <ol>
            <li><NotebookTabs /><strong>{t('pipeline.search')}</strong></li>
            <li><MapPinned /><strong>{t('pipeline.poi')}</strong></li>
            <li><CloudSun /><strong>{t('pipeline.context')}</strong></li>
            <li><CalendarCheck /><strong>{t('pipeline.itinerary')}</strong></li>
            <li><Route /><strong>{t('pipeline.routes')}</strong></li>
          </ol>
        </aside>
      </div>
    </div>
  )
}
