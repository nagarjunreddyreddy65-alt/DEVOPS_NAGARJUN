import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Dict, Any

FEATURE_COLUMNS = [
    "files_changed",
    "lines_added",
    "lines_deleted",
    "test_count",
    "previous_runtime_sec",
    "previous_failure",
    "cpu_usage_pct",
    "memory_usage_mb"
]

class DataPreprocessor:
    """Preprocesses CI/CD pipeline telemetry data, preventing temporal data leakage."""

    def __init__(self, scaler_path: str = "models/preprocessor.joblib"):
        self.scaler_path = scaler_path
        self.scaler = StandardScaler()
        self.is_fitted = False

    def load_raw_data(self, csv_path: str = "data/raw/pipeline_runs.csv") -> pd.DataFrame:
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Raw dataset file not found at {csv_path}")
        df = pd.read_csv(csv_path)
        return df

    def prepare_datasets(
        self,
        df: pd.DataFrame,
        test_ratio: float = 0.20,
        save_processed: bool = True
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Splits dataset chronologically (temporal order) to prevent future-data leakage.
        Fits scaler strictly on the training partition.
        Returns:
            X_train, X_test, y_fail_train, y_fail_test, y_time_train, y_time_test
        """
        # Ensure data is chronologically sorted
        if "timestamp" in df.columns:
            df = df.sort_values(by="timestamp").reset_index(drop=True)

        if "total_runtime_sec" not in df.columns:
            df["total_runtime_sec"] = df["build_time_sec"] + df["test_time_sec"]

        # Drop missing values if any
        df = df.dropna(subset=FEATURE_COLUMNS + ["result", "total_runtime_sec"]).copy()

        split_idx = int(len(df) * (1 - test_ratio))
        train_df = df.iloc[:split_idx].copy()
        test_df = df.iloc[split_idx:].copy()

        X_train_raw = train_df[FEATURE_COLUMNS].values
        X_test_raw = test_df[FEATURE_COLUMNS].values

        # Fit scaler ONLY on train data
        X_train = self.scaler.fit_transform(X_train_raw)
        X_test = self.scaler.transform(X_test_raw)
        self.is_fitted = True

        y_fail_train = train_df["result"].values.astype(int)
        y_fail_test = test_df["result"].values.astype(int)

        y_time_train = train_df["total_runtime_sec"].values.astype(float)
        y_time_test = test_df["total_runtime_sec"].values.astype(float)

        if save_processed:
            os.makedirs("data/processed", exist_ok=True)
            os.makedirs("models", exist_ok=True)

            train_export = pd.DataFrame(X_train, columns=FEATURE_COLUMNS)
            train_export["result"] = y_fail_train
            train_export["total_runtime_sec"] = y_time_train
            train_export.to_csv("data/processed/train_features.csv", index=False)

            test_export = pd.DataFrame(X_test, columns=FEATURE_COLUMNS)
            test_export["result"] = y_fail_test
            test_export["total_runtime_sec"] = y_time_test
            test_export.to_csv("data/processed/test_features.csv", index=False)

            joblib.dump(self.scaler, self.scaler_path)

        return X_train, X_test, y_fail_train, y_fail_test, y_time_train, y_time_test

    def transform_single(self, feature_dict: Dict[str, Any]) -> np.ndarray:
        """Transforms a single observation dictionary into a scaled vector for inference."""
        if not self.is_fitted:
            if os.path.exists(self.scaler_path):
                self.scaler = joblib.load(self.scaler_path)
                self.is_fitted = True
            else:
                # If scaler file not yet saved, use unscaled values
                vals = [float(feature_dict.get(col, 0.0)) for col in FEATURE_COLUMNS]
                return np.array(vals).reshape(1, -1)

        raw_vector = np.array([[float(feature_dict.get(col, 0.0)) for col in FEATURE_COLUMNS]])
        return self.scaler.transform(raw_vector)

if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    print("Preprocessor module loaded.")
