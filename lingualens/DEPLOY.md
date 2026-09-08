# Deploying LinguaLens

Deployment uses **Vercel** for the React frontend and **Render** for the FastAPI
backend. Do the steps **in this order** because the frontend needs the backend
URL, and the backend's CORS allow-list needs the frontend domain.

> **RAM/cost caveat:** the backend loads PyTorch + EasyOCR, which needs ~1GB+ RAM
> once running. Render's free (512MB) plan is usually too small — use the
> `standard` plan (~$7/mo). First boot also downloads EasyOCR models (~64MB).

---

## Order of operations

```
(a) Deploy backend to Render  ──► get the https:// URL
(b) Deploy frontend to Vercel  ──► get the https:// URL
(c) Update ALLOWED_ORIGINS on Render to the Vercel URL
(d) Re-deploy / refresh both
```

---

## (a) Deploy the backend to Render

Prereq: a [Render account](https://render.com). You use the dashboard CLI-free;

1. Go to Render dashboard → **New** → **Blueprint**.
2. Select this repo (`lingualens`).
3. Render reads `render.yaml` and creates the **lingualens-api** web service
   (Docker runtime, root dir `lingualens`, plan `standard`).
4. After the service is created, go to its **Environment** tab and set
   **GROQ_API_KEY** to your real Groq key (it's marked `sync: false`, so enter it
   manually as a secret). Add **ALLOWED_ORIGINS** with the Vercel URL if you
   already have it (you can add it in step (c) instead).
5. Deploy / let it auto-deploy. When healthy, copy the service URL, e.g.
   `https://lingualens-api.onrender.com`.
6. Verify it's up by visiting `<your-render-url>/api/health` → `{"status":"ok"}`.

---

## (b) Deploy the frontend to Vercel

Prereq: the Vercel CLI (`npm i -g vercel`) or the web dashboard.

CLI:

```bash
vercel login            # log in / create an account
cd frontend
vercel                  # first deploy (interactive)
```

Settings (frame them in the dashboard after import, or via CLI flags):

- **Root directory:** `lingualens/frontend`
- **Framework preset:** Vite
- **Build command:** `npm run build`
- **Output directory:** `dist`
- **Environment variable (`VITE_API_URL`):** set in the Vercel dashboard →
  Project → **Settings → Environment Variables**. Add `VITE_API_URL` =
  `https://lingualens-api.onrender.com` (your Render URL). Do **not** commit a
  real URL — it lives in the dashboard only.

Copy the resulting Vercel URL, e.g. `https://lingualens.vercel.app`.

---

## (c) Allow the Vercel origin on Render

1. Render dashboard → your **lingualens-api** service → **Environment**.
2. Set **ALLOWED_ORIGINS** to your Vercel URL, e.g.
   `https://lingualens.vercel.app` (comma-separate if more than one).
3. **Deploy/Restart** the service to apply the new env var (Render shows a
   "changes pending" banner — click **Deploy** on the latest commit).

> This is the two-way dependency: the frontend needs the backend URL, and the
> backend needs the frontend domain for CORS. Env vars can be updated any time —
> the order above just avoids a dead end.

---

## (d) Redeploy / refresh

1. In Vercel, re-run the build (or push) so the built frontend picks up
   `VITE_API_URL`.
2. Open the Vercel URL, upload an image/PDF, and confirm it hits the Render
   backend (check the backend logs).

---

## Quick local sanity check before deploying

```bash
./run-dev.sh                      # backend :8000 + frontend :5173
```

If it works locally, deployment should mirror the same env vars
(`GROQ_API_KEY`, `ALLOWED_ORIGINS` / `VITE_API_URL`).
