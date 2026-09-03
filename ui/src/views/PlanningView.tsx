import { useEffect } from 'react'
import { AlertCircle, CalendarCheck, Check, Circle, CloudSun, LoaderCircle, NotebookTabs, Route } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Link, useNavigate } from 'react-router-dom'
import { useTripStore } from '../stores/tripStore'

export function PlanningView() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const draft = useTripStore((state) => state.draft)
  const stage = useTripStore((state) => state.planningStage)
  const error = useTripStore((state) => state.error)
  const errorCode = useTripStore((state) => state.errorCode)
  const currentStage = useTripStore((state) => state.currentStage)
  const progress = useTripStore((state) => state.progress)
  const clearPlanningError = useTripStore((state) => state.clearPlanningError)
  const runPlanning = useTripStore((state) => state.runPlanning)

  useEffect(() => {
    let active = true
    void runPlanning().then((success) => {
      if (active && success) navigate('/results', { replace: true })
    })
    return () => { active = false }
  }, [navigate, runPlanning])

  useEffect(() => {
    if (stage !== 'error' || errorCode !== 'XHS_AUTH_REQUIRED') return
    clearPlanningError()
    navigate('/admin/integrations/xhs?returnTo=%2Fplan%2Frunning', { replace: true })
  }, [clearPlanningError, errorCode, navigate, stage])

  const steps = [
    { icon: NotebookTabs, label: t('pipeline.search'), stages: ['submitted', 'collecting_attractions'] },
    { icon: CloudSun, label: t('pipeline.context'), stages: ['collecting_weather', 'collecting_hotels'] },
    { icon: CalendarCheck, label: t('pipeline.itinerary'), stages: ['composing_itinerary'] },
    { icon: Route, label: t('pipeline.routes'), stages: ['calculating_routes'] },
    { icon: Check, label: t('pipeline.finalize'), stages: ['validating_plan', 'completed'] },
  ]
  const activeIndex = Math.max(0, steps.findIndex((item) => item.stages.includes(currentStage)))

  return (
    <div className="processing-page">
      <div className="processing-page__visual"><img src="/assets/travel/travelmind-hero.jpg" alt="" /></div>
      <section className="processing-panel">
        {stage === 'error' ? <AlertCircle className="processing-panel__icon processing-panel__icon--error" size={32} /> : <LoaderCircle className="processing-panel__icon spin" size={32} />}
        <span className="eyebrow">{t('planning.eyebrow')}</span>
        <h1>{stage === 'error' ? t('planning.failed') : t('planning.title', { city: draft.city })}</h1>
        <p>{error || t('planning.copy')}</p>
        {stage !== 'error' && (
          <div className="planning-progress" aria-label={t('planning.progress', { progress })}>
            <span style={{ width: `${progress}%` }} />
          </div>
        )}
        <ol className="processing-steps">
          {steps.map((item, index) => {
            const Icon = item.icon
            const done = stage === 'complete' || index < activeIndex
            const active = stage !== 'error' && index === activeIndex
            return <li className={done ? 'is-done' : active ? 'is-active' : ''} key={item.label}><Icon />{item.label}<StepIcon active={active} done={done} /></li>
          })}
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
