# Roadmap

The platform is built in 8 sprints of 1–2 weeks, each delivering something working. Phases refer to the overall project plan; sprints are the execution order.

## Sprint 1 — Foundations ✅

> Phases 1 & 2: project architecture, repository, local dev stack.

- [x] Repository structure (frontend, backend, services, infra, docs)
- [x] Base documentation (README, architecture, roadmap, tech choices)
- [x] Docker Compose stack: PostgreSQL, Redis, Kafka (KRaft), MinIO, MLflow
- [x] FastAPI skeleton with health endpoint
- [x] React + Vite + TypeScript skeleton
- [x] CI pipeline (lint, tests, build, compose validation)

## Sprint 2 — Backend core & auth ✅

> Phase 3: API, users, database.

- [x] SQLAlchemy models + Alembic migrations (users table)
- [x] JWT authentication (`POST /auth/login`), password hashing (Argon2)
- [x] User management endpoints (register, profile, admin listing and deletion)
- [x] Unit and integration tests (pytest, in-memory database)

## Sprint 3 — Datasets ✅

> Phase 4: dataset upload and storage.

- [x] `POST /datasets` upload (CSV, images, ZIP, Parquet) streamed to MinIO
- [x] Metadata in PostgreSQL: owner, date, version, size, type
- [x] `GET /datasets` listing with pagination + presigned download URLs
- [x] Dataset versioning (same name → auto-incremented version)
- [x] Adminer added to the dev stack to browse the database

## Sprint 4 — Training & MLflow ✅

> Phases 5 & 7: training microservice, experiment tracking.

- [x] Training service worker (claims queued jobs with `FOR UPDATE SKIP LOCKED`)
- [x] Tabular pipeline: fetch from MinIO → preprocess → train → metrics → MLflow
- [x] Two model types (logistic regression, random forest) with hyperparameters
- [x] Model Registry usage (each run registers a `{dataset}-classifier` version)
- [x] `POST /train`, `GET /train`, `GET /experiments`, `GET /models` endpoints
- [ ] MNIST, then CIFAR-10 (PyTorch) — after the event-driven refactor (Sprint 5)

## Sprint 5 — Event-driven architecture ✅

> Phase 6: Kafka everywhere.

- [x] Kafka producer in the backend (`TrainingRequested`)
- [x] Kafka consumer in the training service (replaces database polling)
- [x] Job status lifecycle (`queued → running → completed/failed`) driven by events
- [x] `TrainingCompleted` event + dead-letter topic for poison messages
- [x] Idempotent processing (redelivered events are skipped)

## Sprint 6 — Frontend ✅

> Phase 17: dashboard.

- [x] Login page + JWT session handling (localStorage, auto-logout on 401)
- [x] Datasets page: upload, download, delete, one-click training
- [x] Experiments page: live-refreshing job history + MLflow runs
- [x] Metric charts (accuracy bar chart, precision/recall/F1 table)
- [x] Models page (registry) and Profile page (with admin user management)

## Sprint 7 — VPS & Kubernetes 🚧

> Phases 8–12: production infrastructure.

- [x] DigitalOcean droplet provisioning (OpenTofu: droplet, firewall, SSH key)
- [x] Hardening: deploy user, key-only SSH, UFW, Fail2Ban, unattended upgrades, swap
- [x] k3s + Traefik + cert-manager (Let's Encrypt `ClusterIssuer`)
- [x] Kubernetes manifests for every component (+ Ingress and TLS)
- [x] Container images published to GHCR by CI
- [x] Deployment guide ([docs/deployment.md](deployment.md))
- [ ] Apply to the live droplet and DNS sub-domains under `mlops.mcoet.com`
- [ ] Deployment service: model → Docker image → k8s Deployment → prediction endpoint

## Sprint 8 — Observability, security, CI/CD

> Phases 13–16 & 18: production quality.

- [ ] Prometheus + Grafana + Node Exporter + kube-state-metrics
- [ ] Loki + Promtail centralized logging
- [ ] Structured application logging + error handling
- [ ] CI/CD: tests → build → push to GHCR → deploy to k3s
- [ ] RBAC, rate limiting, security headers, Trivy image scans, SAST
- [ ] Final documentation: screenshots, diagrams, install guides, demo video
