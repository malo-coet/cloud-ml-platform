# Frontend — React dashboard

Single-page dashboard for the platform: login, datasets, experiments, models, deployments (pages arrive in Sprint 6 — see [docs/roadmap.md](../docs/roadmap.md)).

Built with React 19, TypeScript and Vite. API calls use relative `/api/...` URLs, proxied to the backend by the Vite dev server (dev) or Traefik (production).

## Run

Inside the full stack (recommended):

```bash
docker compose up -d --build   # from the repository root
```

Standalone:

```bash
cd frontend
npm install
npm run dev        # expects the backend on http://localhost:8000
```

App: http://localhost:5173

## Quality

```bash
npm run build      # type-checks then builds the production bundle
```
