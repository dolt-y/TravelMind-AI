import { useEffect, useMemo, useState } from 'react'
import type { FormEvent, SyntheticEvent } from 'react'
import { useTranslation } from 'react-i18next'
import {
  ArrowRight,
  ArrowLeft,
  BedDouble,
  Bell,
  Bookmark,
  Clock3,
  Compass,
  ExternalLink,
  Heart,
  LoaderCircle,
  MapPin,
  RefreshCw,
  RotateCcw,
  Search,
  Settings,
  Sparkles,
  Star,
  TicketCheck,
  Umbrella,
  Wind,
} from 'lucide-react'
import { extractAttractions, getHealth, getWeather, searchHotels } from './api'
import i18n from './i18n'
import { PrototypeWorkspace } from './prototype'
import type { AppScreen } from './prototype'
import type {
  Attraction,
  AttractionRequest,
  AttractionResponse,
  HealthResponse,
  HotelSearchResponse,
  WeatherResponse,
} from './types'

// 本地图集承担热门目的地和景点卡片的视觉占位，避免页面依赖外部图片 CDN。
const travelImages = {
  amalfiCoast: '/assets/travel/amalfi-coast.jpg',
  amalfiArchitecture: '/assets/travel/amalfi-architecture.jpg',
  kyoto: '/assets/travel/kyoto.jpg',
  icelandAurora: '/assets/travel/iceland-aurora.jpg',
  switzerlandLake: '/assets/travel/switzerland-lake.jpg',
  norwayFjord: '/assets/travel/norway-fjord.jpg',
  hotAirBalloon: '/assets/travel/hot-air-balloon.jpg',
} as const

const cityPresets = [
  { name: '北京', nameKey: 'cities.beijing', keyword: '历史文化', keywordKey: 'cities.history', image: travelImages.amalfiArchitecture },
  { name: '杭州', nameKey: 'cities.hangzhou', keyword: '自然人文', keywordKey: 'cities.nature', image: travelImages.switzerlandLake },
  { name: '成都', nameKey: 'cities.chengdu', keyword: '美食漫游', keywordKey: 'cities.food', image: travelImages.kyoto },
  { name: '冰岛', nameKey: 'cities.iceland', keyword: '自然风光', keywordKey: 'cities.scenery', image: travelImages.icelandAurora },
]

const fallbackImages = Object.values(travelImages)

function formatDuration(minutes: number) {
  if (minutes < 60) return `${minutes} 分钟`
  const hours = Math.floor(minutes / 60)
  const rest = minutes % 60
  return rest ? `${hours} 小时 ${rest} 分` : `${hours} 小时`
}

function handleImageError(event: SyntheticEvent<HTMLImageElement>, index = 0) {
  const image = event.currentTarget
  if (image.dataset.fallback === 'true') return
  image.dataset.fallback = 'true'
  image.src = fallbackImages[index % fallbackImages.length]
}

function AttractionCard({ attraction, index, onOpen }: { attraction: Attraction; index: number; onOpen?: () => void }) {
  const { t } = useTranslation()
  const [saved, setSaved] = useState(false)
  const photo = attraction.photos[0] || fallbackImages[index % fallbackImages.length]

  return (
    <article className="attraction-card" role={onOpen ? 'button' : undefined} tabIndex={onOpen ? 0 : undefined} onClick={onOpen} onKeyDown={(event) => { if (onOpen && (event.key === 'Enter' || event.key === ' ')) { event.preventDefault(); onOpen() } }}>
      <div className="card-media">
        <img src={photo} alt={attraction.name_zh || attraction.name} onError={(event) => handleImageError(event, index)} />
        <button
          className={`save-button ${saved ? 'is-saved' : ''}`}
          type="button"
          title={saved ? '取消收藏' : '收藏景点'}
          aria-label={saved ? '取消收藏' : '收藏景点'}
          aria-pressed={saved}
          onClick={(event) => { event.stopPropagation(); setSaved((current) => !current) }}
        >
          <Heart size={18} fill={saved ? 'currentColor' : 'none'} />
        </button>
        {attraction.rating !== null && (
          <span className="rating-badge"><Star size={14} fill="currentColor" /> {attraction.rating.toFixed(1)}</span>
        )}
      </div>
      <div className="card-body">
        <div className="card-title-row">
          <div>
            <h3>{attraction.name_zh || attraction.name}</h3>
            {attraction.name_en && <p className="english-name">{attraction.name_en}</p>}
          </div>
          <span className="duration"><Clock3 size={15} /> {formatDuration(attraction.duration)}</span>
        </div>
        <p className="reason">{attraction.reason}</p>
        <div className="card-meta">
          {attraction.address && <span><MapPin size={15} />{attraction.address}</span>}
          {attraction.reservation_required && <span className="reservation"><TicketCheck size={15} />{t('data.reservation')}</span>}
        </div>
        {attraction.reservation_tips && <p className="reservation-tip">{attraction.reservation_tips}</p>}
      </div>
    </article>
  )
}

function formatForecastDate(value: string) {
  const date = new Date(`${value}T00:00:00`)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('zh-CN', { month: 'numeric', day: 'numeric', weekday: 'short' }).format(date)
}

function WeatherPanel({ weather, loading }: { weather: WeatherResponse | null; loading: boolean }) {
  const { t } = useTranslation()
  const forecasts = weather?.data.slice(0, 3) ?? []

  return (
    <section className="insight-panel weather-panel" aria-labelledby="weather-heading">
      <div className="insight-heading">
        <div className="insight-icon weather-icon"><Umbrella size={18} /></div>
        <div>
          <p className="eyebrow">{t('data.source')}</p>
          <h3 id="weather-heading">{t('data.weather')}</h3>
        </div>
        {weather?.cached && <span className="cache-label">{t('data.cached')}</span>}
      </div>
      {loading ? (
        <div className="panel-loading"><LoaderCircle size={18} className="spinning" />{t('data.loadingWeather')}</div>
      ) : forecasts.length > 0 ? (
        <div className="forecast-list">
          {forecasts.map((forecast) => (
            <div className="forecast-row" key={`${forecast.city}-${forecast.date}`}>
              <span className="forecast-date">{formatForecastDate(forecast.date)}</span>
              <strong>{forecast.day_temperature === null ? '--' : `${Math.round(forecast.day_temperature)}°`}</strong>
              <span>{forecast.day_weather || '天气待定'}</span>
              <span className="forecast-wind"><Wind size={13} />{forecast.day_wind_power || '风力待定'}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="panel-empty">{t('data.emptyWeather')}</div>
      )}
    </section>
  )
}

function HotelPanel({ hotels, loading }: { hotels: HotelSearchResponse | null; loading: boolean }) {
  const { t } = useTranslation()
  const items = hotels?.data.slice(0, 3) ?? []

  return (
    <section className="insight-panel hotel-panel" aria-labelledby="hotel-heading">
      <div className="insight-heading">
        <div className="insight-icon hotel-icon"><BedDouble size={18} /></div>
        <div>
          <p className="eyebrow">{t('data.source')}</p>
          <h3 id="hotel-heading">{t('data.hotel')}</h3>
        </div>
        {hotels?.cached && <span className="cache-label">{t('data.cached')}</span>}
      </div>
      {loading ? (
        <div className="panel-loading"><LoaderCircle size={18} className="spinning" />{t('data.loadingHotel')}</div>
      ) : items.length > 0 ? (
        <div className="hotel-list">
          {items.map((hotel) => (
            <div className="hotel-row" key={`${hotel.provider}-${hotel.id}`}>
              <div className="hotel-thumb">
                <img src={hotel.photos[0] || travelImages.amalfiCoast} alt="" onError={(event) => handleImageError(event, 0)} />
              </div>
              <div className="hotel-copy">
                <strong>{hotel.name}</strong>
                <span>{hotel.address || t('data.addressPending')}</span>
              </div>
              <div className="hotel-price">
                {hotel.average_price === null ? '--' : `¥${Math.round(hotel.average_price)}`}
                <small>{t('data.perNight')}</small>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="panel-empty">{t('data.emptyHotel')}</div>
      )}
    </section>
  )
}

function TripBuilder({
  form,
  updateForm,
  onSubmit,
  onBack,
  loading,
}: {
  form: AttractionRequest
  updateForm: (patch: Partial<AttractionRequest>) => void
  onSubmit: (event: FormEvent) => void
  onBack: () => void
  loading: boolean
}) {
  const { t } = useTranslation()

  return (
    <section className="builder-layout" aria-labelledby="builder-title">
      <div className="builder-main">
        <button className="back-link" type="button" onClick={onBack}><ArrowLeft size={15} />{t('create.back')}</button>
        <p className="eyebrow">{t('create.eyebrow')}</p>
        <h1 id="builder-title">{t('create.title')}</h1>
        <p className="builder-copy">{t('create.copy')}</p>
        <div className="trip-stepper" aria-label={t('create.title')}>
          {[0, 1, 2].map((step) => (
            <div className={`trip-step ${step === 0 ? 'is-active' : ''}`} key={step}>
              <span>{step + 1}</span><strong>{t(`create.steps.${step}`)}</strong>
            </div>
          ))}
        </div>
        <form className="builder-form" onSubmit={onSubmit}>
          <label className="builder-field">
            <span>{t('create.destination')}</span>
            <div className="builder-input"><MapPin size={17} /><input value={form.city} onChange={(event) => updateForm({ city: event.target.value })} placeholder={t('create.destinationPlaceholder')} autoComplete="off" /></div>
          </label>
          <label className="builder-field">
            <span>{t('create.preference')}</span>
            <div className="builder-input"><Search size={17} /><input value={form.keywords} onChange={(event) => updateForm({ keywords: event.target.value })} placeholder={t('create.preferencePlaceholder')} autoComplete="off" /></div>
          </label>
          <div className="builder-row">
            <label className="builder-field">
              <span>{t('create.source')}</span>
              <div className="builder-range"><input type="range" min="1" max="10" value={form.note_limit} onChange={(event) => updateForm({ note_limit: Number(event.target.value) })} /><strong>{form.note_limit}</strong></div>
            </label>
            <label className="builder-field">
              <span>{t('create.language')}</span>
              <select value={form.language} onChange={(event) => { const language = event.target.value as AttractionRequest['language']; updateForm({ language }); void i18n.changeLanguage(language) }}>
                <option value="zh">{t('language.zh')}</option><option value="en">{t('language.en')}</option><option value="ja">{t('language.ja')}</option>
              </select>
            </label>
          </div>
          <button className="builder-submit" type="submit" disabled={loading}><Sparkles size={17} />{loading ? t('hero.submitting') : t('create.submit')}<ArrowRight size={16} /></button>
        </form>
      </div>
      <aside className="pipeline-panel">
        <p className="eyebrow">{t('create.eyebrow')}</p>
        <h2>{t('create.pipelineTitle')}</h2>
        <p>{t('create.pipelineCopy')}</p>
        <ol className="pipeline-list">
          {[['sourceStep', Bookmark], ['llmStep', Sparkles], ['mapStep', MapPin], ['saveStep', ExternalLink]].map(([key, Icon]) => {
            const PipelineIcon = Icon as typeof Bookmark
            return <li key={String(key)}><span className="pipeline-icon"><PipelineIcon size={16} /></span><span>{t(`create.${String(key)}`)}</span><ArrowRight size={14} /></li>
          })}
        </ol>
      </aside>
    </section>
  )
}

function LibraryPanel({ result, onStart, onOpen }: { result: AttractionResponse | null; onStart: () => void; onOpen: () => void }) {
  const { t } = useTranslation()
  return (
    <section className="library-page" id="library" aria-labelledby="library-title">
      <p className="eyebrow">{t('library.eyebrow')}</p>
      <h1 id="library-title">{t('library.title')}</h1>
      {result ? (
        <div className="library-record">
          <div><span className="record-label">{t('library.latest')}</span><strong>{result.city}</strong><span>{t('result.notes', { count: result.notes_count })} · {t('result.places', { count: result.attractions.length })}</span></div>
          <button className="secondary-button" type="button" onClick={onOpen}>{t('library.open')}<ArrowRight size={15} /></button>
        </div>
      ) : (
        <div className="library-empty"><Bookmark size={28} /><h2>{t('library.empty')}</h2><p>{t('library.emptyCopy')}</p><button className="builder-submit compact" type="button" onClick={onStart}>{t('library.start')}<ArrowRight size={15} /></button></div>
      )}
    </section>
  )
}

// 后端不可用时提供本地演示结果，保证前端流程仍可继续体验。
function createPrototypeResult(city: string, keywords: string): AttractionResponse {
  const names = ['城市历史中心', '当地代表性景点', '热门自然景观']
  return {
    extraction_id: `prototype-${Date.now()}`,
    city,
    keywords,
    notes_count: 4,
    attractions: names.map((name, index) => ({
      name,
      name_zh: name,
      name_en: `Local place ${index + 1}`,
      reason: '本地原型数据：用于演示景点详情、收藏和行程编辑等交互。',
      duration: 120 + index * 30,
      reservation_required: index === 1,
      reservation_tips: index === 1 ? '建议提前预约' : '',
      poi_id: `prototype-poi-${index}`,
      address: '目的地热门区域',
      location: null,
      rating: 4.6 + index * 0.1,
      photos: [travelImages[(['amalfiCoast', 'amalfiArchitecture', 'kyoto'] as const)[index]]],
    })),
  }
}

function App() {
  const { t } = useTranslation()
  const [view, setView] = useState<AppScreen>('home')
  const [form, setForm] = useState<AttractionRequest>({
    city: '',
    keywords: '',
    language: 'zh',
    note_limit: 4,
  })
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [healthLoading, setHealthLoading] = useState(true)
  const [result, setResult] = useState<AttractionResponse | null>(null)
  const [weather, setWeather] = useState<WeatherResponse | null>(null)
  const [hotels, setHotels] = useState<HotelSearchResponse | null>(null)
  const [enrichmentLoading, setEnrichmentLoading] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const refreshHealth = async () => {
    setHealthLoading(true)
    try {
      setHealth(await getHealth())
    } catch {
      setHealth(null)
    } finally {
      setHealthLoading(false)
    }
  }

  useEffect(() => {
    void refreshHealth()
  }, [])

  const status = useMemo(() => {
    if (healthLoading) return { key: 'checking', tone: 'pending' }
    if (!health) return { key: 'offline', tone: 'offline' }
    if (!health.configured) return { key: 'waiting', tone: 'warning' }
    return { key: 'online', tone: 'online' }
  }, [health, healthLoading])

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (!form.city.trim()) {
      setError(t('error.missingCity'))
      return
    }
    setView('generating')
    setLoading(true)
    setError('')
    setWeather(null)
    setHotels(null)
    try {
      const extraction = await extractAttractions({ ...form, city: form.city.trim(), keywords: form.keywords.trim() })
      setResult(extraction)
      setView('result')
      setLoading(false)
      setEnrichmentLoading(true)
      const [weatherResult, hotelResult] = await Promise.allSettled([
        getWeather(extraction.city),
        searchHotels(extraction.city),
      ])
      if (weatherResult.status === 'fulfilled') setWeather(weatherResult.value)
      if (hotelResult.status === 'fulfilled') setHotels(hotelResult.value)
      if (weatherResult.status === 'rejected' && hotelResult.status === 'rejected') {
        setError(t('error.enrichFailed'))
      }
    } catch {
      setResult(createPrototypeResult(form.city.trim(), form.keywords.trim()))
      setError('接口暂不可用，已切换到本地原型数据')
      setView('result')
    } finally {
      setLoading(false)
      setEnrichmentLoading(false)
    }
  }

  const choosePreset = (name: string, keyword: string) => {
    setForm((current) => ({ ...current, city: name, keywords: keyword }))
    setError('')
  }

  const resetSearch = () => {
    setResult(null)
    setWeather(null)
    setHotels(null)
    setError('')
    setView('home')
  }

  return (
    <div className="site-shell" id="top">
      <header className="site-header">
        <a className="site-brand" href="#top" aria-label={t('nav.homeAria')}>
          <span className="site-brand-mark"><Compass size={18} /></span>
          <span>TravelMind <b>AI</b></span>
        </a>
        <nav className="site-nav" aria-label={t('nav.mainAria')}>
          <a className={`site-nav-link ${view === 'home' || view === 'inspiration' ? 'active' : ''}`} href="#discover" onClick={() => setView('home')}>{t('nav.explore')}</a>
          <a className={`site-nav-link ${view === 'library' ? 'active' : ''}`} href="#library" onClick={() => setView('library')}>{t('nav.library')}</a>
          <a className="site-nav-link" href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer">{t('nav.api')}</a>
        </nav>
        <div className="header-actions">
          <span className={`service-status ${status.tone}`}><span className="status-dot" />{t(`status.${status.key}`)}</span>
          <button className="header-cta" type="button" onClick={() => { setView('create'); window.scrollTo({ top: 0, behavior: 'smooth' }) }}>{t('nav.start')}</button>
          <button className="icon-button" type="button" onClick={() => setView('search')} title="搜索" aria-label="搜索"><Search size={16} /></button>
          <button className="icon-button" type="button" onClick={() => setView('favorites')} title="收藏" aria-label="收藏"><Heart size={16} /></button>
          <button className="icon-button" type="button" onClick={() => setView('notifications')} title="通知" aria-label="通知"><Bell size={16} /></button>
          <button className="icon-button" type="button" onClick={() => setView('settings')} title="设置" aria-label="设置"><Settings size={16} /></button>
          <button className="icon-button header-refresh" type="button" onClick={() => void refreshHealth()} title={t('status.refresh')} aria-label={t('status.refresh')}>
            <RefreshCw size={16} className={healthLoading ? 'spinning' : ''} />
          </button>
        </div>
      </header>

      <main>
        {view === 'home' && <>
        <section className="hero-section" aria-labelledby="hero-title">
          <img className="hero-image" src={travelImages.amalfiCoast} alt="海岸旅行风景" />
          <div className="hero-overlay" />
          <div className="hero-content">
            <p className="hero-kicker">{t('hero.kicker')}</p>
            <h1 id="hero-title">{t('hero.title')}</h1>
            <p className="hero-copy">{t('hero.copy')}</p>
            <form className="hero-search" id="discover" onSubmit={(event) => void submit(event)}>
              <div className="hero-field">
                <MapPin size={17} />
                <label className="sr-only" htmlFor="city">{t('hero.cityLabel')}</label>
                <input
                  id="city"
                  value={form.city}
                  onChange={(event) => setForm((current) => ({ ...current, city: event.target.value }))}
                  placeholder={t('hero.cityPlaceholder')}
                  autoComplete="off"
                />
              </div>
              <div className="hero-field hero-keyword-field">
                <Search size={17} />
                <label className="sr-only" htmlFor="keywords">{t('hero.preferenceLabel')}</label>
                <input
                  id="keywords"
                  value={form.keywords}
                  onChange={(event) => setForm((current) => ({ ...current, keywords: event.target.value }))}
                  placeholder={t('hero.preferencePlaceholder')}
                  autoComplete="off"
                />
              </div>
              <button className="hero-submit" type="submit" disabled={loading}>
                {loading ? <LoaderCircle size={18} className="spinning" /> : <Sparkles size={18} />}
                {loading ? t('hero.submitting') : t('hero.submit')}
              </button>
            </form>
            <div className="hero-meta">
              <span>{t('hero.notes', { count: form.note_limit })}</span>
              <input
                aria-label={t('hero.noteAria')}
                type="range"
                min="1"
                max="10"
                value={form.note_limit}
                onChange={(event) => setForm((current) => ({ ...current, note_limit: Number(event.target.value) }))}
              />
              <select
                aria-label={t('hero.languageAria')}
                value={form.language}
                onChange={(event) => {
                  const language = event.target.value as AttractionRequest['language']
                  setForm((current) => ({ ...current, language }))
                  void i18n.changeLanguage(language)
                }}
              >
                <option value="zh">{t('language.zh')}</option>
                <option value="en">{t('language.en')}</option>
                <option value="ja">{t('language.ja')}</option>
              </select>
            </div>
          </div>
        </section>

        <section className="feature-strip" aria-label={t('features.aria')}>
          <button className="feature-item" type="button" onClick={() => setView('create')}><span className="feature-icon"><Sparkles size={17} /></span><span><strong>{t('features.plan')}</strong><small>{t('features.planSub')}</small></span></button>
          <button className="feature-item" type="button" onClick={() => setView('settings')}><span className="feature-icon"><Bookmark size={17} /></span><span><strong>{t('features.custom')}</strong><small>{t('features.customSub')}</small></span></button>
          <button className="feature-item" type="button" onClick={() => setView('map')}><span className="feature-icon"><MapPin size={17} /></span><span><strong>{t('features.trusted')}</strong><small>{t('features.trustedSub')}</small></span></button>
          <button className="feature-item" type="button" onClick={() => setView('mobile')}><span className="feature-icon"><ExternalLink size={17} /></span><span><strong>{t('features.start')}</strong><small>{t('features.startSub')}</small></span></button>
        </section>
        </>}

        {view === 'create' && <TripBuilder form={form} updateForm={(patch) => setForm((current) => ({ ...current, ...patch }))} onSubmit={(event) => void submit(event)} onBack={() => setView('home')} loading={loading} />}

        {error && <div className="error-banner" role="alert"><span>{error}</span><button type="button" onClick={() => setError('')}>{t('error.close')}</button></div>}

        {loading && view !== 'generating' && (
          <section className="loading-state" aria-live="polite">
            <div className="loading-visual"><Compass size={34} /></div>
            <div><h2>{t('loading.title', { city: form.city })}</h2><p>{t('loading.copy')}</p></div>
          </section>
        )}

        {view === 'home' && !loading && !result && (
          <section className="preset-section" aria-labelledby="popular-heading">
            <div className="section-heading">
              <div><p className="eyebrow">{t('popular.eyebrow')}</p><h2 id="popular-heading">{t('popular.title')}</h2></div>
              <p>{t('popular.copy')}</p>
            </div>
            <div className="preset-grid">
              {cityPresets.map((city) => (
                <button className="preset-card" type="button" key={city.name} onClick={() => choosePreset(city.name, city.keyword)}>
                  <img src={city.image} alt={city.name} onError={handleImageError} />
                  <span className="preset-overlay">
                    <span><strong>{t(city.nameKey)}</strong><small>{t(city.keywordKey)}</small></span>
                    <span className="preset-arrow"><ArrowRight size={18} /></span>
                  </span>
                </button>
              ))}
            </div>
          </section>
        )}

        {view === 'result' && !loading && result && (
          <section className="results-section" id="results">
            <div className="results-heading">
              <div>
                <p className="eyebrow">{result.city} · {t('result.notes', { count: result.notes_count })}</p>
                <h2>{t('result.places', { count: result.attractions.length })}</h2>
              </div>
              <div className="result-actions">
                <div className="result-id" title={result.extraction_id}><span>{t('result.saved')}</span><code>{result.extraction_id.slice(0, 8)}</code></div>
                <button className="secondary-button" type="button" onClick={() => setView('overview')}>行程总览</button>
                <button className="secondary-button" type="button" onClick={() => setView('map')}>地图路线</button>
                <button className="secondary-button" type="button" onClick={() => setView('edit')}>编辑</button>
                <button className="secondary-button" type="button" onClick={() => setView('share')}>分享</button>
                <button className="secondary-button" type="button" onClick={() => setView('export')}>导出</button>
                <button className="secondary-button" type="button" onClick={resetSearch}><RotateCcw size={15} />{t('result.retry')}</button>
              </div>
            </div>

            <div className="insight-grid">
              <WeatherPanel weather={weather} loading={enrichmentLoading} />
              <HotelPanel hotels={hotels} loading={enrichmentLoading} />
            </div>

            {result.attractions.length > 0 ? (
              <div className="attraction-grid">
                {result.attractions.map((attraction, index) => (
                  <AttractionCard key={`${attraction.poi_id || attraction.name}-${index}`} attraction={attraction} index={index} onOpen={() => setView('detail')} />
                ))}
              </div>
            ) : (
              <div className="empty-results"><Search size={28} /><h3>{t('result.noPlaces')}</h3><p>{t('result.noPlacesCopy')}</p></div>
            )}
          </section>
        )}

        {view === 'library' && !loading && <LibraryPanel result={result} onStart={() => setView('create')} onOpen={() => setView('result')} />}

        {view !== 'home' && view !== 'create' && view !== 'result' && view !== 'library' && (
          <PrototypeWorkspace screen={view} result={result} onNavigate={setView} />
        )}

        <footer>
          <span>TravelMind AI</span>
          <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer">{t('footer.api')} <ExternalLink size={14} /></a>
        </footer>
      </main>
    </div>
  )
}

export default App
