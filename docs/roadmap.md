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

## Sprint 3 — Datasets

> Phase 4: dataset upload and storage.

- [ ] `POST /datasets` upload (CSV, images, ZIP, Parquet) streamed to MinIO
- [ ] Metadata in PostgreSQL: owner, date, version, size, type
- [ ] `GET /datasets` listing with pagination
- [ ] Dataset versioning

## Sprint 4 — Training & MLflow

> Phases 5 & 7: training microservice, experiment tracking.

- [ ] Training service skeleton (standalone worker)
- [ ] Iris pipeline: fetch → preprocess → train → metrics → MLflow
- [ ] MNIST, then CIFAR-10 (PyTorch)
- [ ] Model Registry usage (versions, stages)
- [ ] `POST /train`, `GET /experiments`, `GET /models` endpoints

## Sprint 5 — Event-driven architecture

> Phase 6: Kafka everywhere.

- [ ] Kafka producer in the backend (`TrainingRequested`, `DeployRequested`, …)
- [ ] Kafka consumer in the training service
- [ ] Job status lifecycle (`pending → running → completed/failed`)
- [ ] Dead-letter handling and retries

## Sprint 6 — Frontend

> Phase 17: dashboard.

- [ ] Login page + JWT session handling
- [ ] Datasets, Experiments, Models, Deployments pages
- [ ] Metric charts (accuracy, loss, precision, recall)
- [ ] Training history

## Sprint 7 — VPS & Kubernetes

> Phases 8–12: production infrastructure.

- [ ] DigitalOcean droplet provisioning (OpenTofu + Ansible)
- [ ] Hardening: SSH keys, firewall, Fail2Ban, unattended upgrades
- [ ] k3s + Traefik + cert-manager (Let's Encrypt)
- [ ] Kubernetes manifests for every component
- [ ] DNS sub-domains under `mlops.mcoet.com`
- [ ] Deployment service: model → Docker image → k8s Deployment → prediction endpoint

## Sprint 8 — Observability, security, CI/CD

> Phases 13–16 & 18: production quality.

- [ ] Prometheus + Grafana + Node Exporter + kube-state-metrics
- [ ] Loki + Promtail centralized logging
- [ ] Structured application logging + error handling
- [ ] CI/CD: tests → build → push to GHCR → deploy to k3s
- [ ] RBAC, rate limiting, security headers, Trivy image scans, SAST
- [ ] Final documentation: screenshots, diagrams, install guides, demo video
