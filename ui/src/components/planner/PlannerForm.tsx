import type { FormEvent } from 'react'
import { ArrowRight, CalendarDays, Car, Footprints, MapPin, Sparkles, TrainFront, Users } from 'lucide-react'
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

  function updateStartDate(startDate: string) {
    updateDraft({
      startDate,
      endDate: draft.endDate < startDate ? startDate : draft.endDate,
    })
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
      {mode === 'full' && (
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
      )}
      {mode === 'full' && (
        <>
          <label className="field">
            <span>{t('planner.startDate')}</span>
            <div className="field__control">
              <CalendarDays size={18} aria-hidden="true" />
              <input
                type="date"
                value={draft.startDate}
                onChange={(event) => updateStartDate(event.target.value)}
                required
              />
            </div>
          </label>
          <label className="field">
            <span>{t('planner.endDate')}</span>
            <div className="field__control">
              <CalendarDays size={18} aria-hidden="true" />
              <input
                type="date"
                min={draft.startDate}
                value={draft.endDate}
                onChange={(event) => updateDraft({ endDate: event.target.value })}
                required
              />
            </div>
          </label>
          <fieldset className="field field--transport">
            <legend>{t('planner.transportation')}</legend>
            <div className="transport-options">
              {([
                ['walking', Footprints],
                ['transit', TrainFront],
                ['driving', Car],
              ] as const).map(([value, Icon]) => (
                <button
                  className={draft.transportation === value ? 'is-active' : ''}
                  key={value}
                  type="button"
                  onClick={() => updateDraft({ transportation: value })}
                >
                  <Icon size={16} />{t(`planner.transport.${value}`)}
                </button>
              ))}
            </div>
          </fieldset>
          <label className="field">
            <span>{t('planner.travelers')}</span>
            <div className="field__control">
              <Users size={18} aria-hidden="true" />
              <input
                type="number"
                min="1"
                max="20"
                value={draft.travelers}
                onChange={(event) => updateDraft({ travelers: Number(event.target.value) })}
                required
              />
            </div>
          </label>
          <label className="field">
            <span>{t('planner.accommodation')}</span>
            <select
              value={draft.accommodation}
              onChange={(event) => updateDraft({ accommodation: event.target.value })}
            >
              <option value="经济型酒店">{t('planner.stays.budget')}</option>
              <option value="舒适型酒店">{t('planner.stays.comfort')}</option>
              <option value="高档酒店">{t('planner.stays.premium')}</option>
              <option value="特色民宿">{t('planner.stays.local')}</option>
            </select>
          </label>
          <label className="field">
            <span>{t('planner.hotelBudget')}</span>
            <input
              type="number"
              min="0"
              step="100"
              value={draft.hotelBudgetMax}
              onChange={(event) => updateDraft({ hotelBudgetMax: Number(event.target.value) })}
            />
          </label>
          <label className="field">
            <span>{t('planner.totalBudget')}</span>
            <input
              type="number"
              min="0"
              step="500"
              value={draft.totalBudget}
              onChange={(event) => updateDraft({ totalBudget: Number(event.target.value) })}
            />
          </label>
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
        {t(mode === 'hero' ? 'home.search' : 'planner.submit')}
        <ArrowRight size={18} aria-hidden="true" />
      </button>
    </form>
  )
}
