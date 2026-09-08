# Deploying LinguaLens

Deployment uses **Hugging Face Spaces** for the FastAPI backend (free 16GB RAM —
torch/EasyOCR need ~1GB+) and **Vercel** for the React frontend. Do the steps
**in this order** because the frontend needs the backend URL, and the backend's
CORS allow-list needs the frontend domain.

> **Cold start caveat:** on first boot the Space downloads EasyOCR models
> (~64MB) and loads torch, so the first request after a build/cold start can be
> slow. HF's storage/image soft limit is 10GB — fine for this app.
>
> **Alternative/paid option:** `render.yaml` at the repo root remains available
> as a Render.com deployment (Blueprint, Docker, `standard` plan ~$7/mo) if you
> prefer to self-host on a paid tier. The steps below use HF Spaces as the
> primary (free) path.

---

## Order of operations

```
(a) Create the HF Space + set GROQ_API_KEY secret
(b) Push backend files to the Space git repo
(c) Wait for build → get https://<user>-<space>.hf.space
(d) Deploy frontend to Vercel (VITE_API_URL = Space URL)
(e) Set ALLOWED_ORIGINS on the Space to the Vercel domain, restart
```

---

## (a) Create a Hugging Face account + Space

1. Create/have a [Hugging Face account](https://huggingface.co/join).
2. Go to [huggingface.co/new-space](https://huggingface.co/new-space).
3. **Space name:** `lingualens-api` (or any name). Owner: your username.
4. **SDK:** choose **Docker**. (This makes HF run our `Dockerfile`.)
5. Leave the rest default and click **Create Space**.

## (b) Set the secrets

1. In the Space, open **Settings** → **Variables and secrets** (right side,
   "Secrets" tab).
2. Add a secret **`GROQ_API_KEY`** with your real Groq key.
3. Add a secret **`ALLOWED_ORIGINS`** — you can leave it empty for now and fill
   it in step (e); it just needs the Vercel domain once the frontend exists.
4. Secrets are **not** committed to the repo — they live in the dashboard only.

## (c) Push the backend files to the Space git repo

The Space is a git repo. From the repo root, push the backend to it:

```bash
cd lingualens
git remote add space https://huggingface.co/spaces/<user>/<space-name>
git add Dockerfile requirements.txt api.py ocr_module.py llm_module.py utils.py pdf_extract.py README_HF.md
git commit -m "Backend: Dockerfile + app modules"
git push space HEAD:main
```

Note: HF requires the **Space root's `README.md`** to carry the app metadata.
Rename/copy `README_HF.md` (the file with the YAML frontmatter: `sdk: docker`,
`app_port: 7860`, etc.) to `README.md` in the Space repo before/after pushing —
it must be at the Space root, not a subfolder. The other files (`api.py`,
`ocr_module.py`, `llm_module.py`, `utils.py`, `pdf_extract.py`, `Dockerfile`,
`requirements.txt`) go at the root too.

## (d) Build and get the URL

1. HF rebuilds on push. Watch the **Builder** tab / logs until it says the app
   is **Running**.
2. Your API URL is `https://<user>-<space>.hf.space`.
3. Verify health: open `https://<user>-<space>.hf.space/api/health` → expect
   `{"status":"ok"}`.

## (e) Deploy the frontend to Vercel

Prereq: the Vercel CLI (`npm i -g vercel`) or the web dashboard.

CLI:

```bash
vercel login            # log in / create an account
cd frontend
vercel                  # first deploy (interactive)
```

Settings (configure in the dashboard after import):

- **Root directory:** `lingualens/frontend`
- **Framework preset:** Vite
- **Build command:** `npm run build`
- **Output directory:** `dist`
- **Environment variable (`VITE_API_URL`):** set in the Vercel dashboard →
  Project → **Settings → Environment Variables**, value =
  `https://<user>-<space>.hf.space` (your HF Space URL). Do **not** commit a
  real URL — it lives in the dashboard only.

Copy the resulting Vercel URL, e.g. `https://lingualens.vercel.app`.

## (f) Allow the Vercel origin on the Space

1. Back in the HF Space → **Settings** → **Variables and secrets**.
2. Set secret **`ALLOWED_ORIGINS`** to your Vercel URL, e.g.
   `https://lingualens.vercel.app` (comma-separate for more than one).
3. **Restart** the Space (`⋮` menu → **Restart**) to apply the new env vars.

> This is the two-way dependency: the frontend needs the backend URL, and the
> backend needs the frontend domain for CORS. Secrets can be updated any time —
> the order above just avoids a dead end.

---

## Quick local sanity check before deploying

```bash
./run-dev.sh                      # backend :8000 + frontend :5173
```

If it works locally, deployment should mirror the same env vars
(`GROQ_API_KEY`, `ALLOWED_ORIGINS` / `VITE_API_URL`). The only difference in
production is the port (HF forces 7860, handled by `Dockerfile`).

---

## Render alternative (paid)

`render.yaml` at the repo root is a working Blueprint: one web service
(`lingualens-api`, Docker, rootDir `lingualens`, health check `/api/health`).
The `Dockerfile` works on Render as-is: the CMD uses `${PORT:-7860}`, and Render
injects its own `$PORT` (which overrides the fallback), so no edit is required —
`EXPOSE` is informational only in Render's Docker runtime.