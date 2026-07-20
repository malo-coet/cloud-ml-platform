import pandas as pd
import pytest

from trainer.pipeline import train_dataframe


def toy_dataframe() -> pd.DataFrame:
    """Three well-separated classes, 30 rows each — trivially learnable."""
    rows = []
    for label, offset in (("a", 0.0), ("b", 5.0), ("c", 10.0)):
        for i in range(30):
            rows.append(
                {
                    "x1": offset + (i % 10) * 0.1,
                    "x2": offset + (i % 7) * 0.2,
                    "label": label,
                }
            )
    return pd.DataFrame(rows)


@pytest.mark.parametrize("model_type", ["logistic_regression", "random_forest"])
def test_training_produces_valid_metrics(model_type: str) -> None:
    result = train_dataframe(toy_dataframe(), model_type=model_type)

    assert set(result.metrics) == {"accuracy", "f1_macro", "precision_macro", "recall_macro"}
    assert all(0.0 <= value <= 1.0 for value in result.metrics.values())
    # Separable data: any sane model should be near-perfect
    assert result.metrics["accuracy"] > 0.9
    assert result.params["target_column"] == "label"
    assert result.params["n_classes"] == "3"


def test_target_defaults_to_last_column() -> None:
    result = train_dataframe(toy_dataframe(), model_type="logistic_regression")
    assert result.params["target_column"] == "label"


def test_explicit_target_column() -> None:
    df = toy_dataframe()[["label", "x1", "x2"]]  # target first, not last
    result = train_dataframe(df, model_type="logistic_regression", target_column="label")
    assert result.metrics["accuracy"] > 0.9


def test_missing_target_column_raises() -> None:
    with pytest.raises(ValueError, match="not found"):
        train_dataframe(toy_dataframe(), "logistic_regression", target_column="nope")


def test_single_class_target_raises() -> None:
    df = toy_dataframe()
    df["label"] = "only-one"
    with pytest.raises(ValueError, match="2 distinct classes"):
        train_dataframe(df, "logistic_regression")


def test_non_numeric_features_raise() -> None:
    df = pd.DataFrame({"text": ["a", "b", "c", "d"], "label": ["x", "y", "x", "y"]})
    with pytest.raises(ValueError, match="numeric"):
        train_dataframe(df, "logistic_regression", target_column="label")


def test_unknown_model_type_raises() -> None:
    with pytest.raises(ValueError, match="Unknown model type"):
        train_dataframe(toy_dataframe(), "quantum_boost")
