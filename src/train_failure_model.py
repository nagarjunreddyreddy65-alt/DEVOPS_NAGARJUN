import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import joblib
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, roc_curve
from sklearn.model_selection import cross_val_score
from src.preprocess import DataPreprocessor

def train_and_compare_failure_models(csv_path: str = "data/raw/pipeline_runs.csv"):
    """
    Trains and benchmarks Logistic Regression, Decision Tree, and Random Forest for CI failure prediction.
    Selects the best model prioritizing Failure Recall for pipeline safety.
    """
    os.makedirs("models", exist_ok=True)
    os.makedirs("results/tables", exist_ok=True)

    preprocessor = DataPreprocessor()
    df = preprocessor.load_raw_data(csv_path)
    X_train, X_test, y_train, y_test, _, _ = preprocessor.prepare_datasets(df, test_ratio=0.20)

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=6, class_weight="balanced", random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=120, max_depth=8, class_weight="balanced", random_state=42)
    }

    results = []
    trained_models = {}

    print("--- Failure Prediction Model Training & Evaluation ---")
    for name, model in models.items():
        # Train
        model.fit(X_train, y_train)
        trained_models[name] = model

        # Predict
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred

        # Metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        auc = roc_auc_score(y_test, y_proba)
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="f1")

        results.append({
            "Model": name,
            "Accuracy": round(acc, 4),
            "Precision": round(prec, 4),
            "Recall": round(rec, 4),
            "F1": round(f1, 4),
            "ROC-AUC": round(auc, 4),
            "CV_F1_Mean": round(cv_scores.mean(), 4)
        })

        print(f"[{name}] Acc: {acc:.4f} | Prec: {prec:.4f} | Recall: {rec:.4f} | F1: {f1:.4f} | ROC-AUC: {auc:.4f}")

    metrics_df = pd.DataFrame(results)
    metrics_df.to_csv("results/tables/model_classification_metrics.csv", index=False)
    print("\nSaved failure classification metrics table to results/tables/model_classification_metrics.csv")

    # Safety prioritization: Choose model with best F1 and Recall
    # Random Forest typically achieves highest composite safety score
    best_name = max(results, key=lambda x: (x["Recall"] * 0.6 + x["F1"] * 0.4))["Model"]
    best_model = trained_models[best_name]
    print(f"\nBest safety-oriented model selected: {best_name}")

    joblib.dump(best_model, "models/failure_model.joblib")
    print("Saved best failure model to models/failure_model.joblib")

    return best_model, metrics_df

if __name__ == "__main__":
    train_and_compare_failure_models()
