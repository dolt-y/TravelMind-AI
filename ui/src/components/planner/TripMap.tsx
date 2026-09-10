import { load as loadAmap } from '@amap/amap-jsapi-loader'
import { CircleAlert, LoaderCircle, MapPinOff, MapPinned } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import type { TripDay } from '../../types'

interface TripMapProps {
  days: TripDay[]
}

type MapStatus = 'loading' | 'ready' | 'missing-key' | 'empty' | 'error'
type MapOverlay = object

interface MapInstance {
  add: (overlays: MapOverlay[]) => void
  setFitView: (overlays?: MapOverlay[], immediately?: boolean, avoid?: number[], maxZoom?: number) => void
  destroy: () => void
}

interface AMapSdk {
  Map: new (container: HTMLDivElement, options: Record<string, unknown>) => MapInstance
  Marker: new (options: Record<string, unknown>) => MapOverlay
  Polyline: new (options: Record<string, unknown>) => MapOverlay
}

const ROUTE_COLORS = ['#345f7a', '#d37a57', '#3d8067', '#c4893f']

export function TripMap({ days }: TripMapProps) {
  const { t } = useTranslation()
  const [selectedDayIndex, setSelectedDayIndex] = useState(0)
  const [status, setStatus] = useState<MapStatus>('loading')
  const containerRef = useRef<HTMLDivElement>(null)
  const selectedDay = days[selectedDayIndex] ?? days[0]
  const apiKey = import.meta.env.VITE_AMAP_JS_KEY?.trim()
  const securityCode = import.meta.env.VITE_AMAP_SECURITY_CODE?.trim()

  useEffect(() => {
    setSelectedDayIndex((current) => Math.min(current, Math.max(days.length - 1, 0)))
  }, [days.length])

  useEffect(() => {
    const container = containerRef.current
    if (!apiKey) {
      setStatus('missing-key')
      return
    }
    if (!container || !selectedDay) {
      setStatus('empty')
      return
    }

    const attractions = selectedDay.attractions.filter((item) => item.location)
    const routePaths = selectedDay.routes.flatMap((segment, routeIndex) => (
      segment.route.steps
        .filter((step) => step.polyline.length > 1)
        .map((step) => ({
          color: ROUTE_COLORS[routeIndex % ROUTE_COLORS.length],
          path: step.polyline.map((point) => [point.longitude, point.latitude]),
        }))
    ))

    if (!attractions.length && !routePaths.length) {
      setStatus('empty')
      return
    }

    let active = true
    let map: MapInstance | null = null
    setStatus('loading')

    // 高德安全密钥必须在地图脚本加载前设置，且只保留在当前浏览器运行环境中。
    if (securityCode) window._AMapSecurityConfig = { securityJsCode: securityCode }

    void loadAmap({ key: apiKey, version: '2.0', plugins: [] })
      .then((sdk: unknown) => {
        if (!active) return
        const AMap = sdk as AMapSdk
        map = new AMap.Map(container, { zoom: 12, viewMode: '2D' })
        const overlays: MapOverlay[] = []

        attractions.forEach((attraction, index) => {
          const location = attraction.location
          if (!location) return
          overlays.push(new AMap.Marker({
            position: [location.longitude, location.latitude],
            title: attraction.name,
            content: `<span class="trip-map__marker"><b>${index + 1}</b></span>`,
            anchor: 'bottom-center',
          }))
        })

        routePaths.forEach(({ color, path }) => {
          overlays.push(new AMap.Polyline({
            path,
            strokeColor: color,
            strokeOpacity: 0.92,
            strokeWeight: 6,
            lineJoin: 'round',
            lineCap: 'round',
            showDir: true,
          }))
        })

        map.add(overlays)
        map.setFitView(overlays, false, [54, 54, 54, 54], 16)
        setStatus('ready')
      })
      .catch(() => {
        if (active) setStatus('error')
      })

    // 切换日期或离开结果页时销毁旧地图，避免重复绑定画布和事件。
    return () => {
      active = false
      map?.destroy()
    }
  }, [apiKey, securityCode, selectedDay])

  const stateContent = {
    loading: { icon: LoaderCircle, copy: t('tripVisuals.map.loading') },
    'missing-key': { icon: MapPinOff, copy: t('tripVisuals.map.unavailable') },
    empty: { icon: MapPinOff, copy: t('tripVisuals.map.empty') },
    error: { icon: CircleAlert, copy: t('tripVisuals.map.error') },
    ready: null,
  }[status]

  return (
    <section className="result-visual result-visual--map" aria-labelledby="trip-map-title">
      <header className="result-visual__heading">
        <MapPinned size={22} aria-hidden="true" />
        <div>
          <h2 id="trip-map-title">{t('tripVisuals.map.title')}</h2>
        </div>
      </header>
      <div className="trip-map__tabs" role="tablist" aria-label={t('tripVisuals.map.days')}>
        {days.map((day, index) => (
          <button
            className={index === selectedDayIndex ? 'is-active' : ''}
            id={`trip-map-tab-${index}`}
            key={day.date}
            type="button"
            role="tab"
            aria-controls="trip-route-map"
            aria-selected={index === selectedDayIndex}
            onClick={() => setSelectedDayIndex(index)}
          >
            <strong>{t('tripVisuals.map.day', { day: day.day_index })}</strong>
            <span>{day.date.slice(5)}</span>
          </button>
        ))}
      </div>
      <div className="trip-map__body">
        <div
          ref={containerRef}
          id="trip-route-map"
          className="trip-map__canvas"
          role="tabpanel"
          aria-labelledby={`trip-map-tab-${selectedDayIndex}`}
          aria-label={selectedDay ? t('tripVisuals.map.aria', { day: selectedDay.day_index, city: selectedDay.city }) : t('tripVisuals.map.title')}
        />
        {stateContent && (
          <div className="trip-map__state" role="status">
            <stateContent.icon className={status === 'loading' ? 'spin' : ''} size={25} aria-hidden="true" />
            <span>{stateContent.copy}</span>
          </div>
        )}
      </div>
    </section>
  )
}
