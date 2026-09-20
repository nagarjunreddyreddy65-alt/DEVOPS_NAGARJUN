import pytest
from src.ast_analyzer import ASTDependencyAnalyzer

def test_ast_symbol_extraction():
    analyzer = ASTDependencyAnalyzer()
    assert len(analyzer.source_symbols) > 0
    # Check that AuthService class is discovered
    auth_symbols = analyzer.source_symbols.get("app/authentication/auth_service.py", set())
    assert "AuthService" in auth_symbols

def test_ast_impacted_tests_resolution():
    analyzer = ASTDependencyAnalyzer()
    res = analyzer.resolve_impacted_tests(["app/payment/payment_gateway.py"])
    assert "tests/test_payment.py" in res["selected_tests"]
    assert "PaymentGateway" in res["impacted_symbols"]

def test_ast_infrastructure_fallback():
    analyzer = ASTDependencyAnalyzer()
    res = analyzer.resolve_impacted_tests(["requirements.txt"])
    assert res["is_full_suite"] is True
    assert "safety fallback" in res["reason"].lower()
