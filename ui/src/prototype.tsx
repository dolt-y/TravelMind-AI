import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import {
  ArrowLeft, ArrowRight, Bell, Check, CheckCircle2, ChevronRight, CircleHelp, CloudDownload, LogIn,
  Copy, Download, FileImage, FileSpreadsheet, FileText, Heart, Map, MapPin, MoreHorizontal,
  Pencil, Plus, RefreshCw, Route, Search, Settings, Share2, Smartphone, Star, Trash2, UserRound,
} from 'lucide-react'
import {
  getXhsLoginStatus,
  loginWithXhsCookie,
  startXhsPhoneLogin,
  startXhsQrLogin,
  verifyXhsPhoneLogin,
} from './api'
import type { Attraction, AttractionResponse, XHSLoginMethod, XHSLoginStatusResponse } from './types'

// 原型页面共享的导航状态和本地交互，不依赖后端行程接口。
export type AppScreen =
  | 'home' | 'create' | 'library' | 'generating' | 'result' | 'overview' | 'detail' | 'edit' | 'map'
  | 'inspiration' | 'favorites' | 'share' | 'export' | 'search' | 'notifications' | 'settings' | 'mobile' | 'xhs-login'

type PrototypeProps = {
  screen: Exclude<AppScreen, 'home' | 'create' | 'result'>
  result: AttractionResponse | null
  onNavigate: (screen: AppScreen) => void
}

const demoStops = [
  { name: '波西塔诺小镇', city: 'Positano', image: '/assets/travel/amalfi-architecture.jpg', rating: 4.8 },
  { name: '阿马尔菲主教堂', city: 'Amalfi Cathedral', image: '/assets/travel/amalfi-coast.jpg', rating: 4.7 },
  { name: '卡普里岛', city: 'Capri Island', image: '/assets/travel/switzerland-lake.jpg', rating: 4.8 },
  { name: '冰岛极光之旅', city: 'Iceland', image: '/assets/travel/iceland-aurora.jpg', rating: 4.9 },
  { name: '日本樱花之旅', city: 'Kyoto', image: '/assets/travel/kyoto.jpg', rating: 4.8 },
  { name: '挪威峡湾', city: 'Geirangerfjord', image: '/assets/travel/norway-fjord.jpg', rating: 4.7 },
]

const fallbackAttractions: Attraction[] = demoStops.slice(0, 3).map((stop, index) => ({
  name: stop.name, name_zh: stop.name, name_en: stop.city, reason: '根据旅行灵感整理的重点地点，适合放入行程进行比较。', duration: 120 + index * 30,
  reservation_required: index === 1, reservation_tips: index === 1 ? '建议提前预约' : '', poi_id: `demo-${index}`, address: '当地热门区域',
  location: null, rating: stop.rating, photos: [stop.image],
}))

function PageFrame({ title, eyebrow, onBack, children, actions }: { title: string; eyebrow?: string; onBack?: () => void; children: React.ReactNode; actions?: React.ReactNode }) {
  return <section className="prototype-page">
    <div className="prototype-heading">
      <div>{onBack && <button className="back-link" type="button" onClick={onBack}><ArrowLeft size={15} />返回</button>}{eyebrow && <p className="eyebrow">{eyebrow}</p>}<h1>{title}</h1></div>
      {actions && <div className="prototype-actions">{actions}</div>}
    </div>
    {children}
  </section>
}

function GeneratingPage({ onNavigate }: { onNavigate: (screen: AppScreen) => void }) {
  const [progress, setProgress] = useState(65)
  useEffect(() => { const timer = window.setInterval(() => setProgress((value) => value >= 92 ? 65 : value + 1), 160); return () => window.clearInterval(timer) }, [])
  return <PageFrame title="AI 正在为你生成行程" eyebrow="AI 生成中">
    <div className="generating-panel"><div className="progress-ring" style={{ '--progress': `${progress * 3.6}deg` } as React.CSSProperties}><strong>{progress}%</strong></div><p>正在分析你的目的地、偏好和真实旅行资料…</p><div className="generation-steps"><span className="done"><CheckCircle2 size={15} />分析目的地信息</span><span className="done"><CheckCircle2 size={15} />提取景点候选</span><span><CheckCircle2 size={15} />匹配地图与天气</span><span><CircleHelp size={15} />整理每日路线</span></div><button className="secondary-button" type="button" onClick={() => onNavigate('result')}>查看当前结果 <ArrowRight size={15} /></button></div>
  </PageFrame>
}

function OverviewPage({ onNavigate }: { onNavigate: (screen: AppScreen) => void }) {
  const [tab, setTab] = useState<'schedule' | 'map' | 'budget' | 'booking'>('schedule')
  return <PageFrame title="意大利阿马尔菲海岸之旅" eyebrow="行程总览" actions={<><button className="secondary-button" type="button" onClick={() => onNavigate('share')}><Share2 size={14} />分享</button><button className="secondary-button" type="button" onClick={() => onNavigate('export')}><Download size={14} />导出</button><button className="icon-button" type="button" title="更多操作"><MoreHorizontal size={17} /></button></>}>
    <div className="trip-meta">2024.08.15 - 2024.06.22 · 8天7晚 <button className="text-button" type="button" onClick={() => onNavigate('edit')}><Pencil size={13} />编辑</button></div>
    <div className="overview-hero"><img src={demoStops[0].image} alt="阿马尔菲海岸" /><div className="overview-stats"><span><strong>8</strong>天数</span><span><strong>24</strong>景点</span><span><strong>¥18,560</strong>人均预算</span><span><strong>4.8</strong>评分</span></div></div>
    <div className="overview-tabs">{[['schedule', '每日行程'], ['map', '地图'], ['budget', '预算'], ['booking', '预订']].map(([key, label]) => <button className={tab === key ? 'is-active' : ''} type="button" key={key} onClick={() => setTab(key as typeof tab)}>{label}</button>)}</div>
    {tab === 'schedule' && <div className="schedule-layout"><div className="day-list">{['抵达那不勒斯，机场周转', '探索波西塔诺海岸', '海边小镇与古迹', '阿马尔菲 · 历史中心', '卡普里岛一日游', '奥特拉托 · 返程'].map((day, index) => <button type="button" key={day} onClick={() => onNavigate('detail')}><span>Day {index + 1}</span>{day}<ChevronRight size={14} /></button>)}</div><div className="route-map"><Map size={30} /><strong>阿马尔菲海岸路线</strong><span>已规划 6 个停靠点</span><button className="primary-button" type="button" onClick={() => onNavigate('map')}>查看地图路线</button></div></div>}
    {tab === 'map' && <div className="tab-placeholder"><Map size={30} /><h2>地图路线</h2><p>查看每日景点顺序与交通连接。</p><button className="primary-button" type="button" onClick={() => onNavigate('map')}>打开路线</button></div>}
    {tab === 'budget' && <div className="budget-grid"><div><span>住宿</span><strong>¥8,400</strong></div><div><span>交通</span><strong>¥3,860</strong></div><div><span>门票与活动</span><strong>¥4,300</strong></div><div><span>餐饮</span><strong>¥2,000</strong></div></div>}
    {tab === 'booking' && <div className="booking-list"><div><span>住宿</span><strong>3 间候选酒店</strong><button className="text-button" type="button" onClick={() => onNavigate('search')}>查看</button></div><div><span>景点预约</span><strong>2 个需要提前预约</strong><button className="text-button" type="button" onClick={() => onNavigate('detail')}>查看</button></div></div>}
  </PageFrame>
}

function DetailPage({ onNavigate, result }: { onNavigate: (screen: AppScreen) => void; result: AttractionResponse | null }) {
  const attraction = result?.attractions[0] || fallbackAttractions[0]; const [saved, setSaved] = useState(false); const [added, setAdded] = useState(false)
  return <PageFrame title={attraction.name_zh || attraction.name} eyebrow="景点详情" onBack={() => onNavigate('result')} actions={<button className={`icon-button ${saved ? 'is-saved' : ''}`} type="button" onClick={() => setSaved(!saved)} title="收藏地点"><Heart size={18} fill={saved ? 'currentColor' : 'none'} /></button>}>
    <div className="detail-layout"><div><img className="detail-image" src={attraction.photos[0] || demoStops[0].image} alt={attraction.name_zh || attraction.name} /><div className="detail-tags"><span>海岸风光</span><span>自然景观</span><span>值得预约</span></div><p className="detail-reason">{attraction.reason || '这里是旅行中值得留出时间慢慢感受的地点，适合根据当天节奏安排停留。'}</p></div><aside className="detail-facts"><div><span>建议游玩时间</span><strong>{Math.round(attraction.duration / 60)} 小时</strong></div><div><span>最佳访问时间</span><strong>上午 9:00 - 18:00</strong></div><div><span>门票信息</span><strong>以现场及官方信息为准</strong></div><div><span>地址</span><strong>{attraction.address || '当地热门区域'}</strong></div><button className="primary-button" type="button" onClick={() => setAdded(true)}>{added ? '已加入行程' : '加入行程'}<Plus size={15} /></button></aside></div>
  </PageFrame>
}

function EditPage({ onNavigate }: { onNavigate: (screen: AppScreen) => void }) {
  const [items, setItems] = useState(['波西塔诺海岸漫步', '海边小镇拍摄', '海边午餐', 'Spiaggia Grande 遗址休闲', '小镇自由活动'])
  return <PageFrame title="编辑行程" eyebrow="日程调整" onBack={() => onNavigate('overview')} actions={<button className="primary-button" type="button" onClick={() => onNavigate('overview')}>保存修改 <Check size={15} /></button>}>
    <div className="edit-day-bar"><strong>Day 3</strong><span>波西塔诺 · 海岸漫步</span><button className="secondary-button" type="button" onClick={() => setItems([...items, '自由探索时间'])}><Plus size={14} />添加活动</button></div>
    <div className="editable-timeline">{items.map((item, index) => <div key={`${item}-${index}`}><span className="timeline-time">{['09:00', '10:00', '12:00', '14:00', '16:00', '19:00'][index] || '20:00'}</span><span className="timeline-dot" /><input value={item} onChange={(event) => setItems(items.map((current, currentIndex) => currentIndex === index ? event.target.value : current))} /><button className="icon-button danger" type="button" title="删除活动" onClick={() => setItems(items.filter((_, currentIndex) => currentIndex !== index))}><Trash2 size={14} /></button></div>)}</div>
  </PageFrame>
}

function MapPage({ onNavigate }: { onNavigate: (screen: AppScreen) => void }) {
  const [day, setDay] = useState(1)
  return <PageFrame title="地图路线" eyebrow="Map & Route" onBack={() => onNavigate('overview')} actions={<button className="primary-button" type="button" onClick={() => onNavigate('overview')}>优化路线 <Route size={15} /></button>}>
    <div className="map-layout"><div className="map-sidebar">{[1, 2, 3, 4, 5, 6].map((item) => <button className={day === item ? 'is-active' : ''} type="button" key={item} onClick={() => setDay(item)}><span>Day {item}</span>{['那不勒斯抵达', '波西塔诺海岸', '自然景观', '阿马尔菲', '卡普里岛', '奥特拉托'][item - 1]}<ChevronRight size={14} /></button>)}</div><div className="map-canvas"><div className="map-grid" /><div className="route-line" /><MapPin className="map-pin pin-a" /><MapPin className="map-pin pin-b" /><MapPin className="map-pin pin-c" /><div className="map-caption"><strong>Day {day} 路线</strong><span>3 个停靠点 · 12.6 km</span></div></div></div>
  </PageFrame>
}

function InspirationPage({ onNavigate }: { onNavigate: (screen: AppScreen) => void }) {
  const [category, setCategory] = useState('全部'); const categories = ['全部', '海岛度假', '沉浸文化', '自然风光', '美食之旅']
  return <PageFrame title="灵感探索" eyebrow="Inspiration"><div className="category-tabs">{categories.map((item) => <button className={category === item ? 'is-active' : ''} type="button" key={item} onClick={() => setCategory(item)}>{item}</button>)}</div><div className="inspiration-grid">{demoStops.slice(3).map((item) => <button type="button" className="inspiration-item" key={item.name} onClick={() => onNavigate('detail')}><img src={item.image} alt={item.name} /><strong>{item.name}</strong><span>{item.city}</span><small><Star size={13} fill="currentColor" /> {item.rating}</small></button>)}</div><button className="wide-outline" type="button" onClick={() => onNavigate('search')}>查看更多灵感 <ArrowRight size={15} /></button></PageFrame>
}

function FavoritesPage({ onNavigate }: { onNavigate: (screen: AppScreen) => void }) {
  const [items, setItems] = useState(demoStops.slice(0, 3));
  return <PageFrame title="收藏地点" eyebrow="Favorites"><div className="favorite-list">{items.map((item) => <div key={item.name} className="favorite-row"><img src={item.image} alt={item.name} /><div><strong>{item.name}</strong><span>{item.city}</span><small><Star size={13} fill="currentColor" /> {item.rating}</small></div><button className="icon-button is-saved" type="button" title="取消收藏" onClick={() => setItems(items.filter((current) => current.name !== item.name))}><Heart size={17} fill="currentColor" /></button></div>)}</div>{items.length === 0 && <div className="empty-inline">还没有收藏的地点</div>}<button className="wide-outline" type="button" onClick={() => onNavigate('inspiration')}>管理收藏 <Settings size={15} /></button></PageFrame>
}

function SharePage({ onNavigate }: { onNavigate: (screen: AppScreen) => void }) {
  const [copied, setCopied] = useState(false)
  return <PageFrame title="分享行程" eyebrow="Share Trip" onBack={() => onNavigate('overview')}><div className="share-layout"><div className="share-preview"><img src={demoStops[0].image} alt="" /><strong>意大利阿马尔菲海岸之旅</strong><span>2024.06.15 · 8天7晚 · 24个地点</span></div><div className="share-control"><label>分享链接</label><div className="share-url"><input readOnly value="https://travelmind.cn/trip/abc123" /><button className="primary-button" type="button" onClick={() => setCopied(true)}><Copy size={14} />{copied ? '已复制' : '复制'}</button></div><label>分享至</label><div className="share-channels"><button type="button" onClick={() => setCopied(true)}>微信</button><button type="button" onClick={() => setCopied(true)}>朋友圈</button><button type="button" onClick={() => setCopied(true)}>QQ</button><button type="button" onClick={() => setCopied(true)}>微博</button></div><button className="wide-outline" type="button" onClick={() => onNavigate('overview')}><ArrowLeft size={15} />返回行程</button></div></div></PageFrame>
}

function ExportPage({ onNavigate }: { onNavigate: (screen: AppScreen) => void }) {
  const [format, setFormat] = useState('pdf'); const [done, setDone] = useState(false)
  const formats = [['pdf', 'PDF 文档', FileText], ['image', '图片长图', FileImage], ['excel', 'Excel 表格', FileSpreadsheet], ['print', '打印版本', CloudDownload]] as const
  return <PageFrame title="导出行程" eyebrow="Export Trip" onBack={() => onNavigate('overview')}><div className="export-options">{formats.map(([key, label, Icon]) => <button className={format === key ? 'is-active' : ''} type="button" key={key} onClick={() => setFormat(key)}><Icon size={26} /><strong>{label}</strong><span>{key === 'pdf' ? '适合打印和分享' : '生成对应格式文件'}</span></button>)}</div><div className="export-preview"><img src={demoStops[0].image} alt="" /><span>当前导出：{formats.find(([key]) => key === format)?.[1]}</span></div><button className="primary-button export-submit" type="button" onClick={() => setDone(true)}>{done ? '已准备下载' : '导出'} <Download size={15} /></button></PageFrame>
}

function SearchPage({ onNavigate }: { onNavigate: (screen: AppScreen) => void }) {
  const [query, setQuery] = useState(''); const filtered = useMemo(() => demoStops.filter((item) => !query || `${item.name}${item.city}`.toLowerCase().includes(query.toLowerCase())), [query])
  return <PageFrame title="搜索与筛选" eyebrow="Search & Filter"><div className="search-toolbar"><div className="search-input"><Search size={16} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索目的地、景点、主题" /></div><select><option>全部目的地</option><option>意大利</option><option>日本</option></select><select><option>全部类型</option><option>自然风光</option><option>历史文化</option></select></div><div className="search-results">{filtered.map((item) => <button type="button" key={item.name} onClick={() => onNavigate('detail')}><img src={item.image} alt="" /><span><strong>{item.name}</strong><small>{item.city}</small></span><span className="rating-text"><Star size={13} fill="currentColor" />{item.rating}</span><ChevronRight size={15} /></button>)}</div></PageFrame>
}

function NotificationsPage({ onNavigate }: { onNavigate: (screen: AppScreen) => void }) {
  const [read, setRead] = useState(false); const notifications = [{ title: '行程生成完成', copy: '你的阿马尔菲海岸之旅已经准备好', time: '10分钟前' }, { title: '资料已更新', copy: '天气和住宿资料已完成匹配', time: '1小时前' }, { title: '路线需要确认', copy: '有 2 个景点建议提前预约', time: '3小时前' }]
  return <PageFrame title="通知中心" eyebrow="Notifications" actions={<button className="text-button" type="button" onClick={() => setRead(true)}>全部标记已读</button>}><div className="notification-list">{notifications.map((item, index) => <button className={read || index === 2 ? 'is-read' : ''} type="button" key={item.title} onClick={() => onNavigate(index === 0 ? 'overview' : 'detail')}><span className="notification-icon"><Bell size={15} /></span><span><strong>{item.title}</strong><small>{item.copy}</small></span><time>{item.time}</time></button>)}</div></PageFrame>
}

function SettingsPage({ onNavigate }: { onNavigate: (screen: AppScreen) => void }) {
  const [saved, setSaved] = useState(false); const [notify, setNotify] = useState(true); const [unit, setUnit] = useState('metric')
  return <PageFrame title="个人设置" eyebrow="Settings"><div className="settings-tabs"><button className="is-active" type="button">个人信息</button><button type="button">偏好设置</button><button type="button">账号安全</button></div><div className="settings-form"><div className="avatar"><UserRound size={24} /></div><label>昵称<input defaultValue="旅行者小明" /></label><label>邮箱<input defaultValue="xiaoming@example.com" /></label><label>默认语言<select><option>简体中文</option><option>English</option><option>日本語</option></select></label><label className="setting-toggle">接收行程通知<button type="button" className={notify ? 'toggle-on' : ''} onClick={() => setNotify(!notify)}><span /></button></label><label>距离单位<select value={unit} onChange={(event) => setUnit(event.target.value)}><option value="metric">公里（km）</option><option value="imperial">英里（mi）</option></select></label><button className="primary-button" type="button" onClick={() => setSaved(true)}>{saved ? '已保存' : '保存设置'}<Check size={15} /></button></div><div className="settings-links"><button className="wide-outline" type="button" onClick={() => onNavigate('xhs-login')}><LogIn size={15} />连接小红书账号</button><button className="wide-outline" type="button" onClick={() => onNavigate('mobile')}><Smartphone size={15} />打开移动端工作台</button></div></PageFrame>
}

function XHSLoginPage({ onNavigate }: { onNavigate: (screen: AppScreen) => void }) {
  const [method, setMethod] = useState<XHSLoginMethod>('qrcode')
  const [loginId, setLoginId] = useState('')
  const [status, setStatus] = useState<XHSLoginStatusResponse | null>(null)
  const [phone, setPhone] = useState('')
  const [code, setCode] = useState('')
  const [cookie, setCookie] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (!loginId || method === 'cookie') return undefined
    let active = true
    const poll = async () => {
      try {
        const next = await getXhsLoginStatus(loginId)
        if (!active) return
        setStatus(next)
        setMessage(next.message)
        if (next.state === 'success') window.setTimeout(() => onNavigate('home'), 400)
      } catch (requestError) {
        if (active) setError(requestError instanceof Error ? requestError.message : '登录状态查询失败')
      }
    }
    void poll()
    const timer = window.setInterval(() => void poll(), 1800)
    return () => { active = false; window.clearInterval(timer) }
  }, [loginId, method, onNavigate])

  const changeMethod = (nextMethod: XHSLoginMethod) => {
    setMethod(nextMethod); setLoginId(''); setStatus(null); setMessage(''); setError(''); setCode('')
  }

  const startQr = async () => {
    setSubmitting(true); setError(''); setMessage('正在准备二维码')
    try {
      const started = await startXhsQrLogin()
      setLoginId(started.login_id); setStatus({ ...started, qr_url: null, user_nickname: null })
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : '二维码登录启动失败')
    } finally { setSubmitting(false) }
  }

  const startPhone = async (event: FormEvent) => {
    event.preventDefault(); setSubmitting(true); setError('')
    try {
      const started = await startXhsPhoneLogin(phone)
      setLoginId(started.login_id); setStatus({ ...started, qr_url: null, user_nickname: null })
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : '验证码发送失败')
    } finally { setSubmitting(false) }
  }

  const verifyPhone = async (event: FormEvent) => {
    event.preventDefault(); setSubmitting(true); setError('')
    try {
      const started = await verifyXhsPhoneLogin(loginId, code)
      setStatus((current) => current ? { ...current, ...started } : { ...started, qr_url: null, user_nickname: null })
      setMessage(started.message)
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : '验证码验证失败')
    } finally { setSubmitting(false) }
  }

  const submitCookie = async (event: FormEvent) => {
    event.preventDefault(); setSubmitting(true); setError('')
    try {
      const started = await loginWithXhsCookie(cookie)
      setMessage(started.message); setCookie('')
      window.setTimeout(() => onNavigate('home'), 400)
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Cookie 验证失败')
    } finally { setSubmitting(false) }
  }

  return <PageFrame title="连接小红书账号" eyebrow="XHS ACCOUNT" onBack={() => onNavigate('settings')}>
    <p className="muted-copy">选择一种方式建立小红书 PC 会话，登录凭证只在服务端处理。</p>
    <div className="xhs-login-tabs">{([['qrcode', '扫码登录'], ['phone', '手机号登录'], ['cookie', 'Cookie 登录']] as const).map(([key, label]) => <button className={method === key ? 'is-active' : ''} type="button" key={key} onClick={() => changeMethod(key)}>{label}</button>)}</div>
    <div className="xhs-login-panel">
      {method === 'qrcode' && <div className="xhs-qr-flow">{status?.qr_url ? <img className="xhs-qr-image" src={`/api/xhs/login/${loginId}/qrcode`} alt="小红书登录二维码" /> : <div className="xhs-qr-placeholder"><LogIn size={30} /><span>{status?.message || '点击按钮生成二维码'}</span></div>}<p>{message || status?.message || '扫码后请在小红书 App 内确认登录'}</p><button className="primary-button" type="button" onClick={() => void startQr()} disabled={submitting}>{submitting ? '准备中…' : status?.qr_url ? '重新生成二维码' : '生成登录二维码'}<RefreshCw size={15} /></button></div>}
      {method === 'phone' && <div className="xhs-form-flow">{!loginId || status?.state === 'error' ? <form onSubmit={(event) => void startPhone(event)}><label>手机号<input value={phone} onChange={(event) => setPhone(event.target.value)} inputMode="numeric" placeholder="请输入手机号" required /></label><button className="primary-button" type="submit" disabled={submitting}>{submitting ? '发送中…' : '发送验证码'}<ArrowRight size={15} /></button></form> : <form onSubmit={(event) => void verifyPhone(event)}><div className="xhs-task-state"><span>验证码已发送至</span><strong>{phone}</strong></div><label>短信验证码<input value={code} onChange={(event) => setCode(event.target.value)} inputMode="numeric" placeholder="请输入验证码" required /></label><button className="primary-button" type="submit" disabled={submitting || status?.state !== 'code_sent'}>{submitting ? '验证中…' : status?.state === 'code_sent' ? '确认登录' : status?.message}<Check size={15} /></button></form>}<p className="xhs-login-message">{message || status?.message || '手机号只用于本次登录任务'}</p></div>}
      {method === 'cookie' && <form className="xhs-form-flow" onSubmit={(event) => void submitCookie(event)}><label>完整 Cookie<textarea value={cookie} onChange={(event) => setCookie(event.target.value)} placeholder="粘贴已登录的小红书 PC Cookie" rows={5} required /></label><p className="xhs-login-message">Cookie 不会保存到浏览器，也不会出现在接口响应和日志中。</p><button className="primary-button" type="submit" disabled={submitting}>{submitting ? '验证中…' : '验证并连接'}<Check size={15} /></button></form>}
    </div>
    {error && <div className="error-banner" role="alert"><span>{error}</span><button type="button" onClick={() => setError('')}>关闭</button></div>}
  </PageFrame>
}

function MobilePage() {
  const [device, setDevice] = useState('home')
  const screens = { home: { title: '发现世界的美好', image: demoStops[0].image }, trip: { title: '阿马尔菲海岸之旅', image: demoStops[1].image }, map: { title: '地图路线', image: demoStops[2].image } }
  const current = screens[device as keyof typeof screens]
  return <PageFrame title="移动端预览" eyebrow="Mobile Preview"><div className="mobile-tabs">{[['home', '首页'], ['trip', '行程'], ['map', '地图']].map(([key, label]) => <button className={device === key ? 'is-active' : ''} type="button" key={key} onClick={() => setDevice(key)}>{label}</button>)}</div><div className="phone-preview"><div className="phone-notch" /><img src={current.image} alt="" /><div className="phone-copy"><strong>{current.title}</strong><span>真实资料，轻松规划每一次出发</span><button className="primary-button" type="button">开始探索</button></div></div></PageFrame>
}

export function PrototypeWorkspace({ screen, result, onNavigate }: PrototypeProps) {
  switch (screen) {
    case 'generating': return <GeneratingPage onNavigate={onNavigate} />
    case 'overview': return <OverviewPage onNavigate={onNavigate} />
    case 'detail': return <DetailPage onNavigate={onNavigate} result={result} />
    case 'edit': return <EditPage onNavigate={onNavigate} />
    case 'map': return <MapPage onNavigate={onNavigate} />
    case 'inspiration': return <InspirationPage onNavigate={onNavigate} />
    case 'favorites': return <FavoritesPage onNavigate={onNavigate} />
    case 'share': return <SharePage onNavigate={onNavigate} />
    case 'export': return <ExportPage onNavigate={onNavigate} />
    case 'search': return <SearchPage onNavigate={onNavigate} />
    case 'notifications': return <NotificationsPage onNavigate={onNavigate} />
    case 'settings': return <SettingsPage onNavigate={onNavigate} />
    case 'xhs-login': return <XHSLoginPage onNavigate={onNavigate} />
    case 'mobile': return <MobilePage />
    default: return null
  }
}
