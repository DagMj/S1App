import { Navigate } from 'react-router-dom'

import { getIsAdmin, getToken } from '../services/api'

export function RequireAdmin({ children }: { children: JSX.Element }) {
  if (!getToken()) return <Navigate to="/login" replace />
  if (!getIsAdmin()) return <Navigate to="/dashboard" replace />
  return children
}
