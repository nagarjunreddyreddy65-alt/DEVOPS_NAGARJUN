import os
import json
import time
from typing import Dict, Any, Optional

class AutonomousDecisionEngine:
    """
    Evaluates ML predictions and system constraints to select safe pipeline actions.
    Ensures safe fallbacks whenever confidence is low or failure probability is elevated.
    """

    def __init__(
        self,
        failure_threshold: Optional[float] = None,
        confidence_threshold: Optional[float] = None,
        runtime_threshold: Optional[float] = None
    ):
        self.failure_threshold = failure_threshold if failure_threshold is not None else float(os.environ.get("FAILURE_THRESHOLD", "0.70"))
        self.confidence_threshold = confidence_threshold if confidence_threshold is not None else float(os.environ.get("CONFIDENCE_THRESHOLD", "0.65"))
        self.runtime_threshold = runtime_threshold if runtime_threshold is not None else float(os.environ.get("RUNTIME_THRESHOLD", "0.60"))

    def evaluate_decision(
        self,
        failure_prob: float,
        model_confidence: float,
        predicted_runtime_sec: float,
        context_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes decision policy logic defined in IEEE guide:
        1. if failure_prob >= 0.80 -> FULL_PIPELINE (High risk of failure, require comprehensive diagnostics)
        2. elif model_confidence < 0.90 -> FULL_PIPELINE (Uncertain prediction, safe full fallback)
        3. elif predicted_runtime >= RUNTIME_THRESHOLD -> OPTIMIZE_TESTS (Safe and long runtime, optimize)
        4. else -> STANDARD_PIPELINE (Fast, low-risk build)
        """
        safety_fallback_triggered = False
        action = "STANDARD_PIPELINE"
        reason = "Predicted low failure risk, high confidence, and short runtime."

        if failure_prob >= self.failure_threshold:
            action = "FULL_PIPELINE"
            safety_fallback_triggered = True
            reason = f"Failure risk {failure_prob:.2f} >= threshold {self.failure_threshold:.2f}."
        elif model_confidence < self.confidence_threshold:
            action = "FULL_PIPELINE"
            safety_fallback_triggered = True
            reason = f"Model confidence {model_confidence:.2f} < threshold {self.confidence_threshold:.2f} (Uncertainty fallback)."
        elif predicted_runtime_sec >= self.runtime_threshold:
            action = "OPTIMIZE_TESTS"
            reason = f"Predicted runtime {predicted_runtime_sec:.1f}s >= threshold {self.runtime_threshold:.1f}s, safe to optimize."
        else:
            action = "STANDARD_PIPELINE"
            reason = f"Low risk, runtime {predicted_runtime_sec:.1f}s below optimization threshold."

        decision_output = {
            "action": action,
            "failure_probability": round(float(failure_prob), 4),
            "model_confidence": round(float(model_confidence), 4),
            "predicted_runtime_sec": round(float(predicted_runtime_sec), 2),
            "safety_fallback_triggered": safety_fallback_triggered,
            "reason": reason,
            "timestamp": time.time(),
            "context": context_metadata or {}
        }

        return decision_output

    def save_decision_artifact(self, decision: Dict[str, Any], filepath: str = "decision.json"):
        """Saves the operational decision as a JSON artifact for GitHub Actions workflow steps."""
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(decision, f, indent=2)

if __name__ == "__main__":
    engine = AutonomousDecisionEngine()
    print(engine.evaluate_decision(0.85, 0.95, 25.0))
    print(engine.evaluate_decision(0.10, 0.75, 25.0))
    print(engine.evaluate_decision(0.10, 0.95, 25.0))
    print(engine.evaluate_decision(0.10, 0.95, 12.0))
