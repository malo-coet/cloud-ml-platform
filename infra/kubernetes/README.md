# Kubernetes manifests

Workloads deployed on the k3s cluster, in the `mlops` namespace.

| File | Resources |
|---|---|
| `namespace.yaml` | The `mlops` namespace |
| `postgres.yaml` | StatefulSet + PVC + Service, with the MLflow database created on first boot |
| `redis.yaml` | Deployment + Service |
| `minio.yaml` | StatefulSet + PVC + Service (S3 API on 9000, console on 9001) |
| `kafka.yaml` | StatefulSet + PVC + Service (single-node KRaft, capped JVM heap) |
| `mlflow.yaml` | Deployment + Service, with an init container that creates the buckets |
| `backend.yaml` | Deployment + Service, migrations run in an init container |
| `frontend.yaml` | Deployment + Service (nginx serving the built SPA) |
| `training-service.yaml` | Deployment (raise `replicas` to scale — Kafka splits the work) |
| `ingress.yaml` | Traefik Ingress + TLS for every public hostname |
| `traefik-config.yaml` | Cluster-wide HTTP → HTTPS redirect |

```bash
kubectl apply -f namespace.yaml
kubectl apply -f secrets.yaml     # from secrets.example.yaml — never committed
kubectl apply -k .
```

Secrets are intentionally excluded from `kustomization.yaml` so real credentials
are always applied deliberately.

Full walkthrough: [docs/deployment.md](../../docs/deployment.md).
