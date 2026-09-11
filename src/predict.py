import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import argparse
import joblib
import numpy as np
from src.collect_features import FeatureCollector
from src.preprocess import DataPreprocessor, FEATURE_COLUMNS
from src.test_selector import ChangeAwareTestSelector
from src.decision_engine import AutonomousDecisionEngine

def run_prediction_pipeline(
    changed_files=None,
    lines_added=0,
    lines_deleted=0,
    commit_id=None,
    output_file="decision.json",
    export_github_output=True
):
    """
    Executes the real-time AI decision pipeline for CI/CD runs.
    Extracts features, evaluates models, runs test selector, and outputs decision.json.
    """
    collector = FeatureCollector()
    feature_dict = collector.collect_features_vector(
        changed_files=changed_files,
        lines_added=lines_added,
        lines_deleted=lines_deleted,
        commit_id=commit_id
    )

    preprocessor = DataPreprocessor()
    X_vec = preprocessor.transform_single(feature_dict)

    # Load trained models
    failure_model_path = "models/failure_model.joblib"
    runtime_model_path = "models/runtime_model.joblib"

    if os.path.exists(failure_model_path):
        failure_model = joblib.load(failure_model_path)
        if hasattr(failure_model, "predict_proba"):
            probs = failure_model.predict_proba(X_vec)[0]
            failure_prob = float(probs[1]) if len(probs) > 1 else 0.0
            # Confidence is the certainty of the decision (max class probability)
            model_confidence = float(np.max(probs))
        else:
            failure_prob = float(failure_model.predict(X_vec)[0])
            model_confidence = 0.95
    else:
        # Fallback if model not yet trained
        failure_prob = 0.15
        model_confidence = 0.92

    if os.path.exists(runtime_model_path):
        runtime_model = joblib.load(runtime_model_path)
        predicted_runtime = float(runtime_model.predict(X_vec)[0])
    else:
        predicted_runtime = 20.0

    # Evaluate decision logic
    engine = AutonomousDecisionEngine()
    decision = engine.evaluate_decision(
        failure_prob=failure_prob,
        model_confidence=model_confidence,
        predicted_runtime_sec=predicted_runtime,
        context_metadata={"commit_id": feature_dict["commit_id"], "files_changed": feature_dict["files_changed"]}
    )

    # Perform change-aware test selection
    selector = ChangeAwareTestSelector()
    force_full = (decision["action"] == "FULL_PIPELINE" or decision["action"] == "STANDARD_PIPELINE")
    test_selection = selector.select_tests_for_changes(
        changed_files=feature_dict["changed_files"],
        force_full_suite=force_full
    )

    # Enrich decision payload
    decision["selected_tests"] = test_selection["selected_tests"]
    decision["is_full_suite"] = test_selection["is_full_suite"]
    decision["test_selection_reason"] = test_selection["reason"]
    decision["features"] = {k: v for k, v in feature_dict.items() if k != "changed_files"}

    # Save artifact
    engine.save_decision_artifact(decision, output_file)
    print(f"Decision written to {output_file}:")
    print(f"  Action: {decision['action']}")
    print(f"  Failure Probability: {decision['failure_probability']:.4f}")
    print(f"  Confidence: {decision['model_confidence']:.4f}")
    print(f"  Predicted Runtime: {decision['predicted_runtime_sec']:.2f}s")
    print(f"  Selected Tests: {decision['selected_tests']}")

    # Export to GitHub Actions GITHUB_OUTPUT if present
    github_output_path = os.environ.get("GITHUB_OUTPUT")
    if export_github_output and github_output_path:
        with open(github_output_path, "a", encoding="utf-8") as gh_out:
            gh_out.write(f"action={decision['action']}\n")
            gh_out.write(f"selected_tests={' '.join(decision['selected_tests'])}\n")
            gh_out.write(f"is_full_suite={str(decision['is_full_suite']).lower()}\n")

    return decision

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous CI/CD Prediction CLI")
    parser.add_argument("--changed-files", nargs="*", default=None, help="List of changed file paths")
    parser.add_argument("--lines-added", type=int, default=0, help="Number of added lines")
    parser.add_argument("--lines-deleted", type=int, default=0, help="Number of deleted lines")
    parser.add_argument("--commit-id", type=str, default=None, help="Git commit SHA")
    parser.add_argument("--output", type=str, default="decision.json", help="Path to save decision.json")

    args = parser.parse_args()
    run_prediction_pipeline(
        changed_files=args.changed_files,
        lines_added=args.lines_added,
        lines_deleted=args.lines_deleted,
        commit_id=args.commit_id,
        output_file=args.output
    )
