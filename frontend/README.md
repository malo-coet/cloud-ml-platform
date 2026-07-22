# Frontend — React dashboard

Single-page dashboard for the platform. Built with React 19, TypeScript, Vite,
React Router and Recharts. API calls use relative `/api/...` URLs, proxied to the
backend by the Vite dev server (dev) or Traefik (production).

## Pages

| Route | Purpose |
|---|---|
| `/login` | JWT sign-in (token in localStorage, auto sign-out on 401) |
| `/datasets` | Upload, download, delete datasets; launch a training run in one click |
| `/experiments` | Training-job history (live-refreshing) + MLflow runs with an accuracy chart |
| `/models` | Models in the MLflow Model Registry, with their versions |
| `/deployments` | Placeholder — model serving arrives in Sprint 7 |
| `/profile` | Account settings; admins also manage team members |

## Structure

```
src/
├── api/        # typed fetch client, shared types, useApi hook
├── auth/       # AuthContext (token + current user) and useAuth hook
├── components/ # Layout, ProtectedRoute, Modal, StatusBadge, states…
├── lib/        # formatting helpers
└── pages/      # one file + CSS module per route
```

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
npm run build      # type-checks (tsc) then builds the production bundle
```
