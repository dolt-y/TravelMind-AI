import { useEffect } from 'react'
import { BookOpen, Compass, House, Map, Menu, Mountain, Settings, X } from 'lucide-react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { LanguageSwitcher } from '../components/common/LanguageSwitcher'
import { useAppStore } from '../stores/appStore'

const navItems = [
  { to: '/', key: 'nav.homeLink', icon: House },
  { to: '/inspiration', key: 'nav.inspiration', icon: Compass },
  { to: '/plan', key: 'nav.plan', icon: Map },
  { to: '/library', key: 'nav.library', icon: BookOpen },
  { to: '/settings', key: 'nav.settings', icon: Settings },
]

export function AppLayout() {
  const { t } = useTranslation()
  const location = useLocation()
  const isHome = location.pathname === '/'
  const mobileMenuOpen = useAppStore((state) => state.mobileMenuOpen)
  const setMobileMenuOpen = useAppStore((state) => state.setMobileMenuOpen)

  useEffect(() => {
    setMobileMenuOpen(false)
  }, [location.pathname, setMobileMenuOpen])

  return (
    <div className="app-shell">
      <header className={`site-header${isHome ? ' site-header--home' : ''}`}>
        <div className="site-header__inner">
          <NavLink className="brand" to="/" aria-label={t('nav.home')}>
            <span className="brand__mark"><Mountain size={20} /></span>
            <span>TravelMind</span>
          </NavLink>
          <nav className={`main-nav${mobileMenuOpen ? ' is-open' : ''}`} aria-label={t('nav.main')}>
            {navItems.map(({ to, key, icon: Icon }) => (
              <NavLink key={to} to={to} className={({ isActive }) => isActive ? 'is-active' : ''}>
                <Icon size={17} aria-hidden="true" />{t(key)}
              </NavLink>
            ))}
            <div className="main-nav__mobile-tools"><LanguageSwitcher /></div>
          </nav>
          <div className="site-header__tools">
            <LanguageSwitcher />
            <button className="icon-button menu-button" type="button" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} title={t('nav.menu')}>
              {mobileMenuOpen ? <X size={21} /> : <Menu size={21} />}
            </button>
          </div>
        </div>
      </header>
      <main><Outlet /></main>
      <footer className="site-footer">
        <div><span>TravelMind</span><small>{t('footer.copy')}</small></div>
      </footer>
    </div>
  )
}
