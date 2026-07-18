# Training Service

Python worker that consumes `TrainingRequested` events from Kafka, then:

1. downloads the dataset from MinIO,
2. preprocesses it,
3. trains the model (scikit-learn or PyTorch),
4. logs params, metrics and the model to MLflow,
5. publishes a `TrainingCompleted` event.

**Status: placeholder — implemented in Sprints 4–5** (see [docs/roadmap.md](../docs/roadmap.md)). Planned model progression: Iris → MNIST → CIFAR-10 → a real-world dataset.
