import { Sparkles } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { PlannerForm } from '../components/planner/PlannerForm'
import { PlannerSummary } from '../components/planner/PlannerSummary'

export function PlanView() {
  const { t } = useTranslation()
  const navigate = useNavigate()

  return (
    <div className="page-container plan-page">
      <header className="page-heading page-heading--split">
        <div><span className="eyebrow"><Sparkles size={15} />{t('plan.eyebrow')}</span><h1>{t('plan.title')}</h1></div>
        <p>{t('plan.copy')}</p>
      </header>
      <div className="plan-layout">
        <section className="form-surface"><PlannerForm onSubmit={() => navigate('/plan/running')} /></section>
        <PlannerSummary />
      </div>
    </div>
  )
}
