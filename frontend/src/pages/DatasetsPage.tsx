import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ApiError, api } from "../api/client";
import { useApi } from "../api/useApi";
import type { Dataset, ModelType, TrainingJob } from "../api/types";
import { Modal } from "../components/Modal";
import { PageHeader } from "../components/PageHeader";
import { EmptyState, ErrorState, Loading } from "../components/States";
import { formatBytes, formatDate } from "../lib/format";
import styles from "./DatasetsPage.module.css";

export function DatasetsPage() {
  const { data, loading, error, reload } = useApi(() => api.get<Dataset[]>("/datasets"));
  const fileInput = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [trainTarget, setTrainTarget] = useState<Dataset | null>(null);

  async function handleUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = ""; // allow re-selecting the same file
    if (!file) return;
    setNotice(null);
    setUploading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      await api.postForm<Dataset>("/datasets", form);
      reload();
    } catch (err) {
      setNotice(err instanceof ApiError ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  async function handleDownload(dataset: Dataset) {
    try {
      const { url } = await api.get<{ url: string }>(`/datasets/${dataset.id}/download`);
      window.open(url, "_blank");
    } catch (err) {
      setNotice(err instanceof ApiError ? err.message : "Download failed");
    }
  }

  async function handleDelete(dataset: Dataset) {
    if (!confirm(`Delete "${dataset.name}" v${dataset.version}?`)) return;
    try {
      await api.del(`/datasets/${dataset.id}`);
      reload();
    } catch (err) {
      setNotice(err instanceof ApiError ? err.message : "Delete failed");
    }
  }

  return (
    <>
      <PageHeader
        title="Datasets"
        subtitle="Upload data, then train a model on any CSV in one click."
        actions={
          <>
            <input
              ref={fileInput}
              type="file"
              accept=".csv,.parquet,.zip,.png,.jpg,.jpeg"
              hidden
              onChange={handleUpload}
            />
            <button
              className="btn btn-primary"
              onClick={() => fileInput.current?.click()}
              disabled={uploading}
            >
              {uploading ? "Uploading…" : "Upload dataset"}
            </button>
          </>
        }
      />

      {notice && <p className={styles.notice}>{notice}</p>}

      {loading && <Loading />}
      {error && <ErrorState message={error} onRetry={reload} />}
      {data && data.length === 0 && (
        <EmptyState title="No datasets yet">
          Upload a CSV file to get started — re-uploading the same name creates a new version.
        </EmptyState>
      )}

      {data && data.length > 0 && (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Version</th>
                <th>Format</th>
                <th>Size</th>
                <th>Uploaded</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {data.map((dataset) => (
                <tr key={dataset.id}>
                  <td className={styles.name}>{dataset.name}</td>
                  <td>v{dataset.version}</td>
                  <td>
                    <span className="tag">{dataset.format}</span>
                  </td>
                  <td>{formatBytes(dataset.size_bytes)}</td>
                  <td className="muted">{formatDate(dataset.created_at)}</td>
                  <td>
                    <div className={styles.actions}>
                      {dataset.format === "csv" && (
                        <button
                          className="btn btn-sm btn-primary"
                          onClick={() => setTrainTarget(dataset)}
                        >
                          Train
                        </button>
                      )}
                      <button className="btn btn-sm" onClick={() => handleDownload(dataset)}>
                        Download
                      </button>
                      <button
                        className="btn btn-sm btn-danger"
                        onClick={() => handleDelete(dataset)}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {trainTarget && (
        <TrainDialog dataset={trainTarget} onClose={() => setTrainTarget(null)} />
      )}
    </>
  );
}

function TrainDialog({ dataset, onClose }: { dataset: Dataset; onClose: () => void }) {
  const navigate = useNavigate();
  const [modelType, setModelType] = useState<ModelType>("logistic_regression");
  const [targetColumn, setTargetColumn] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await api.postJson<TrainingJob>("/train", {
        dataset_id: dataset.id,
        model_type: modelType,
        target_column: targetColumn.trim() || null,
        hyperparameters: {},
      });
      navigate("/experiments");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not start training");
      setSubmitting(false);
    }
  }

  return (
    <Modal title={`Train on ${dataset.name}`} onClose={onClose}>
      <form className={styles.form} onSubmit={handleSubmit}>
        <div>
          <label className="field-label" htmlFor="model">
            Model
          </label>
          <select
            id="model"
            className="select"
            value={modelType}
            onChange={(e) => setModelType(e.target.value as ModelType)}
          >
            <option value="logistic_regression">Logistic regression</option>
            <option value="random_forest">Random forest</option>
          </select>
        </div>

        <div>
          <label className="field-label" htmlFor="target">
            Target column <span className="muted">(optional — defaults to last column)</span>
          </label>
          <input
            id="target"
            className="input"
            placeholder="e.g. species"
            value={targetColumn}
            onChange={(e) => setTargetColumn(e.target.value)}
          />
        </div>

        {error && <p className={styles.notice}>{error}</p>}

        <div className={styles.formActions}>
          <button type="button" className="btn" onClick={onClose}>
            Cancel
          </button>
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? "Starting…" : "Start training"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
