import { useEffect, useMemo, useState } from 'react'
import type { FormEvent, SyntheticEvent } from 'react'
import {
  ArrowRight,
  Bookmark,
  Clock3,
  Compass,
  ExternalLink,
  Heart,
  LoaderCircle,
  MapPin,
  RefreshCw,
  Search,
  SlidersHorizontal,
  Sparkles,
  Star,
  TicketCheck,
} from 'lucide-react'
import { extractAttractions, getHealth } from './api'
import type { Attraction, AttractionRequest, AttractionResponse, HealthResponse } from './types'

const cityPresets = [
  { name: '北京', keyword: '历史文化', image: 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?auto=format&fit=crop&w=900&q=85' },
  { name: '杭州', keyword: '自然人文', image: 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?auto=format&fit=crop&w=900&q=85' },
  { name: '成都', keyword: '美食漫游', image: 'https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=900&q=85' },
]

const fallbackImages = cityPresets.map((city) => city.image)

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

function AttractionCard({ attraction, index }: { attraction: Attraction; index: number }) {
  const [saved, setSaved] = useState(false)
  const photo = attraction.photos[0] || fallbackImages[index % fallbackImages.length]

  return (
    <article className="attraction-card">
      <div className="card-media">
        <img src={photo} alt={attraction.name_zh || attraction.name} onError={(event) => handleImageError(event, index)} />
        <button
          className={`save-button ${saved ? 'is-saved' : ''}`}
          type="button"
          title={saved ? '取消收藏' : '收藏景点'}
          aria-label={saved ? '取消收藏' : '收藏景点'}
          aria-pressed={saved}
          onClick={() => setSaved((current) => !current)}
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
          {attraction.reservation_required && <span className="reservation"><TicketCheck size={15} />建议预约</span>}
        </div>
        {attraction.reservation_tips && <p className="reservation-tip">{attraction.reservation_tips}</p>}
      </div>
    </article>
  )
}

function App() {
  const [form, setForm] = useState<AttractionRequest>({
    city: '',
    keywords: '',
    language: 'zh',
    note_limit: 4,
  })
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [healthLoading, setHealthLoading] = useState(true)
  const [result, setResult] = useState<AttractionResponse | null>(null)
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
    if (healthLoading) return { label: '检查中', tone: 'pending' }
    if (!health) return { label: '服务未连接', tone: 'offline' }
    if (!health.configured) return { label: '等待配置', tone: 'warning' }
    return { label: '服务可用', tone: 'online' }
  }, [health, healthLoading])

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (!form.city.trim()) {
      setError('请先填写目的地城市')
      return
    }
    setLoading(true)
    setError('')
    try {
      setResult(await extractAttractions({ ...form, city: form.city.trim(), keywords: form.keywords.trim() }))
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : '景点提取失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  const choosePreset = (name: string, keyword: string) => {
    setForm((current) => ({ ...current, city: name, keywords: keyword }))
    setError('')
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#top" aria-label="TravelMind AI 首页">
          <span className="brand-mark"><Compass size={22} /></span>
          <span>TravelMind <b>AI</b></span>
        </a>

        <nav aria-label="主导航">
          <a className="nav-item active" href="#discover"><Sparkles size={18} />灵感探索</a>
          <a className="nav-item" href="#results"><Bookmark size={18} />本次结果</a>
        </nav>

        <div className="sidebar-status">
          <div className="status-heading">
            <span className={`status-dot ${status.tone}`} />
            <span>{status.label}</span>
            <button type="button" onClick={() => void refreshHealth()} title="刷新服务状态" aria-label="刷新服务状态">
              <RefreshCw size={15} className={healthLoading ? 'spinning' : ''} />
            </button>
          </div>
          <p>{health?.mode === 'pc-read-only' ? '小红书只读模式' : 'FastAPI · localhost:8000'}</p>
        </div>
      </aside>

      <main id="top">
        <header className="topbar">
          <div>
            <p className="eyebrow">旅行灵感工作台</p>
            <h1>下一站，去哪里？</h1>
          </div>
          <div className={`connection-pill ${status.tone}`}>
            <span className="status-dot" />{status.label}
          </div>
        </header>

        <section className="search-panel" id="discover">
          <form onSubmit={(event) => void submit(event)}>
            <div className="field destination-field">
              <label htmlFor="city"><MapPin size={16} />目的地</label>
              <input
                id="city"
                value={form.city}
                onChange={(event) => setForm((current) => ({ ...current, city: event.target.value }))}
                placeholder="城市，例如：北京"
                autoComplete="off"
              />
            </div>
            <div className="field keyword-field">
              <label htmlFor="keywords"><Search size={16} />旅行偏好</label>
              <input
                id="keywords"
                value={form.keywords}
                onChange={(event) => setForm((current) => ({ ...current, keywords: event.target.value }))}
                placeholder="历史文化、美食、亲子…"
                autoComplete="off"
              />
            </div>
            <div className="field language-field">
              <label htmlFor="language"><SlidersHorizontal size={16} />结果语言</label>
              <select
                id="language"
                value={form.language}
                onChange={(event) => setForm((current) => ({ ...current, language: event.target.value as AttractionRequest['language'] }))}
              >
                <option value="zh">中文</option>
                <option value="en">English</option>
                <option value="ja">日本語</option>
              </select>
            </div>
            <button className="submit-button" type="submit" disabled={loading}>
              {loading ? <LoaderCircle size={19} className="spinning" /> : <Sparkles size={19} />}
              {loading ? '正在整理' : '生成灵感'}
            </button>
          </form>

          <div className="search-options">
            <label htmlFor="note-limit">参考游记 <strong>{form.note_limit} 篇</strong></label>
            <input
              id="note-limit"
              type="range"
              min="1"
              max="10"
              value={form.note_limit}
              onChange={(event) => setForm((current) => ({ ...current, note_limit: Number(event.target.value) }))}
            />
            <span>内容越多，处理时间越长</span>
          </div>
        </section>

        {error && <div className="error-banner" role="alert"><span>{error}</span><button type="button" onClick={() => setError('')}>关闭</button></div>}

        {loading && (
          <section className="loading-state" aria-live="polite">
            <div className="loading-visual"><Compass size={34} /></div>
            <div><h2>正在探索 {form.city}</h2><p>检索游记、整理推荐理由并匹配地点信息…</p></div>
          </section>
        )}

        {!loading && !result && (
          <section className="preset-section">
            <div className="section-heading">
              <div><p className="eyebrow">快速开始</p><h2>热门目的地</h2></div>
              <p>选择一个城市，自动填入旅行主题</p>
            </div>
            <div className="preset-grid">
              {cityPresets.map((city) => (
                <button className="preset-card" type="button" key={city.name} onClick={() => choosePreset(city.name, city.keyword)}>
                  <img src={city.image} alt={city.name} onError={handleImageError} />
                  <span className="preset-overlay">
                    <span><strong>{city.name}</strong><small>{city.keyword}</small></span>
                    <span className="preset-arrow"><ArrowRight size={18} /></span>
                  </span>
                </button>
              ))}
            </div>
          </section>
        )}

        {!loading && result && (
          <section className="results-section" id="results">
            <div className="results-heading">
              <div>
                <p className="eyebrow">{result.city} · {result.notes_count} 篇游记</p>
                <h2>{result.attractions.length} 个值得留意的地方</h2>
              </div>
              <div className="result-id" title={result.extraction_id}>
                <span>记录已保存</span>
                <code>{result.extraction_id.slice(0, 8)}</code>
              </div>
            </div>

            {result.attractions.length > 0 ? (
              <div className="attraction-grid">
                {result.attractions.map((attraction, index) => (
                  <AttractionCard key={`${attraction.poi_id || attraction.name}-${index}`} attraction={attraction} index={index} />
                ))}
              </div>
            ) : (
              <div className="empty-results"><Search size={28} /><h3>没有找到合适的景点</h3><p>换一个旅行偏好后重新试试。</p></div>
            )}
          </section>
        )}

        <footer>
          <span>TravelMind AI</span>
          <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer">API 文档 <ExternalLink size={14} /></a>
        </footer>
      </main>
    </div>
  )
}

export default App
