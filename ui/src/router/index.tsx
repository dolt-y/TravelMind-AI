import { LoaderCircle } from 'lucide-react'
import { Navigate, createBrowserRouter } from 'react-router-dom'
import { AppLayout } from '../layouts/AppLayout'
import { HomeView } from '../views/HomeView'
import { InspirationView } from '../views/InspirationView'
import { LibraryView } from '../views/LibraryView'
import { NotFoundView } from '../views/NotFoundView'
import { PlanningView } from '../views/PlanningView'
import { PlanView } from '../views/PlanView'
import { SettingsView } from '../views/SettingsView'
export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <HomeView /> },
      { path: 'inspiration', element: <InspirationView /> },
      { path: 'plan', element: <PlanView /> },
      { path: 'plan/running', element: <PlanningView /> },
      {
        path: 'results',
        hydrateFallbackElement: <div className="route-loading" role="status"><LoaderCircle className="spin" size={24} aria-hidden="true" /></div>,
        lazy: async () => {
          const { ResultsView } = await import('../views/ResultsView')
          return { Component: ResultsView }
        },
      },
      { path: 'library', element: <LibraryView /> },
      { path: 'settings', element: <SettingsView /> },
      { path: 'discover', element: <Navigate to="/" replace /> },
      { path: '*', element: <NotFoundView /> },
    ],
  },
])
