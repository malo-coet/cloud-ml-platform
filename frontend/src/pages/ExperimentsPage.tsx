import { useEffect } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../api/client";
import { useApi } from "../api/useApi";
import type { Experiment, TrainingJob } from "../api/types";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { EmptyState, ErrorState, Loading } from "../components/States";
import { formatDate, formatDuration, formatMetric } from "../lib/format";
import styles from "./ExperimentsPage.module.css";

const ACTIVE = new Set(["queued", "running"]);

export function ExperimentsPage() {
  const jobs = useApi(() => api.get<TrainingJob[]>("/train"));
  const experiments = useApi(() => api.get<Experiment[]>("/experiments"));

  // Poll while any job is still running so the lifecycle updates live.
  const hasActive = jobs.data?.some((job) => ACTIVE.has(job.status)) ?? false;
  useEffect(() => {
    if (!hasActive) return;
    const timer = setInterval(() => {
      jobs.reload();
      experiments.reload();
    }, 3000);
    return () => clearInterval(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hasActive]);

  return (
    <>
      <PageHeader
        title="Experiments"
        subtitle="Training jobs and their MLflow runs. This view refreshes while jobs are running."
      />

      <section className={styles.section}>
        <h2 className={styles.heading}>Training jobs</h2>
        {jobs.loading && <Loading />}
        {jobs.error && <ErrorState message={jobs.error} onRetry={jobs.reload} />}
        {jobs.data && jobs.data.length === 0 && (
          <EmptyState title="No training jobs yet">
            Start one from the Datasets page.
          </EmptyState>
        )}
        {jobs.data && jobs.data.length > 0 && (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Model</th>
                  <th>Target</th>
                  <th>Started</th>
                  <th>Duration</th>
                  <th>Result</th>
                </tr>
              </thead>
              <tbody>
                {jobs.data.map((job) => (
                  <tr key={job.id}>
                    <td>
                      <StatusBadge status={job.status} />
                    </td>
                    <td>
                      <span className="tag">{job.model_type}</span>
                    </td>
                    <td className="muted">{job.target_column ?? "auto"}</td>
                    <td className="muted">{formatDate(job.started_at)}</td>
                    <td className="muted">{formatDuration(job.started_at, job.finished_at)}</td>
                    <td>
                      {job.status === "failed" ? (
                        <span className={styles.failure} title={job.error ?? ""}>
                          {job.error}
                        </span>
                      ) : job.mlflow_run_id ? (
                        <span className="mono muted">{job.mlflow_run_id.slice(0, 10)}…</span>
                      ) : (
                        "—"
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className={styles.section}>
        <h2 className={styles.heading}>MLflow runs</h2>
        {experiments.loading && <Loading />}
        {experiments.error && (
          <ErrorState message={experiments.error} onRetry={experiments.reload} />
        )}
        {experiments.data && experiments.data.length === 0 && (
          <EmptyState title="No runs recorded yet">
            Completed trainings will appear here with their metrics.
          </EmptyState>
        )}
        {experiments.data && experiments.data.length > 0 && (
          <>
            <AccuracyChart runs={experiments.data} />
            <RunsTable runs={experiments.data} />
          </>
        )}
      </section>
    </>
  );
}

function AccuracyChart({ runs }: { runs: Experiment[] }) {
  // Key each bar by its unique run id; run names (model-version) can repeat,
  // which Recharts would otherwise use as a colliding category key.
  const data = runs
    .filter((run) => typeof run.metrics.accuracy === "number")
    .slice(0, 12)
    .reverse()
    .map((run) => ({
      runId: run.run_id,
      label: run.run_name ?? run.run_id.slice(0, 6),
      accuracy: Number(run.metrics.accuracy.toFixed(4)),
    }));

  if (data.length === 0) return null;

  const labelFor = (runId: string) => data.find((d) => d.runId === runId)?.label ?? runId;

  return (
    <div className={`card ${styles.chartCard}`}>
      <div className={styles.chartTitle}>Accuracy by run</div>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} margin={{ top: 8, right: 8, bottom: 8, left: -18 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f1" vertical={false} />
          <XAxis
            dataKey="runId"
            tickFormatter={labelFor}
            tick={{ fontSize: 11, fill: "#a1a1aa" }}
            tickLine={false}
            axisLine={{ stroke: "#ececee" }}
          />
          <YAxis
            domain={[0, 1]}
            tick={{ fontSize: 11, fill: "#a1a1aa" }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            labelFormatter={(value) => labelFor(String(value))}
            cursor={{ fill: "rgba(79, 70, 229, 0.05)" }}
            contentStyle={{
              borderRadius: 8,
              border: "1px solid #ececee",
              fontSize: 12,
              boxShadow: "0 1px 3px rgba(24,24,27,0.08)",
            }}
          />
          <Bar dataKey="accuracy" fill="#4f46e5" radius={[4, 4, 0, 0]} maxBarSize={44} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

const METRIC_KEYS = ["accuracy", "f1_macro", "precision_macro", "recall_macro"] as const;
const METRIC_LABELS = ["Accuracy", "F1", "Precision", "Recall"];

function RunsTable({ runs }: { runs: Experiment[] }) {
  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            <th>Run</th>
            <th>Experiment</th>
            {METRIC_LABELS.map((label) => (
              <th key={label}>{label}</th>
            ))}
            <th>Finished</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <tr key={run.run_id}>
              <td className={styles.runName}>{run.run_name ?? run.run_id.slice(0, 8)}</td>
              <td className="muted">{run.experiment ?? "—"}</td>
              {METRIC_KEYS.map((key) => (
                <td key={key} className="mono">
                  {typeof run.metrics[key] === "number" ? formatMetric(run.metrics[key]) : "—"}
                </td>
              ))}
              <td className="muted">
                {run.end_time ? formatDate(new Date(run.end_time).toISOString()) : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
