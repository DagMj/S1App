# S1 Eksamenstrening MVP

Produksjonsklar kodebase for eksamenstrening i matematikk S1.

## Teknologistack

- Backend: FastAPI + SQLAlchemy + SymPy
- Frontend: React + Vite + TypeScript
- Database: PostgreSQL
- Generatorer: Python-generatorrammeverk (14+ generatorer)
- Grafikk: matplotlib
- Container: Docker / docker-compose

## Prosjektstruktur

- `backend/app/main.py`: API bootstrap, CORS, startup
- `backend/app/generators/`: generatorrammeverk + S1-generatorer
- `backend/app/services/evaluation_engine.py`: robust svarretting
- `backend/app/services/session_service.py`: eksamens- og treningslogikk
- `backend/app/services/asset_service.py`: lokal eller S3/R2 asset-lagring
- `frontend/src/`: sider, komponenter, API-klient
- `docs/API.md`: API-endepunkter
- `docs/ARCHITECTURE.md`: arkitektur
- `docs/DEPLOYMENT.md`: produksjonsdeploy steg for steg

## Lokal utvikling (Docker)

```bash
docker compose up --build
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000/docs`
- Postgres: `localhost:5432`

## Lokal utvikling (uten Docker)

### Backend

```bash
cd backend
pip install -r requirements-dev.txt
cp .env.example .env
python scripts/init_db.py
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Tester

```bash
cd backend
pytest
```

Generator stress-test:

```bash
cd backend
python scripts/generator_stress_test.py --generator linear_equation --count 1000
```

## Produksjon (anbefalt)

Anbefalt setup:

1. Backend + Postgres: Railway
2. Asset-lagring for figurer: Cloudflare R2 (S3-kompatibel)
3. Frontend: Vercel

Se full guide i [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Miljøvariabler backend (prod)

Viktigste variabler:

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `CORS_ORIGINS`
- `ASSET_STORAGE_BACKEND=s3`
- `S3_ENDPOINT_URL`
- `S3_REGION_NAME`
- `S3_BUCKET_NAME`
- `S3_ACCESS_KEY_ID`
- `S3_SECRET_ACCESS_KEY`
- `S3_KEY_PREFIX`
- `ASSETS_PUBLIC_BASE_URL`

## Miljøvariabler frontend (prod)

- `VITE_API_BASE_URL=https://<backend-domene>/api/v1`

## Deploy-filer inkludert

- `backend/railway.json`
- `frontend/vercel.json`
- `backend/.dockerignore`
- `frontend/.dockerignore`
