import { Compass, Github, MapPinned, Mountain, NotebookText } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

const exploreLinks = [
  { to: '/', key: 'nav.homeLink' },
  { to: '/inspiration', key: 'nav.inspiration' },
  { to: '/plan', key: 'nav.plan' },
]

const journeyLinks = [
  { to: '/library', key: 'nav.library' },
  { to: '/settings', key: 'nav.settings' },
]

export function SiteFooter() {
  const { t } = useTranslation()
  const year = new Date().getFullYear()

  return (
    <footer className="site-footer">
      <div className="site-footer__inner">
        <div className="site-footer__content">
          <div className="site-footer__brand">
            <Link className="site-footer__brand-link" to="/" aria-label={t('nav.home')}>
              <span className="site-footer__mark"><Mountain size={21} aria-hidden="true" /></span>
              <strong>TravelMind</strong>
            </Link>
            <p>{t('footer.description')}</p>
            <span className="site-footer__tagline">{t('footer.copy')}</span>
          </div>

          <div className="site-footer__links">
            <section className="site-footer__group" aria-labelledby="footer-explore-title">
              <h2 id="footer-explore-title">{t('footer.explore')}</h2>
              <nav aria-label={t('footer.explore')}>
                {exploreLinks.map((item) => <Link key={item.to} to={item.to}>{t(item.key)}</Link>)}
              </nav>
            </section>

            <section className="site-footer__group" aria-labelledby="footer-journey-title">
              <h2 id="footer-journey-title">{t('footer.journey')}</h2>
              <nav aria-label={t('footer.journey')}>
                {journeyLinks.map((item) => <Link key={item.to} to={item.to}>{t(item.key)}</Link>)}
              </nav>
            </section>

            <section className="site-footer__group site-footer__group--sources" aria-labelledby="footer-sources-title">
              <h2 id="footer-sources-title">{t('footer.sources')}</h2>
              <ul>
                <li><NotebookText size={15} aria-hidden="true" /><span>{t('footer.sourceXhs')}</span></li>
                <li><MapPinned size={15} aria-hidden="true" /><span>{t('footer.sourceMap')}</span></li>
                <li><Compass size={15} aria-hidden="true" /><span>{t('footer.sourcePlanning')}</span></li>
              </ul>
            </section>
          </div>
        </div>

        <div className="site-footer__bottom">
          <div className="site-footer__legal">
            <small>{t('footer.copyright', { year })}</small>
            <a
              className="site-footer__github"
              href="https://github.com/dolt-y/TravelMind-AI"
              target="_blank"
              rel="noreferrer"
              aria-label={t('footer.github')}
              title={t('footer.github')}
            >
              <Github size={17} aria-hidden="true" />
            </a>
          </div>
          <small>{t('footer.disclaimer')}</small>
        </div>
      </div>
    </footer>
  )
}
