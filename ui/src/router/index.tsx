import { Navigate, createBrowserRouter } from 'react-router-dom'
import { AppLayout } from '../layouts/AppLayout'
import { HomeView } from '../views/HomeView'
import { InspirationView } from '../views/InspirationView'
import { LibraryView } from '../views/LibraryView'
import { NotFoundView } from '../views/NotFoundView'
import { PlanningView } from '../views/PlanningView'
import { PlanView } from '../views/PlanView'
import { ResultsView } from '../views/ResultsView'
import { SettingsView } from '../views/SettingsView'
import { XhsAdminView } from '../views/XhsAdminView'

export const router = createBrowserRouter([
  { path: '/admin/integrations/xhs', element: <XhsAdminView /> },
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <HomeView /> },
      { path: 'inspiration', element: <InspirationView /> },
      { path: 'plan', element: <PlanView /> },
      { path: 'plan/running', element: <PlanningView /> },
      { path: 'results', element: <ResultsView /> },
      { path: 'library', element: <LibraryView /> },
      { path: 'settings', element: <SettingsView /> },
      { path: 'discover', element: <Navigate to="/" replace /> },
      { path: '*', element: <NotFoundView /> },
    ],
  },
])
