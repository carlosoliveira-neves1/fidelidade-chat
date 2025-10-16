# Frontend Fix Pack (Vercel + Vite)

Arquivos incluídos (substitua dentro de `frontend/` do seu projeto):
- `vercel.json`  → Rotas corretas para SPA e proxy do backend.
- `vite.config.js` → Garante `base: '/'` para servir assets corretamente.
- `src/services/api.js` → Usa `VITE_API_BASE` (defina `/api` na Vercel).
- `.env.example` → Exemplo das variáveis que devem estar na Vercel.

## Passos
1. Copie estes arquivos para a pasta `frontend/` do seu repo.
2. Commit & push:
   ```bash
   git add frontend/vercel.json frontend/vite.config.js frontend/src/services/api.js frontend/.env.example
   git commit -m "chore(frontend): fix vercel routes + vite base + api base"
   git push origin main
   ```
3. Na Vercel (Project → Settings → Environment Variables), crie/ajuste:
   ```
   VITE_API_BASE=/api
   VITE_APP_NAME=Casa do Cigano Fidelidade
   VITE_DEFAULT_THEME=light
   VITE_ALLOWED_ORIGINS=https://fidelidade-chat.vercel.app,https://fidelidade-chat-dgfz22.vercel.app,http://localhost:5173
   VITE_ENV=production
   ```
4. Em **Build & Development Settings**:
   - Root Directory: `frontend`
   - Framework Preset: `Vite`
   - Install Command: `npm install`
   - Build Command: `npm run build`
   - Output Directory: `dist`

5. Faça um **Redeploy**.
6. Teste a URL de produção. O erro *"Failed to load module script (text/html)"* deve desaparecer.
