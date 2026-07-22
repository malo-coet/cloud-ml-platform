import type { ReactNode } from "react";
import styles from "./States.module.css";

export function Loading({ label = "Loading…" }: { label?: string }) {
  return (
    <div className={styles.state}>
      <span className={styles.spinner} />
      <span className="muted">{label}</span>
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className={styles.state}>
      <p className={styles.error}>{message}</p>
      {onRetry && (
        <button className="btn btn-sm" onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  );
}

export function EmptyState({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className={styles.state}>
      <p className={styles.emptyTitle}>{title}</p>
      {children && <p className="muted">{children}</p>}
    </div>
  );
}
