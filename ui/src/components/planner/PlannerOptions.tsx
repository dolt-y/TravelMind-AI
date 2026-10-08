import { Car, Footprints, TrainFront, Users } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import type { TripDraft } from '../../stores/tripStore'

interface PlannerOptionsProps {
  draft: TripDraft
  updateDraft: (patch: Partial<TripDraft>) => void
  section: 'travel' | 'details'
}

export function PlannerOptions({ draft, updateDraft, section }: PlannerOptionsProps) {
  const { t } = useTranslation()

  return section === 'travel' ? (
    <>
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
              aria-pressed={draft.transportation === value}
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
    </>
  ) : (
    <>
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
          onChange={(event) => updateDraft({ language: event.target.value as TripDraft['language'] })}
        >
          <option value="zh">中文</option>
          <option value="en">English</option>
          <option value="ja">日本語</option>
        </select>
      </label>
    </>
  )
}
