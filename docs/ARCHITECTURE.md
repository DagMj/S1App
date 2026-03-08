# Arkitektur

## Backend

- FastAPI med modulær struktur i `app/api`, `app/services`, `app/generators`, `app/models`.
- SQLAlchemy for persistens.
- Generatorregister synkroniseres mot DB ved oppstart.
- Sessions håndterer både eksamen og trening.
- Asset-lagring støtter:
  - `local` (for lokal utvikling)
  - `s3` (for stateless produksjon via S3/R2)

## Frontend

- React + React Router med dedikerte sider for alle MVP-flyter.
- API-klient i `src/services/api.ts`.
- Komponenter for LaTeX-rendering og oppgavevisning.

## Datamodell

- `users`
- `generator_configs`
- `problem_instances`
- `practice_sessions`
- `session_items`
- `submissions`
- `progress_daily`

## Generatorrammeverk

- Kontrakt: `metadata()`, `generate()`, `evaluate()`, `solution()`.
- Auto-discovery av nye generatorer i `app/generators/library`.
- Generatorer kan produsere figurer via `AssetService` + matplotlib.

## Evaluering

- Lag 1: deterministisk (tall, uttrykk, funksjon, løsningsmengde, intervaller).
- Lag 2: generator-spesifikk overstyring.
- Lag 3: AI-lignende fallback med usikkerhetsflagg.
