import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, mean_absolute_error, mean_squared_error, r2_score
)
from src.preprocess import DataPreprocessor

def evaluate_all_models(
    failure_model_path: str = "models/failure_model.joblib",
    runtime_model_path: str = "models/runtime_model.joblib"
):
    """
    Evaluates saved models against the holdout evaluation partition.
    Prints full scientific report and exports evaluation results.
    """
    preprocessor = DataPreprocessor()
    df = preprocessor.load_raw_data("data/raw/pipeline_runs.csv")
    X_train, X_test, y_fail_train, y_fail_test, y_time_train, y_time_test = preprocessor.prepare_datasets(df, test_ratio=0.20, save_processed=False)

    print("===============================================================")
    print("      AUTONOMOUS DEVOPS: SCIENTIFIC MODEL EVALUATION REPORT   ")
    print("===============================================================")

    # 1. Evaluate Failure Classifier
    if os.path.exists(failure_model_path):
        failure_model = joblib.load(failure_model_path)
        y_fail_pred = failure_model.predict(X_test)
        y_fail_proba = failure_model.predict_proba(X_test)[:, 1] if hasattr(failure_model, "predict_proba") else y_fail_pred

        acc = accuracy_score(y_fail_test, y_fail_pred)
        prec = precision_score(y_fail_test, y_fail_pred, zero_division=0)
        rec = recall_score(y_fail_test, y_fail_pred, zero_division=0)
        f1 = f1_score(y_fail_test, y_fail_pred, zero_division=0)
        auc = roc_auc_score(y_fail_test, y_fail_proba)

        print("\n[CLASSIFICATION: CI Failure Prediction]")
        print(f"  Holdout Samples:   {len(y_fail_test)}")
        print(f"  Accuracy:          {acc * 100:.2f}%")
        print(f"  Precision:         {prec:.4f}")
        print(f"  Recall (Safety):   {rec:.4f}")
        print(f"  F1-Score:          {f1:.4f}")
        print(f"  ROC-AUC:           {auc:.4f}")
    else:
        print("\n[WARNING] Failure model not found.")

    # 2. Evaluate Runtime Regressor
    if os.path.exists(runtime_model_path):
        runtime_model = joblib.load(runtime_model_path)
        y_time_pred = runtime_model.predict(X_test)

        mae = mean_absolute_error(y_time_test, y_time_pred)
        rmse = np.sqrt(mean_squared_error(y_time_test, y_time_pred))
        r2 = r2_score(y_time_test, y_time_pred)

        print("\n[REGRESSION: Pipeline Runtime Prediction]")
        print(f"  Holdout Samples:   {len(y_time_test)}")
        print(f"  MAE:               {mae:.3f} seconds")
        print(f"  RMSE:              {rmse:.3f} seconds")
        print(f"  R^2 Score:         {r2:.4f}")
    else:
        print("\n[WARNING] Runtime model not found.")

    print("===============================================================\n")

if __name__ == "__main__":
    evaluate_all_models()
