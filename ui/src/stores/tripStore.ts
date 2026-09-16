import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { ApiError } from '../services/http'
import { createTripPlan, getTripHistory, getTripPlan, getTripStatus } from '../services/travel'
import type { TripHistoryItem, TripPlan } from '../types'

export type TripLanguage = 'zh' | 'en' | 'ja'
export type PlanningStage = 'idle' | 'processing' | 'complete' | 'error'

function localDate(offsetDays: number) {
  const value = new Date()
  value.setDate(value.getDate() + offsetDays)
  const timezoneOffset = value.getTimezoneOffset() * 60_000
  return new Date(value.getTime() - timezoneOffset).toISOString().slice(0, 10)
}

export interface TripDraft {
  city: string
  keywords: string
  language: TripLanguage
  noteLimit: number
  startDate: string
  endDate: string
  transportation: 'walking' | 'driving' | 'transit'
  accommodation: string
  travelers: number
  totalBudget: number
  hotelBudgetMax: number
}

interface TripState {
  draft: TripDraft
  plan: TripPlan | null
  history: TripHistoryItem[]
  historyLoading: boolean
  historyErrorPage: number | null
  historyPage: number
  historyPageSize: number
  historyTotal: number
  historyTotalPages: number
  favoritePoiIds: string[]
  planningStage: PlanningStage
  currentStage: string
  progress: number
  taskId: string | null
  error: string | null
  errorCode: string | null
  updateDraft: (patch: Partial<TripDraft>) => void
  applyPreset: (city: string, keywords: string) => void
  toggleFavorite: (poiId: string) => void
  clearPlanningError: () => void
  loadTripHistory: (page?: number) => Promise<void>
  restoreTripPlan: (planId: string) => Promise<void>
  runPlanning: () => Promise<boolean>
}

let activePlanningRequest: Promise<boolean> | null = null
let activeHistoryRequest: Promise<void> | null = null

export const useTripStore = create<TripState>()(
  persist(
    (set, get) => ({
      draft: {
        city: '',
        keywords: '',
        language: 'zh',
        noteLimit: 4,
        startDate: localDate(1),
        endDate: localDate(3),
        transportation: 'transit',
        accommodation: '舒适型酒店',
        travelers: 1,
        totalBudget: 5000,
        hotelBudgetMax: 800,
      },
      plan: null,
      history: [],
      historyLoading: true,
      historyErrorPage: null,
      historyPage: 1,
      historyPageSize: 6,
      historyTotal: 0,
      historyTotalPages: 0,
      favoritePoiIds: [],
      planningStage: 'idle',
      currentStage: 'idle',
      progress: 0,
      taskId: null,
      error: null,
      errorCode: null,
      updateDraft: (patch) => set((state) => ({ draft: { ...state.draft, ...patch } })),
      applyPreset: (city, keywords) => set((state) => ({
        draft: { ...state.draft, city, keywords },
      })),
      toggleFavorite: (poiId) => set((state) => ({
        favoritePoiIds: state.favoritePoiIds.includes(poiId)
          ? state.favoritePoiIds.filter((id) => id !== poiId)
          : [...state.favoritePoiIds, poiId],
      })),
      clearPlanningError: () => set({
        planningStage: 'idle',
        currentStage: 'idle',
        progress: 0,
        taskId: null,
        error: null,
        errorCode: null,
      }),
      loadTripHistory: (page = 1) => {
        if (activeHistoryRequest) return activeHistoryRequest
        set({ historyLoading: true, historyErrorPage: null })
        const request = (async () => {
          try {
            const response = await getTripHistory(page, get().historyPageSize)
            set({
              history: response.items,
              historyPage: response.page,
              historyPageSize: response.page_size,
              historyTotal: response.total,
              historyTotalPages: response.total_pages,
            })
          } catch {
            set({ historyErrorPage: page })
          } finally {
            set({ historyLoading: false })
            activeHistoryRequest = null
          }
        })()
        activeHistoryRequest = request
        return request
      },
      restoreTripPlan: async (planId) => {
        // 历史列表只有摘要，详情页需重新读取完整行程。
        const savedPlan = await getTripPlan(planId)
        set({ plan: savedPlan })
      },
      runPlanning: () => {
        if (activePlanningRequest) return activePlanningRequest

        const draft = get().draft
        activePlanningRequest = (async () => {
          if (!draft.city.trim()) {
            set({ error: '请先填写目的地', errorCode: null, planningStage: 'error' })
            return false
          }

          set({
            planningStage: 'processing',
            currentStage: 'submitted',
            progress: 5,
            plan: null,
            taskId: null,
            error: null,
            errorCode: null,
          })

          try {
            const created = await createTripPlan({
              city: draft.city.trim(),
              start_date: draft.startDate,
              end_date: draft.endDate,
              transportation: draft.transportation,
              accommodation: draft.accommodation,
              preferences: draft.keywords.split(/[,，、]/).map((item) => item.trim()).filter(Boolean),
              free_text_input: draft.keywords.trim(),
              language: draft.language,
              note_limit: draft.noteLimit,
              travelers: draft.travelers,
              total_budget: draft.totalBudget || null,
              hotel_budget_max: draft.hotelBudgetMax || null,
            })
            set({ taskId: created.task_id })

            // 轮询状态，完成后接收完整行程。
            for (let attempt = 0; attempt < 1200; attempt += 1) {
              const task = await getTripStatus(created.task_id)
              set({
                currentStage: task.stage,
                progress: task.progress,
              })
              if (task.status === 'completed' && task.result) {
                set({
                  plan: task.result,
                  planningStage: 'complete',
                  currentStage: 'completed',
                  progress: 100,
                })
                return true
              }
              if (task.status === 'failed') {
                throw new ApiError(
                  task.error || task.message || '旅行计划生成失败',
                  task.error_code || undefined,
                )
              }
              await new Promise((resolve) => window.setTimeout(resolve, 750))
            }
            throw new ApiError('旅行规划时间过长，请稍后重试', 'TRIP_TASK_TIMEOUT')
          } catch (error) {
            set({
              planningStage: 'error',
              error: error instanceof Error ? error.message : '旅行资料生成失败',
              errorCode: error instanceof ApiError ? (error.code || null) : null,
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
      name: 'travelmind-trip-plan',
      // 仅持久化表单、当前行程和收藏。
      partialize: (state) => ({
        draft: state.draft,
        plan: state.plan,
        favoritePoiIds: state.favoritePoiIds,
      }),
    },
  ),
)
