import { useEffect } from 'react'
import { AlertCircle, Check, Circle, Database, LoaderCircle, MapPinned, NotebookTabs, Sparkles } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Link, useNavigate } from 'react-router-dom'
import { useTripStore } from '../stores/tripStore'

export function PlanningView() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const draft = useTripStore((state) => state.draft)
  const stage = useTripStore((state) => state.planningStage)
  const error = useTripStore((state) => state.error)
  const runPlanning = useTripStore((state) => state.runPlanning)

  useEffect(() => {
    let active = true
    void runPlanning().then((success) => {
      if (active && success) navigate('/results', { replace: true })
    })
    return () => { active = false }
  }, [navigate, runPlanning])

  const enrichmentActive = stage === 'enriching'

  return (
    <div className="processing-page">
      <div className="processing-page__visual"><img src="/assets/travel/travelmind-hero.jpg" alt="" /></div>
      <section className="processing-panel">
        {stage === 'error' ? <AlertCircle className="processing-panel__icon processing-panel__icon--error" size={32} /> : <LoaderCircle className="processing-panel__icon spin" size={32} />}
        <span className="eyebrow">{t('planning.eyebrow')}</span>
        <h1>{stage === 'error' ? t('planning.failed') : t('planning.title', { city: draft.city })}</h1>
        <p>{error || t('planning.copy')}</p>
        <ol className="processing-steps">
          <li className={stage === 'extracting' ? 'is-active' : 'is-done'}><NotebookTabs />{t('pipeline.search')}<StepIcon active={stage === 'extracting'} done={enrichmentActive || stage === 'complete'} /></li>
          <li className={stage === 'extracting' ? 'is-active' : 'is-done'}><Sparkles />{t('pipeline.extract')}<StepIcon active={stage === 'extracting'} done={enrichmentActive || stage === 'complete'} /></li>
          <li className={enrichmentActive ? 'is-active' : stage === 'complete' ? 'is-done' : ''}><MapPinned />{t('pipeline.poi')}<StepIcon active={enrichmentActive} done={stage === 'complete'} /></li>
          <li className={enrichmentActive ? 'is-active' : stage === 'complete' ? 'is-done' : ''}><Database />{t('pipeline.persist')}<StepIcon active={enrichmentActive} done={stage === 'complete'} /></li>
        </ol>
        {stage === 'error' && <Link className="button button--primary" to="/plan">{t('planning.back')}</Link>}
      </section>
    </div>
  )
}

function StepIcon({ active, done }: { active: boolean; done: boolean }) {
  if (done) return <Check className="step-state" size={16} />
  if (active) return <LoaderCircle className="step-state spin" size={16} />
  return <Circle className="step-state" size={14} />
}
