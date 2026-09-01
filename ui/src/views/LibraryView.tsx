import { ArrowRight, BookOpen, MapPin } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { EmptyState } from '../components/common/EmptyState'
import { useTripStore } from '../stores/tripStore'

export function LibraryView() {
  const { t } = useTranslation()
  const result = useTripStore((state) => state.result)

  if (!result) {
    return <div className="page-container"><EmptyState icon={BookOpen} title={t('library.emptyTitle')} description={t('library.emptyCopy')} actionLabel={t('library.start')} actionTo="/plan" /></div>
  }

  return (
    <div className="page-container">
      <header className="page-heading"><span className="eyebrow"><BookOpen size={15} />{t('library.eyebrow')}</span><h1>{t('library.title')}</h1><p>{t('library.copy')}</p></header>
      <article className="library-record">
        <img src={result.attractions[0]?.photos[0] || '/assets/travel/travelmind-hero.jpg'} alt="" />
        <div><span>{t('library.latest')}</span><h2>{result.city}</h2><p><MapPin size={14} />{t('library.summary', { notes: result.notes_count, places: result.attractions.length })}</p><small>{result.keywords || t('library.noPreference')}</small></div>
        <Link className="button button--primary" to="/results">{t('library.open')}<ArrowRight size={17} /></Link>
      </article>
    </div>
  )
}
