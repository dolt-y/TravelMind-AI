import type { FormEvent } from 'react'
import { ArrowRight, MapPin, Sparkles } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useTripStore } from '../../stores/tripStore'

interface PlannerFormProps {
  mode?: 'hero' | 'full'
  onSubmit: () => void
}

export function PlannerForm({ mode = 'full', onSubmit }: PlannerFormProps) {
  const { t } = useTranslation()
  const draft = useTripStore((state) => state.draft)
  const updateDraft = useTripStore((state) => state.updateDraft)

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (draft.city.trim()) onSubmit()
  }

  return (
    <form className={`planner-form planner-form--${mode}`} onSubmit={submit}>
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
      {mode === 'full' && (
        <>
          <label className="field">
            <span>{t('planner.noteCount')}</span>
            <select
              value={draft.noteLimit}
              onChange={(event) => updateDraft({ noteLimit: Number(event.target.value) })}
            >
              {[2, 4, 6, 8].map((count) => (
                <option key={count} value={count}>{t('planner.notes', { count })}</option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>{t('planner.resultLanguage')}</span>
            <select
              value={draft.language}
              onChange={(event) => updateDraft({ language: event.target.value as 'zh' | 'en' | 'ja' })}
            >
              <option value="zh">中文</option>
              <option value="en">English</option>
              <option value="ja">日本語</option>
            </select>
          </label>
        </>
      )}
      <button className="button button--accent planner-form__submit" type="submit">
        {t('planner.submit')}
        <ArrowRight size={18} aria-hidden="true" />
      </button>
    </form>
  )
}
