import pytest
import os
import numpy as np
from src.collect_features import FeatureCollector
from src.test_selector import ChangeAwareTestSelector
from src.decision_engine import AutonomousDecisionEngine

def test_change_aware_selector_single_module():
    selector = ChangeAwareTestSelector()
    res = selector.select_tests_for_changes(["app/authentication/auth_service.py"])
    assert res["is_full_suite"] is False
    assert "tests/test_auth.py" in res["selected_tests"]
    assert "authentication" in res["matched_modules"]

def test_change_aware_selector_database_fallback():
    selector = ChangeAwareTestSelector()
    # Modifying database triggers broader/full test selection
    res = selector.select_tests_for_changes(["app/database/connection.py"])
    assert res["is_full_suite"] is True
    assert "tests/test_database.py" in res["selected_tests"]
    assert "tests/test_auth.py" in res["selected_tests"]

def test_change_aware_selector_infrastructure_fallback():
    selector = ChangeAwareTestSelector()
    res = selector.select_tests_for_changes(["requirements.txt"])
    assert res["is_full_suite"] is True
    assert "safety fallback" in res["reason"].lower()

def test_decision_engine_high_risk_fallback():
    engine = AutonomousDecisionEngine(failure_threshold=0.80, confidence_threshold=0.90)
    decision = engine.evaluate_decision(failure_prob=0.85, model_confidence=0.95, predicted_runtime_sec=25.0)
    assert decision["action"] == "FULL_PIPELINE"
    assert decision["safety_fallback_triggered"] is True

def test_decision_engine_low_confidence_fallback():
    engine = AutonomousDecisionEngine(failure_threshold=0.80, confidence_threshold=0.90)
    decision = engine.evaluate_decision(failure_prob=0.20, model_confidence=0.75, predicted_runtime_sec=25.0)
    assert decision["action"] == "FULL_PIPELINE"
    assert decision["safety_fallback_triggered"] is True

def test_decision_engine_optimize_tests():
    engine = AutonomousDecisionEngine(failure_threshold=0.80, confidence_threshold=0.90, runtime_threshold=18.0)
    decision = engine.evaluate_decision(failure_prob=0.10, model_confidence=0.95, predicted_runtime_sec=24.5)
    assert decision["action"] == "OPTIMIZE_TESTS"
    assert decision["safety_fallback_triggered"] is False

def test_decision_engine_standard_pipeline():
    engine = AutonomousDecisionEngine(failure_threshold=0.80, confidence_threshold=0.90, runtime_threshold=18.0)
    decision = engine.evaluate_decision(failure_prob=0.05, model_confidence=0.98, predicted_runtime_sec=10.0)
    assert decision["action"] == "STANDARD_PIPELINE"
    assert decision["safety_fallback_triggered"] is False

def test_feature_collector_test_count():
    collector = FeatureCollector()
    cnt = collector.count_available_tests()
    assert cnt > 10
