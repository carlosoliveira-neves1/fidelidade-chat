import React, { useEffect, useState } from 'react'
import api from '../services/api'

export default function Clientes(){
  const [cpf,setCpf] = useState('')
  const [page,setPage] = useState(1)
  const [items,setItems] = useState([])
  const [total,setTotal] = useState(0)
  const [form,setForm] = useState({name:'',cpf:'',phone:'',email:'',birthday:''})

  async function load(){
    const r = await api.get('/api/clientes?cpf='+encodeURIComponent(cpf)+'&page='+page+'&per_page=10')
    setItems(r.data.items); setTotal(r.data.total)
  }
  useEffect(()=>{ load() },[page])

  async function create(e){
    e.preventDefault()
    await api.post('/api/clientes', form)
    setForm({name:'',cpf:'',phone:'',email:'',birthday:''})
    setPage(1); load()
  }

  return (
    <div>
      <h2 style={{color:'var(--vinho)'}}>Clientes</h2>
      <div className="card">
        <form onSubmit={create}>
          <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:8}}>
            <div><label>Nome</label><input value={form.name} onChange={e=>setForm({...form,name:e.target.value})} required /></div>
            <div><label>CPF</label><input value={form.cpf} onChange={e=>setForm({...form,cpf:e.target.value})} /></div>
            <div><label>Telefone</label><input value={form.phone} onChange={e=>setForm({...form,phone:e.target.value})} /></div>
            <div><label>Email</label><input type="email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})} /></div>
            <div><label>Nascimento</label><input type="date" value={form.birthday} onChange={e=>setForm({...form,birthday:e.target.value})} /></div>
          </div>
          <button className="btn" style={{marginTop:8}}>Cadastrar</button>
        </form>
      </div>

      <div className="card">
        <label>Buscar por CPF</label>
        <input value={cpf} onChange={e=>setCpf(e.target.value)} placeholder="000.000.000-00" />
        <button className="btn" style={{marginTop:8}} onClick={()=>{setPage(1); load()}}>Buscar</button>
      </div>
      <table className="card">
        <thead><tr><th>Nome</th><th>CPF</th><th>Telefone</th><th>Email</th><th>Nasc.</th></tr></thead>
        <tbody>{items.map(c=>(<tr key={c.id}><td>{c.name}</td><td>{c.cpf}</td><td>{c.phone}</td><td>{c.email}</td><td>{c.birthday}</td></tr>))}</tbody>
      </table>
      <div style={{display:'flex', gap:8}}>
        <button className="btn ghost" onClick={()=>setPage(p=>Math.max(1,p-1))}>Anterior</button>
        <span style={{alignSelf:'center'}}>Página {page}</span>
        <button className="btn" onClick={()=>setPage(p=>p+1)}>Próxima</button>
      </div>
    </div>
  )
}
