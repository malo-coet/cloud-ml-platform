import { api } from "../api/client";
import { useApi } from "../api/useApi";
import type { RegisteredModel } from "../api/types";
import { PageHeader } from "../components/PageHeader";
import { EmptyState, ErrorState, Loading } from "../components/States";
import { formatEpoch } from "../lib/format";
import styles from "./ModelsPage.module.css";

export function ModelsPage() {
  const { data, loading, error, reload } = useApi(() =>
    api.get<RegisteredModel[]>("/models"),
  );

  return (
    <>
      <PageHeader
        title="Models"
        subtitle="Models registered in the MLflow Model Registry — promote a version to deploy it."
      />

      {loading && <Loading />}
      {error && <ErrorState message={error} onRetry={reload} />}
      {data && data.length === 0 && (
        <EmptyState title="No registered models yet">
          Each successful training run registers a model version automatically.
        </EmptyState>
      )}

      {data && data.length > 0 && (
        <div className={styles.grid}>
          {data.map((model) => (
            <div key={model.name} className={`card ${styles.card}`}>
              <div className={styles.cardHead}>
                <h3 className={styles.name}>{model.name}</h3>
                <span className="muted">Updated {formatEpoch(model.last_updated_at)}</span>
              </div>
              <div className={styles.versions}>
                {model.latest_versions.length === 0 && (
                  <span className="muted">No versions</span>
                )}
                {model.latest_versions.map((version) => (
                  <div key={version.version} className={styles.version}>
                    <span className={styles.versionTag}>v{version.version}</span>
                    <span className="tag">{version.stage ?? "None"}</span>
                    {version.run_id && (
                      <span className="mono muted">{version.run_id.slice(0, 10)}…</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
