import React, { useEffect, useState } from 'react'
import api from '../services/api'

export default function Dashboard(){
  const [kpis, setKpis] = useState({visitas_30d:0, clientes_total:0, resgates_30d:0})
  const [anivCount, setAnivCount] = useState(0)
  const [loading, setLoading] = useState(false)

  useEffect(()=>{
    (async()=>{
      try{
        const [k, a] = await Promise.all([
          api.get('/api/dashboard/kpis'),
          api.get('/api/dashboard/aniversariantes')
        ])
        setKpis(k.data)
        setAnivCount((a.data||[]).length)
      }catch(e){ console.error(e) }
    })()
  },[])

  async function exportar(){
    try{
      setLoading(true)
      const r = await api.get('/api/dashboard/aniversariantes_export', { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([r.data]))
      const a = document.createElement('a')
      a.href = url
      a.download = r.headers['content-disposition']?.split('filename=')[1]?.replace(/"/g,'') || 'aniversariantes.xlsx'
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    }catch(e){ console.error(e) } finally { setLoading(false) }
  }

  const card = (title,value) => (
    <div className="kpi">
      <div className="kpi-title">{title}</div>
      <div className="kpi-value">{value}</div>
    </div>
  )

  return (
    <div>
      <h2 style={{color:'var(--vinho)'}}>Dashboard</h2>
      <div className="kpi-grid">
        {card('Visitas (30d)', kpis.visitas_30d)}
        {card('Clientes', kpis.clientes_total)}
        {card('Resgates (30d)', kpis.resgates_30d)}
      </div>

      <div className="card" style={{marginTop:16}}>
        <h3>Aniversariantes deste mês</h3>
        <div style={{display:'flex', alignItems:'center', gap:12}}>
          <div className="pill">{anivCount}</div>
          <button className="btn" onClick={exportar} disabled={loading}>
            {loading ? 'Gerando...' : 'Exportar Excel'}
          </button>
        </div>
        <p style={{marginTop:8, color:'#666'}}>A listagem completa sai no Excel.</p>
      </div>
    </div>
  )
}
