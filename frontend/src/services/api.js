import axios from 'axios'

// baseURL deve vir do env (defina VITE_API_BASE_URL na Vercel sem barra final ou com /api já)
// ex: VITE_API_BASE_URL=https://fidelidade-backend.onrender.com/api
const base = import.meta.env.VITE_API_BASE_URL || ''
const api = axios.create({
  baseURL: base,
  // se precisar enviar cookies (não parece necessário no seu caso), habilite:
  // withCredentials: true
})

export function setToken(token) {
  if (token) {
    api.defaults.headers.common['Authorization'] = 'Bearer ' + token
  } else {
    delete api.defaults.headers.common['Authorization']
  }
}

api.interceptors.response.use(
  (r) => r,
  (err) => {
    const code = err?.response?.status
    if (code === 401 || code === 422) {
      // limpa e redireciona para login
      try { localStorage.clear() } catch (e) {}
      if (!location.pathname.includes('/login')) location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default Object.assign(api, { setToken })
