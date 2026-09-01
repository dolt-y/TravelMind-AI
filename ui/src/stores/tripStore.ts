import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { extractAttractions, getWeather, searchHotels } from '../services/travel'
import type {
  AttractionResponse,
  HotelSearchResponse,
  WeatherResponse,
} from '../types'

export type TripLanguage = 'zh' | 'en' | 'ja'
export type PlanningStage = 'idle' | 'extracting' | 'enriching' | 'complete' | 'error'

export interface TripDraft {
  city: string
  keywords: string
  language: TripLanguage
  noteLimit: number
}

interface TripState {
  draft: TripDraft
  result: AttractionResponse | null
  weather: WeatherResponse | null
  hotels: HotelSearchResponse | null
  favoritePoiIds: string[]
  planningStage: PlanningStage
  error: string | null
  enrichmentWarning: string | null
  updateDraft: (patch: Partial<TripDraft>) => void
  applyPreset: (city: string, keywords: string) => void
  toggleFavorite: (poiId: string) => void
  runPlanning: () => Promise<boolean>
}

let activePlanningRequest: Promise<boolean> | null = null

export const useTripStore = create<TripState>()(
  persist(
    (set, get) => ({
      draft: { city: '', keywords: '', language: 'zh', noteLimit: 4 },
      result: null,
      weather: null,
      hotels: null,
      favoritePoiIds: [],
      planningStage: 'idle',
      error: null,
      enrichmentWarning: null,
      updateDraft: (patch) => set((state) => ({ draft: { ...state.draft, ...patch } })),
      applyPreset: (city, keywords) => set((state) => ({
        draft: { ...state.draft, city, keywords },
      })),
      toggleFavorite: (poiId) => set((state) => ({
        favoritePoiIds: state.favoritePoiIds.includes(poiId)
          ? state.favoritePoiIds.filter((id) => id !== poiId)
          : [...state.favoritePoiIds, poiId],
      })),
      runPlanning: () => {
        if (activePlanningRequest) return activePlanningRequest

        const draft = get().draft
        activePlanningRequest = (async () => {
          if (!draft.city.trim()) {
            set({ error: '请先填写目的地', planningStage: 'error' })
            return false
          }

          set({
            planningStage: 'extracting',
            result: null,
            weather: null,
            hotels: null,
            error: null,
            enrichmentWarning: null,
          })

          try {
            const result = await extractAttractions({
              city: draft.city.trim(),
              keywords: draft.keywords.trim(),
              language: draft.language,
              note_limit: draft.noteLimit,
            })
            set({ result, planningStage: 'enriching' })

            const [weatherResult, hotelResult] = await Promise.allSettled([
              getWeather(draft.city.trim()),
              searchHotels(draft.city.trim()),
            ])
            const failedServices: string[] = []
            if (weatherResult.status === 'fulfilled') {
              set({ weather: weatherResult.value })
            } else {
              failedServices.push('天气')
            }
            if (hotelResult.status === 'fulfilled') {
              set({ hotels: hotelResult.value })
            } else {
              failedServices.push('酒店')
            }
            set({
              planningStage: 'complete',
              enrichmentWarning: failedServices.length
                ? `${failedServices.join('、')}信息暂时无法获取，景点结果仍可正常查看`
                : null,
            })
            return true
          } catch (error) {
            set({
              planningStage: 'error',
              error: error instanceof Error ? error.message : '旅行资料生成失败',
            })
            return false
          }
        })().finally(() => {
          activePlanningRequest = null
        })

        return activePlanningRequest
      },
    }),
    {
      name: 'travelmind-trip',
      // 只保留用户可继续使用的旅行资料，临时请求、错误和登录凭证不进入本地存储。
      partialize: (state) => ({
        draft: state.draft,
        result: state.result,
        weather: state.weather,
        hotels: state.hotels,
        favoritePoiIds: state.favoritePoiIds,
      }),
    },
  ),
)
