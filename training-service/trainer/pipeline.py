"""Pure training pipeline: dataframe in, fitted model + metrics out.

No I/O here (no database, no MLflow, no S3) so it stays trivially testable.
"""

from dataclasses import dataclass

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split


@dataclass
class TrainResult:
    model: object
    metrics: dict[str, float]
    params: dict[str, str]


def _build_model(model_type: str, hp: dict):
    if model_type == "logistic_regression":
        return LogisticRegression(
            max_iter=int(hp.get("max_iter", 1000)),
            C=float(hp.get("C", 1.0)),
        )
    if model_type == "random_forest":
        max_depth = hp.get("max_depth")
        return RandomForestClassifier(
            n_estimators=int(hp.get("n_estimators", 100)),
            max_depth=int(max_depth) if max_depth is not None else None,
            random_state=int(hp.get("random_state", 42)),
        )
    raise ValueError(f"Unknown model type '{model_type}'")


def train_dataframe(
    df: pd.DataFrame,
    model_type: str,
    target_column: str | None = None,
    hyperparameters: dict | None = None,
) -> TrainResult:
    """Classification pipeline: preprocess, split, fit, evaluate."""
    hp = hyperparameters or {}
    target = target_column or df.columns[-1]
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found in dataset")

    df = df.dropna()
    y = df[target]
    features = df.drop(columns=[target]).select_dtypes(include="number")
    if features.empty:
        raise ValueError("Dataset has no numeric feature columns")
    if y.nunique() < 2:
        raise ValueError("Target column needs at least 2 distinct classes")

    test_size = float(hp.get("test_size", 0.2))
    random_state = int(hp.get("random_state", 42))
    x_train, x_test, y_train, y_test = train_test_split(
        features, y, test_size=test_size, random_state=random_state, stratify=y
    )

    model = _build_model(model_type, hp)
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "f1_macro": f1_score(y_test, y_pred, average="macro", zero_division=0),
        "precision_macro": precision_score(y_test, y_pred, average="macro", zero_division=0),
        "recall_macro": recall_score(y_test, y_pred, average="macro", zero_division=0),
    }
    params = {
        "model_type": model_type,
        "target_column": target,
        "test_size": str(test_size),
        "random_state": str(random_state),
        "n_rows": str(len(df)),
        "n_features": str(features.shape[1]),
        "n_classes": str(y.nunique()),
        **{f"model.{key}": str(value) for key, value in model.get_params().items()},
    }
    return TrainResult(model=model, metrics=metrics, params=params)
