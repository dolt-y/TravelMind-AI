import { useEffect } from 'react'
import { BookOpen, Compass, Menu, Settings, Sparkles, X } from 'lucide-react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { LanguageSwitcher } from '../components/common/LanguageSwitcher'
import { ServiceStatus } from '../components/common/ServiceStatus'
import { useAppStore } from '../stores/appStore'

const navItems = [
  { to: '/inspiration', key: 'nav.inspiration', icon: Compass },
  { to: '/plan', key: 'nav.plan', icon: Sparkles },
  { to: '/library', key: 'nav.library', icon: BookOpen },
  { to: '/settings', key: 'nav.settings', icon: Settings },
]

export function AppLayout() {
  const { t } = useTranslation()
  const location = useLocation()
  const mobileMenuOpen = useAppStore((state) => state.mobileMenuOpen)
  const setMobileMenuOpen = useAppStore((state) => state.setMobileMenuOpen)
  const refreshHealth = useAppStore((state) => state.refreshHealth)

  useEffect(() => {
    void refreshHealth()
  }, [refreshHealth])

  useEffect(() => {
    setMobileMenuOpen(false)
  }, [location.pathname, setMobileMenuOpen])

  return (
    <div className="app-shell">
      <header className="site-header">
        <div className="site-header__inner">
          <NavLink className="brand" to="/" aria-label={t('nav.home')}>
            <span className="brand__mark"><Compass size={20} /></span>
            <span>TravelMind <strong>AI</strong></span>
          </NavLink>
          <nav className={`main-nav${mobileMenuOpen ? ' is-open' : ''}`} aria-label={t('nav.main')}>
            {navItems.map(({ to, key, icon: Icon }) => (
              <NavLink key={to} to={to} className={({ isActive }) => isActive ? 'is-active' : ''}>
                <Icon size={17} aria-hidden="true" />{t(key)}
              </NavLink>
            ))}
            <div className="main-nav__mobile-tools"><ServiceStatus /><LanguageSwitcher /></div>
          </nav>
          <div className="site-header__tools">
            <ServiceStatus compact />
            <LanguageSwitcher />
            <button className="icon-button menu-button" type="button" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} title={t('nav.menu')}>
              {mobileMenuOpen ? <X size={21} /> : <Menu size={21} />}
            </button>
          </div>
        </div>
      </header>
      <main><Outlet /></main>
      <footer className="site-footer">
        <div><span>TravelMind AI</span><small>{t('footer.copy')}</small></div>
        <a href="/docs" target="_blank" rel="noreferrer">{t('footer.api')}</a>
      </footer>
    </div>
  )
}
