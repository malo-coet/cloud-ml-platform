import type { JobStatus } from "../api/types";
import styles from "./StatusBadge.module.css";

const LABELS: Record<JobStatus, string> = {
  queued: "Queued",
  running: "Running",
  completed: "Completed",
  failed: "Failed",
};

export function StatusBadge({ status }: { status: JobStatus }) {
  return (
    <span className={`${styles.badge} ${styles[status]}`}>
      <span className={styles.dot} />
      {LABELS[status]}
    </span>
  );
}
