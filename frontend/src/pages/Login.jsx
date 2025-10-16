import React, { useState } from 'react'
import api from '../services/api'

export default function Login({onSuccess}){
  const [email,setEmail] = useState('admin@cdc.com')
  const [password,setPassword] = useState('123456')
  const [error,setError] = useState(null)
  const [loading,setLoading] = useState(false)

  async function handleSubmit(e){
    e.preventDefault()
    setLoading(true); setError(null)
    try{
      const res = await api.post('/api/auth/login', {email,password})
      onSuccess(res.data)
    }catch(err){
      setError(err?.response?.data?.error || 'Falha no login')
    }finally{
      setLoading(false)
    }
  }

  return (
    <div style={{display:'grid', placeItems:'center', height:'100vh'}}>
      <div className="card" style={{width:380}}>
        <div style={{textAlign:'center'}}>
          <img src="/logo.png" alt="Casa do Cigano" style={{height:56}}/>
          <h2 style={{marginBottom:4, color:'var(--vinho)'}}>Fidelidade</h2>
          <p style={{marginTop:0, color:'var(--muted)'}}>Entre para continuar</p>
        </div>
        <form onSubmit={handleSubmit}>
          <label>Email</label>
          <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="email" />
          <label>Senha</label>
          <input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="senha" />
          {error && <p style={{color:'crimson'}}>{error}</p>}
          <button className="btn" disabled={loading} style={{width:'100%', marginTop:12}}>{loading?'Entrando...':'Entrar'}</button>
        </form>
      </div>
    </div>
  )
}
