# Deployment (Anbefalt Produksjonsoppsett)

Denne guiden setter opp plattformen uten hosting på egen PC.

## Målarkitektur

- Frontend (React): Vercel
- Backend API (FastAPI): Railway
- Database: Railway PostgreSQL
- Figur/assets: Cloudflare R2 (S3-kompatibel, public bucket eller custom domain)

## 1) Forbered repo

Push kode til GitHub først.

```bash
git add .
git commit -m "Prepare cloud deployment"
git push
```

## 2) Opprett Cloudflare R2 (assets)

1. Gå til Cloudflare Dashboard -> R2.
2. Opprett bucket, f.eks. `s1-eksamen-assets`.
3. Opprett API Token (Access Key + Secret).
4. Sett bucket som lesbar offentlig (eller bruk custom public domain).
5. Noter:

- `S3_ENDPOINT_URL` (typisk `https://<accountid>.r2.cloudflarestorage.com`)
- `S3_ACCESS_KEY_ID`
- `S3_SECRET_ACCESS_KEY`
- `S3_BUCKET_NAME`
- `ASSETS_PUBLIC_BASE_URL` (f.eks. `https://pub-xxxx.r2.dev/s1-eksamen-assets` eller eget domene)

## 3) Deploy backend på Railway

1. Opprett Railway-prosjekt.
2. Legg til PostgreSQL i samme prosjekt.
3. Opprett ny service fra GitHub-repo:

- Root directory: `backend`
- Railway vil bruke `backend/Dockerfile` + `backend/railway.json`

4. Sett backend environment variables i Railway:

```env
APP_ENV=prod
APP_DEBUG=false
API_PREFIX=/api/v1
DATABASE_URL=<Railway Postgres URL>
JWT_SECRET_KEY=<lang-random-hemmelighet>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=https://<frontend-domain>

ASSET_STORAGE_BACKEND=s3
S3_ENDPOINT_URL=https://<accountid>.r2.cloudflarestorage.com
S3_REGION_NAME=auto
S3_BUCKET_NAME=s1-eksamen-assets
S3_ACCESS_KEY_ID=<r2-access-key>
S3_SECRET_ACCESS_KEY=<r2-secret-key>
S3_KEY_PREFIX=generated
ASSETS_PUBLIC_BASE_URL=https://<public-r2-domain>

AI_FALLBACK_ENABLED=true
```

5. Deploy og verifiser:

- `https://<railway-backend-domain>/health` -> `{ "status": "ok" }`
- `https://<railway-backend-domain>/docs` åpner Swagger

## 4) Deploy frontend på Vercel

1. Opprett Vercel-prosjekt fra samme GitHub-repo.
2. Sett root directory til `frontend`.
3. Legg til env:

```env
VITE_API_BASE_URL=https://<railway-backend-domain>/api/v1
```

4. Deploy.
5. `frontend/vercel.json` håndterer SPA-routes.

## 5) Koble CORS riktig

Oppdater `CORS_ORIGINS` i Railway backend til eksakt frontend URL(er), kommaseparert ved flere:

```env
CORS_ORIGINS=https://app.dittdomene.no,https://preview-url.vercel.app
```

## 6) Domene (anbefalt)

- Vercel: koble `app.dittdomene.no`
- Railway: koble `api.dittdomene.no`
- Oppdater `VITE_API_BASE_URL` og `CORS_ORIGINS` tilsvarende.

## 7) Etter deploy (sjekkliste)

1. Registrering + login fungerer.
2. Start eksamensøkt (10 oppgaver) fungerer.
3. Grafoppgaver rendres med bilder (R2 URL-er).
4. Svarlevering lagres og progresjon oppdateres.
5. Enter-flyt i oppgaver fungerer (1x evaluer, 2x neste).

## Feilsøking

### Assets vises ikke

- Sjekk `ASSET_STORAGE_BACKEND=s3`
- Sjekk `ASSETS_PUBLIC_BASE_URL`
- Sjekk at bucket er offentlig eller korrekt via custom domain
- Sjekk R2 credentials

### 401/500 på backend

- Sjekk `JWT_SECRET_KEY`
- Sjekk `DATABASE_URL`
- Sjekk Railway logs

### CORS-feil i frontend

- Sjekk `CORS_ORIGINS` matcher frontend URL eksakt
- Sjekk at frontend bruker riktig `VITE_API_BASE_URL`
