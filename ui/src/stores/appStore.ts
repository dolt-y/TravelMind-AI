import { create } from 'zustand'
import { getHealth } from '../services/travel'

type HealthState = 'idle' | 'checking' | 'online' | 'needs_config' | 'offline'

interface AppState {
  mobileMenuOpen: boolean
  healthState: HealthState
  setMobileMenuOpen: (open: boolean) => void
  refreshHealth: () => Promise<void>
}

export const useAppStore = create<AppState>((set) => ({
  mobileMenuOpen: false,
  healthState: 'idle',
  setMobileMenuOpen: (mobileMenuOpen) => set({ mobileMenuOpen }),
  refreshHealth: async () => {
    set({ healthState: 'checking' })
    try {
      const health = await getHealth()
      set({
        healthState: health.configured && health.vendor_present ? 'online' : 'needs_config',
      })
    } catch {
      set({ healthState: 'offline' })
    }
  },
}))
