import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import joblib
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from src.preprocess import DataPreprocessor

def train_and_compare_runtime_models(csv_path: str = "data/raw/pipeline_runs.csv"):
    """
    Trains and benchmarks Linear Regression, Random Forest, and Gradient Boosting for pipeline duration prediction.
    Reports MAE, RMSE, and R2 regression metrics.
    """
    os.makedirs("models", exist_ok=True)
    os.makedirs("results/tables", exist_ok=True)

    preprocessor = DataPreprocessor()
    df = preprocessor.load_raw_data(csv_path)
    X_train, X_test, _, _, y_time_train, y_time_test = preprocessor.prepare_datasets(df, test_ratio=0.20)

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest Regressor": RandomForestRegressor(n_estimators=120, max_depth=8, random_state=42),
        "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=100, max_depth=4, random_state=42)
    }

    results = []
    trained_models = {}

    print("--- Runtime Prediction Model Training & Evaluation ---")
    for name, model in models.items():
        model.fit(X_train, y_time_train)
        trained_models[name] = model

        y_pred = model.predict(X_test)

        mae = mean_absolute_error(y_time_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_time_test, y_pred))
        r2 = r2_score(y_time_test, y_pred)

        results.append({
            "Model": name,
            "MAE": round(mae, 4),
            "RMSE": round(rmse, 4),
            "R2": round(r2, 4)
        })

        print(f"[{name}] MAE: {mae:.4f}s | RMSE: {rmse:.4f}s | R2: {r2:.4f}")

    metrics_df = pd.DataFrame(results)
    metrics_df.to_csv("results/tables/runtime_regression_metrics.csv", index=False)
    print("\nSaved runtime regression metrics table to results/tables/runtime_regression_metrics.csv")

    # Select model with highest R2 score
    best_name = max(results, key=lambda x: x["R2"])["Model"]
    best_model = trained_models[best_name]
    print(f"\nBest regression model selected: {best_name}")

    joblib.dump(best_model, "models/runtime_model.joblib")
    print("Saved best runtime model to models/runtime_model.joblib")

    return best_model, metrics_df

if __name__ == "__main__":
    train_and_compare_runtime_models()
