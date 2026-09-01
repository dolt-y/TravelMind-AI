import { Check, Database, MapPinned, NotebookTabs, Sparkles } from 'lucide-react'
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
          <span className="eyebrow">{t('plan.pipelineEyebrow')}</span>
          <h2>{t('plan.pipelineTitle')}</h2>
          <p>{t('plan.pipelineCopy')}</p>
          <ol>
            <li><NotebookTabs /><div><strong>{t('pipeline.search')}</strong><span>{t('pipeline.searchCopy')}</span></div><Check /></li>
            <li><Sparkles /><div><strong>{t('pipeline.extract')}</strong><span>{t('pipeline.extractCopy')}</span></div><Check /></li>
            <li><MapPinned /><div><strong>{t('pipeline.poi')}</strong><span>{t('pipeline.poiCopy')}</span></div><Check /></li>
            <li><Database /><div><strong>{t('pipeline.persist')}</strong><span>{t('pipeline.persistCopy')}</span></div><Check /></li>
          </ol>
        </aside>
      </div>
    </div>
  )
}
