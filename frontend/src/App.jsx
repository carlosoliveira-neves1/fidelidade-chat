import React, { useEffect, useState } from 'react'
import { Routes, Route, Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Clientes from './pages/Clientes'
import Visitas from './pages/Visitas'
import Resgates from './pages/Resgates'
import Admin from './pages/Admin'
import api from './services/api'

function Sidebar({path}){
  return (
    <aside className="sidebar">
      <div className="brand">
        <img src="/logo.png" alt="Casa do Cigano" />
        <h1>Fidelidade</h1>
      </div>
      <nav className="nav">
        <Link className={path==='/'?'active':''} to="/">Dashboard</Link>
        <Link className={path.startsWith('/clientes')?'active':''} to="/clientes">Clientes</Link>
        <Link className={path.startsWith('/visitas')?'active':''} to="/visitas">Visitas</Link>
        <Link className={path.startsWith('/resgates')?'active':''} to="/resgates">Resgates</Link>
        <Link className={path.startsWith('/admin')?'active':''} to="/admin">Admin</Link>
      </nav>
      <div style={{marginTop:'auto', fontSize:12, color:'#6b6b6b'}}>
        <p>Casa do Cigano ©</p>
      </div>
    </aside>
  )
}

function Topbar({user, onLogout}){
  return (
    <div className="topbar">
      <b style={{color:'var(--vinho)'}}>{user?.name}</b>
      <span className="pill">{user?.role}{user?.lock_loja ? ' · Loja Fixa' : ' · Todas'}</span>
      <div style={{marginLeft:'auto'}}>
        <button className="btn ghost" onClick={onLogout}>Sair</button>
      </div>
    </div>
  )
}

export default function App(){
  const [user,setUser] = useState(null)
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(()=>{
    const saved = localStorage.getItem('user')
    const token = localStorage.getItem('token')
    if(saved && token){
      setUser(JSON.parse(saved))
      api.setToken(token)
    }
  },[])

  function onLoginSuccess(payload){
    localStorage.setItem('token', payload.token)
    localStorage.setItem('user', JSON.stringify(payload.user))
    api.setToken(payload.token)
    setUser(payload.user)
    navigate('/')
  }
  function onLogout(){
    localStorage.clear()
    setUser(null)
    navigate('/login')
  }

  if(!user){
    return (
      <Routes>
        <Route path="/login" element={<Login onSuccess={onLoginSuccess} />} />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    )
  }

  return (
    <div className="layout">
      <Sidebar path={location.pathname} />
      <main>
        <Topbar user={user} onLogout={onLogout} />
        <div className="container">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/clientes" element={<Clientes />} />
            <Route path="/visitas" element={<Visitas />} />
            <Route path="/resgates" element={<Resgates />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </div>
      </main>
    </div>
  )
}
