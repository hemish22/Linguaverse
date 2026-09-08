# Deploying LinguaLens

Deployment uses **Render** for the FastAPI backend (free 512MB plan — fine now
that the backend uses Tesseract, not PyTorch) and **Vercel** for the React
frontend. Do the steps **in this order** because the frontend needs the backend
URL, and the backend's CORS allow-list needs the frontend domain.

> **Cold start caveat (free tier):** Render free services spin down after
> ~15 min idle and take ~50s to spin back up on the next request. Expect a slow
> first hit after inactivity.
>
> **Alternate host (not used):** `README_HF.md` keeps the Hugging Face Spaces
> config (Docker SDK, frontmatter) from an earlier iteration. With Tesseract the
> app is much lighter, so Render free works; HF Spaces free is also fine if you
> ever prefer it — just note HF Spaces **Pro** is required for spaces of this
> size, so Render free is the primary target.

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

Prereq: a [Render account](https://render.com).

1. Render dashboard → **New** → **Blueprint**.
2. Connect the **`hemish22/Linguaverse` GitHub repo**.
3. Render reads `render.yaml` and creates the **lingualens-api** web service
   (Docker runtime, repo root, plan `free`).
4. In the service → **Environment** tab, set **GROQ_API_KEY** to your real Groq
   key (`sync: false` in the blueprint means you enter it as a secret; it's
   never written to the repo). You can set **ALLOWED_ORIGINS** here too or in
   step (c).
5. Deploy. When healthy, copy the service URL, e.g.
   `https://lingualens-api.onrender.com`.
6. Verify: visit `<your-render-url>/api/health` → `{"status":"ok"}`.

## (b) Deploy the frontend to Vercel

Prereq: the Vercel CLI (`npm i -g vercel`) or the web dashboard.

CLI:

```bash
vercel login            # log in / create an account
cd frontend
vercel                  # first deploy (interactive)
```

Settings (configure in the dashboard after import):

- **Root directory:** `frontend`
- **Framework preset:** Vite
- **Build command:** `npm run build`
- **Output directory:** `dist`
- **Environment variable (`VITE_API_URL`):** set in the Vercel dashboard →
  Project → **Settings → Environment Variables**, value =
  `https://lingualens-api.onrender.com` (your Render URL). Do **not** commit a
  real URL — it lives in the dashboard only.

Copy the resulting Vercel URL, e.g. `https://lingualens.vercel.app`.

## (c) Allow the Vercel origin on Render

1. Render dashboard → your **lingualens-api** service → **Environment**.
2. Set **ALLOWED_ORIGINS** to your Vercel URL, e.g.
   `https://lingualens.vercel.app` (comma-separate for more than one).
3. **Deploy/Restart** the service to apply the new env var (Render shows a
   "changes pending" banner — click **Deploy** on the latest commit).

> This is the two-way dependency: the frontend needs the backend URL, and the
> backend needs the frontend domain for CORS. Env vars can be updated any time —
> the order above just avoids a dead end.

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