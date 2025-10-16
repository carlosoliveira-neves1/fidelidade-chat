import React, { useState } from 'react'
import api from '../services/api'

export default function Resgates(){
  const [cpf,setCpf] = useState('')
  const [gift,setGift] = useState('Brinde')
  const [resp,setResp] = useState(null)
  const [err,setErr] = useState(null)

  async function resgatar(){
    setErr(null); setResp(null)
    try{
      const r = await api.post('/api/resgates', { cpf, gift_name: gift })
      setResp(r.data)
    }catch(e){
      setErr(e?.response?.data?.error || 'Erro ao resgatar')
    }
  }

  return (
    <div>
      <h2 style={{color:'var(--vinho)'}}>Resgatar Brinde</h2>
      <div className="card">
        <label>CPF</label>
        <input value={cpf} onChange={e=>setCpf(e.target.value)} placeholder="CPF do cliente" />
        <label>Brinde</label>
        <input value={gift} onChange={e=>setGift(e.target.value)} placeholder="Descrição do brinde" />
        <button className="btn" onClick={resgatar} style={{marginTop:8}}>Resgatar</button>
        {err && <p style={{color:'crimson'}}>{err}</p>}
        {resp && <div className="card" style={{marginTop:8}}>
          <b>Resgate #{resp.redemption_id}</b><br/>
          Brinde: {resp.gift_name}<br/>
          Quando: {resp.when}<br/>
          Loja registro: {resp.store_id}
        </div>}
      </div>
    </div>
  )
}
