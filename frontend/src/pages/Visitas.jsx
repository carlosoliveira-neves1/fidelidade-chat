import React, { useState } from 'react'
import api from '../services/api'

export default function Visitas(){
  const [cpf,setCpf] = useState('')
  const [resp,setResp] = useState(null)
  const [err,setErr] = useState(null)

  async function registrar(){
    setErr(null); setResp(null)
    try{
      const r = await api.post('/api/visitas', { cpf })
      setResp(r.data)
    }catch(e){
      setErr(e?.response?.data?.error || 'Erro ao registrar')
    }
  }

  return (
    <div>
      <h2 style={{color:'var(--vinho)'}}>Registrar Visita</h2>
      <div className="card">
        <label>CPF</label>
        <input value={cpf} onChange={e=>setCpf(e.target.value)} placeholder="CPF do cliente" />
        <button className="btn" onClick={registrar} style={{marginTop:8}}>Registrar</button>
        {err && <p style={{color:'crimson'}}>{err}</p>}
        {resp && <div style={{marginTop:8}}>
          <div className="card">
            <b>Cliente:</b> {resp.client?.name} — {resp.client?.cpf}<br/>
            <b>Visitas:</b> {resp.visits_count} / <b>Meta:</b> {resp.meta} — {resp.eligible? <span className="pill">Elegível ao brinde</span> : 'Ainda não elegível'}<br/>
            Loja registro: {resp.store_id}
            <div style={{marginTop:8, display:'flex', gap:8, flexWrap:'wrap'}}>
              {resp.whatsapp_url && <a className="btn" href={resp.whatsapp_url} target="_blank" rel="noreferrer">Enviar WhatsApp</a>}
              {resp.whatsapp_image_url && <a className="btn ghost" href={resp.whatsapp_image_url} target="_blank" rel="noreferrer">Baixar Arte</a>}
            </div>
          </div>
        </div>}
      </div>
    </div>
  )
}
