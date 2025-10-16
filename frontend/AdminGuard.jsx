// Drop-in replacement para a página Admin: redireciona se não for ADMIN
import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import AdminPage from './Admin' // se o conteúdo estiver no mesmo arquivo, ajuste conforme seu projeto

export default function AdminGuard(){
  const navigate = useNavigate()

  useEffect(()=>{
    api.get('/api/auth/me')
      .then(r => {
        if (r.data?.role !== 'ADMIN') {
          navigate('/', { replace: true })
        }
      })
      .catch(() => navigate('/', { replace: true }))
  }, [])

  return <AdminPage />
}
