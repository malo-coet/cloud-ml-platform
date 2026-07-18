# Tech choices

Short ADR-style records: what was chosen, over what, and why.

## FastAPI (over Flask / Django REST Framework)

Async-first (fits an event-publishing API), first-class Pydantic validation, automatic OpenAPI docs, and the de-facto standard for ML-adjacent APIs. Django brings an ORM/admin we don't need; Flask would require assembling all of this by hand.

## PostgreSQL (over MySQL / MongoDB)

Relational data (users → datasets → jobs) with strong consistency needs. Also serves as the MLflow backend store, so one database engine covers both. SQLAlchemy 2.x + Alembic give typed models and versioned migrations.

## Kafka in KRaft mode (over RabbitMQ / Redis Streams / direct calls)

The point of the platform is an **event-driven architecture**: the API publishes facts (`TrainingRequested`), workers react. Kafka adds replayable history, consumer groups, and industry relevance. KRaft mode removes ZooKeeper, so a single-node setup stays light enough for one VPS. RabbitMQ would work for queuing but lacks the log semantics; direct HTTP calls would couple the API to worker availability.

## MinIO (over cloud S3 / local filesystem)

Self-hosted constraint rules out AWS S3, but the **S3 API compatibility** means every tool (MLflow, boto3) works unchanged — and a later migration to real S3 is a config change. A pinned pre-2025-05 community release is used locally to keep the full web console.

## MLflow (over Weights & Biases / homemade tracking)

Self-hostable, open source, and covers the whole loop: experiment tracking, artifact storage, and a Model Registry whose stage transitions (`staging → production`) drive the automated deployment flow. W&B is SaaS-first; building tracking by hand teaches less than integrating the industry standard.

## k3s (over full kubeadm / Docker Swarm / plain Compose in prod)

Real Kubernetes API (manifests, Helm, RBAC all apply) in a single ~500 MB binary that fits a 4 GB VPS. Swarm is simpler but career-irrelevant; kubeadm wastes the VPS's resources on control-plane overhead. Traefik ships as k3s's default ingress controller, which matches our routing needs.

## DigitalOcean (over Hostinger)

Both work; DigitalOcean was picked because of an available $200 credit (≈ 8 months of a 2 vCPU / 4 GB droplet), better API/tooling (OpenTofu provider, doctl), and excellent k3s documentation. The infra code stays provider-agnostic: Ansible targets any Ubuntu host.

## OpenTofu + Ansible (over manual setup)

OpenTofu (open-source Terraform fork) declares the cloud resources: droplet, firewall, DNS records. Ansible configures the OS: hardening, Docker, k3s. Split follows the classic *provision vs configure* boundary and makes the whole VPS reproducible from scratch.

## React + Vite + TypeScript (over Next.js / CRA)

The frontend is a pure SPA dashboard behind an API — no SSR/SEO needs, so Next.js adds complexity without benefit. Vite gives instant HMR and a minimal build; TypeScript is non-negotiable for a portfolio project in 2026.

## uv (over pip / poetry)

Rust-based Python package manager: 10-100× faster installs (noticeable in Docker builds and CI), single tool for venvs + dependencies, standard `pyproject.toml`.

## Monorepo (over one repo per service)

Four services sharing one docker-compose, one CI pipeline, and atomic cross-service changes. At this team size (one person), polyrepo would only add friction; the directory layout keeps service boundaries explicit.

## GitHub Actions + GHCR (over GitLab CI / Docker Hub)

The repo lives on GitHub, so Actions is zero-setup and GHCR keeps images next to the code with the same permissions model. Free tier is more than enough.
