// frontend/src/pages/AdminGuard.jsx
import React, { useEffect, useState } from 'react'
import { Navigate, Outlet } from 'react-router-dom'
import api from '../services/api'

export default function AdminGuard(){
  const [ok, setOk] = useState(null)
  useEffect(()=>{
    api.get('/api/auth/me')
      .then(r => setOk(r.data?.role === 'ADMIN'))
      .catch(() => setOk(false))
  }, [])
  if (ok === null) return null
  return ok ? <Outlet/> : <Navigate to="/" replace />
}
