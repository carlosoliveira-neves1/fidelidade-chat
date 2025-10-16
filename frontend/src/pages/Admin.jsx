import React, { useEffect, useState } from 'react'
import api from '../services/api'

export default function Admin(){
  const [stores, setStores] = useState([])
  const [users, setUsers] = useState([])
  const [form, setForm] = useState({ name:'', email:'', role:'ATENDENTE', store_id:'all', password:'' })
  const [editing, setEditing] = useState(null)
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')

  useEffect(()=>{
    // buscar lojas sempre, mesmo que /users falhe
    api.get('/api/admin/stores')
      .then(r=> setStores(r.data))
      .catch(()=> setStores([]))
      .finally(()=>{
        api.get('/api/admin/users')
          .then(r=> setUsers(r.data))
          .catch(e=> console.error(e))
      })
  },[])

  function onChange(e){
    const {name, value} = e.target
    setForm(f=>({...f, [name]: value}))
  }

  async function createUser(){
    setMsg(''); setErr('')
    try{
      const payload = {
        name: form.name,
        email: form.email,
        password: form.password,
        role: form.role,
        store_id: form.store_id === 'all' ? null : Number(form.store_id)
      }
      await api.post('/api/admin/users', payload)
      setForm({ name:'', email:'', role:'ATENDENTE', store_id:'all', password:'' })
      const [u] = await Promise.all([ api.get('/api/admin/users') ])
      setUsers(u.data)
      setMsg('Usuário criado com sucesso.')
    }catch(e){
      setErr(e?.response?.data?.error || 'Erro ao criar usuário')
    }
  }

  function startEdit(u){
    setEditing(u.id)
    setForm({
      name: u.name,
      email: u.email,
      role: u.role,
      store_id: u.store_id ?? 'all',
      password: ''
    })
  }

  async function saveEdit(){
    setMsg(''); setErr('')
    try{
      const payload = {
        name: form.name,
        email: form.email,
        role: form.role,
        store_id: form.store_id === 'all' ? null : Number(form.store_id)
      }
      if(form.password) payload.password = form.password
      await api.put(`/api/admin/users/${editing}`, payload)
      setEditing(null)
      setForm({ name:'', email:'', role:'ATENDENTE', store_id:'all', password:'' })
      const u = await api.get('/api/admin/users')
      setUsers(u.data)
      setMsg('Usuário atualizado.')
    }catch(e){
      setErr(e?.response?.data?.error || 'Erro ao atualizar usuário')
    }
  }

  async function removeUser(id){
    if(!window.confirm('Excluir este usuário?')) return
    setMsg(''); setErr('')
    try{
      await api.delete(`/api/admin/users/${id}`)
      const u = await api.get('/api/admin/users')
      setUsers(u.data)
      setMsg('Usuário excluído.')
    }catch(e){
      setErr(e?.response?.data?.error || 'Erro ao excluir usuário')
    }
  }

  const storeName = (id) => id ? (stores.find(s=>s.id===id)?.name || id) : 'Todas'

  return (
    <div>
      <h2 style={{color:'var(--vinho)'}}>Administração</h2>

      <div className="card">
        <h3>{editing ? 'Editar Usuário' : 'Criar Usuário'}</h3>
        <div className="grid" style={{gridTemplateColumns:'1fr 1fr 1fr 1fr'}}>
          <input name="name" placeholder="Nome" value={form.name} onChange={onChange} />
          <input name="email" placeholder="Email" value={form.email} onChange={onChange} />
          <input name="password" placeholder={editing ? 'Nova senha (opcional)' : 'Senha'} value={form.password} onChange={onChange} />
          <select name="role" value={form.role} onChange={onChange}>
            <option value="ATENDENTE">ATENDENTE</option>
            <option value="GERENTE">GERENTE</option>
            <option value="ADMIN">ADMIN</option>
          </select>
          <select name="store_id" value={form.store_id} onChange={onChange}>
            <option value="all">Todas as lojas</option>
            {stores.map(s=> <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <div style={{gridColumn:'span 3', display:'flex', gap:8, justifyContent:'flex-end'}}>
            {editing ? (
              <>
                <button className="btn ghost" onClick={()=>{ setEditing(null); setForm({ name:'', email:'', role:'ATENDENTE', store_id:'all', password:'' })}}>Cancelar</button>
                <button className="btn" onClick={saveEdit}>Salvar alterações</button>
              </>
            ) : (
              <button className="btn" onClick={createUser}>Criar Usuário</button>
            )}
          </div>
        </div>
        {msg && <p style={{color:'green', marginTop:8}}>{msg}</p>}
        {err && <p style={{color:'crimson', marginTop:8}}>{err}</p>}
      </div>

      <div className="card" style={{marginTop:16}}>
        <h3>Usuários</h3>
        <div className="table">
          <div className="tr head">
            <div className="td">Nome</div>
            <div className="td">Email</div>
            <div className="td">Papel</div>
            <div className="td">Loja</div>
            <div className="td" style={{textAlign:'right'}}>Ações</div>
          </div>
          {users.map(u=> (
            <div className="tr" key={u.id}>
              <div className="td">{u.name}</div>
              <div className="td">{u.email}</div>
              <div className="td"><span className="pill">{u.role}</span></div>
              <div className="td">{storeName(u.store_id)}</div>
              <div className="td" style={{textAlign:'right'}}>
                <button className="btn ghost" onClick={()=>startEdit(u)}>Editar</button>
                <button className="btn danger" onClick={()=>removeUser(u.id)} style={{marginLeft:8}}>Excluir</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
