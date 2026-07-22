export type UserRole = "admin" | "user";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export type DatasetFormat = "csv" | "parquet" | "zip" | "image";

export interface Dataset {
  id: string;
  owner_id: string;
  name: string;
  filename: string;
  format: DatasetFormat;
  size_bytes: number;
  version: number;
  created_at: string;
}

export type ModelType = "logistic_regression" | "random_forest";
export type JobStatus = "queued" | "running" | "completed" | "failed";

export interface TrainingJob {
  id: string;
  dataset_id: string;
  owner_id: string;
  model_type: ModelType;
  target_column: string | null;
  hyperparameters: Record<string, unknown>;
  status: JobStatus;
  error: string | null;
  mlflow_run_id: string | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}

export interface Experiment {
  run_id: string;
  run_name: string | null;
  experiment: string | null;
  status: string;
  start_time: number | null;
  end_time: number | null;
  metrics: Record<string, number>;
  params: Record<string, string>;
}

export interface ModelVersion {
  version: string;
  stage: string | null;
  run_id: string | null;
  status: string | null;
}

export interface RegisteredModel {
  name: string;
  created_at: number | null;
  last_updated_at: number | null;
  latest_versions: ModelVersion[];
}
