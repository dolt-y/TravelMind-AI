import { useRef, useState, type FormEvent } from 'react'
import { ArrowLeft, ArrowRight, CalendarDays, MapPin, Sparkles } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useTripStore } from '../../stores/tripStore'
import { PlannerOptions } from './PlannerOptions'

interface PlannerFormProps {
  mode?: 'hero' | 'full'
  onSubmit: () => void
}

const stepKeys = ['journey', 'style', 'details'] as const

export function PlannerForm({ mode = 'full', onSubmit }: PlannerFormProps) {
  const { t } = useTranslation()
  const draft = useTripStore((state) => state.draft)
  const updateDraft = useTripStore((state) => state.updateDraft)
  const formRef = useRef<HTMLFormElement>(null)
  const [step, setStep] = useState(0)
  const [furthestStep, setFurthestStep] = useState(0)

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!draft.city.trim()) return
    if (mode === 'full' && step < stepKeys.length - 1) {
      setStep(step + 1)
      setFurthestStep((current) => Math.max(current, step + 1))
      return
    }
    if (mode === 'full' && (!draft.city.trim() || !draft.startDate || !draft.endDate || draft.endDate < draft.startDate)) {
      setStep(0)
      return
    }
    if (mode === 'full' && (!Number.isInteger(draft.travelers) || draft.travelers < 1 || draft.travelers > 20)) {
      setStep(1)
      return
    }
    onSubmit()
  }

  function goToStep(index: number) {
    if (index > step && !formRef.current?.reportValidity()) return
    setStep(index)
  }

  function updateStartDate(startDate: string) {
    updateDraft({
      startDate,
      endDate: draft.endDate < startDate ? startDate : draft.endDate,
    })
  }

  const destinationField = (
    <label className="field field--destination">
      <span>{t('planner.destination')}</span>
      <div className="field__control">
        <MapPin size={18} aria-hidden="true" />
        <input
          value={draft.city}
          onChange={(event) => updateDraft({ city: event.target.value })}
          placeholder={t('planner.destinationPlaceholder')}
          required
        />
      </div>
    </label>
  )

  return (
    <form ref={formRef} className={`planner-form planner-form--${mode}`} onSubmit={submit}>
      {mode === 'hero' ? (
        <>
          {destinationField}
          <button className="button button--accent planner-form__submit" type="submit">
            {t('home.search')}<ArrowRight size={18} aria-hidden="true" />
          </button>
        </>
      ) : (
        <>
          <nav className="planner-step-nav" aria-label={t('plan.title')}>
            {stepKeys.map((key, index) => (
              <button
                key={key}
                type="button"
                className={index === step ? 'is-active' : ''}
                disabled={index > furthestStep}
                aria-current={index === step ? 'step' : undefined}
                onClick={() => goToStep(index)}
              >
                <span>{String(index + 1).padStart(2, '0')}</span>
                {t(`planner.groups.${key}`)}
              </button>
            ))}
          </nav>
          <section className="planner-step" aria-labelledby="planner-step-title">
            <header className="planner-step__heading">
              <span>{String(step + 1).padStart(2, '0')} / 03</span>
              <h2 id="planner-step-title">{t(`planner.groups.${stepKeys[step]}`)}</h2>
            </header>
            <div className="planner-step__fields">
              {step === 0 && (
                <>
                  {destinationField}
                  <label className="field field--preferences">
                    <span>{t('planner.preferences')}</span>
                    <div className="field__control">
                      <Sparkles size={18} aria-hidden="true" />
                      <input
                        value={draft.keywords}
                        onChange={(event) => updateDraft({ keywords: event.target.value })}
                        placeholder={t('planner.preferencesPlaceholder')}
                      />
                    </div>
                  </label>
                  <label className="field field--date">
                    <span>{t('planner.startDate')}</span>
                    <div className="field__control">
                      <CalendarDays size={18} aria-hidden="true" />
                      <input type="date" value={draft.startDate} onChange={(event) => updateStartDate(event.target.value)} required />
                    </div>
                  </label>
                  <label className="field field--date">
                    <span>{t('planner.endDate')}</span>
                    <div className="field__control">
                      <CalendarDays size={18} aria-hidden="true" />
                      <input type="date" min={draft.startDate} value={draft.endDate} onChange={(event) => updateDraft({ endDate: event.target.value })} required />
                    </div>
                  </label>
                </>
              )}
              {step === 1 && <PlannerOptions draft={draft} updateDraft={updateDraft} section="travel" />}
              {step === 2 && <PlannerOptions draft={draft} updateDraft={updateDraft} section="details" />}
            </div>
          </section>
          <div className="planner-form__actions">
            {step > 0 && <button className="button button--secondary" type="button" onClick={() => setStep(step - 1)}><ArrowLeft size={17} />{t('planner.previous')}</button>}
            <button className="button button--accent planner-form__submit" type="submit">
              {t(step === stepKeys.length - 1 ? 'planner.submit' : 'planner.next')}<ArrowRight size={18} aria-hidden="true" />
            </button>
          </div>
        </>
      )}
    </form>
  )
}
