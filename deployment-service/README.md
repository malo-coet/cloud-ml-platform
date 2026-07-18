# Deployment Service

Python worker that consumes `DeployRequested` events from Kafka, then:

1. pulls the model from the MLflow Model Registry,
2. builds a serving Docker image,
3. creates the Kubernetes Deployment and Service,
4. exposes the prediction endpoint through Traefik,
5. publishes a `ModelDeployed` event.

**Status: placeholder — implemented in Sprint 7** (see [docs/roadmap.md](../docs/roadmap.md)).
