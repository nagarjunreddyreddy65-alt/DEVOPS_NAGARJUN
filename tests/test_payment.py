import pytest
from app.payment.payment_gateway import PaymentGateway
from app.payment.transactions import TransactionStatus

@pytest.fixture
def gateway():
    return PaymentGateway()

def test_process_payment_success(gateway):
    ok, msg, tx = gateway.process_payment("cust_123", 250.0, "USD")
    assert ok is True
    assert tx.status == TransactionStatus.COMPLETED
    assert tx.amount == 250.0
    assert gateway.balance == 100250.0

def test_process_payment_unsupported_currency(gateway):
    ok, msg, tx = gateway.process_payment("cust_123", 100.0, "XYZ")
    assert ok is False
    assert "Unsupported currency" in msg

def test_process_payment_exceed_limit(gateway):
    ok, msg, tx = gateway.process_payment("cust_123", 999999.0, "USD")
    assert ok is False
    assert "limit" in msg
    assert tx.status == TransactionStatus.FAILED

def test_process_payment_negative_amount(gateway):
    ok, msg, tx = gateway.process_payment("cust_123", -50.0, "USD")
    assert ok is False

def test_refund_transaction_full(gateway):
    _, _, tx = gateway.process_payment("cust_456", 500.0, "USD")
    ok, msg = gateway.refund_transaction(tx.transaction_id)
    assert ok is True
    assert tx.status == TransactionStatus.REFUNDED
    assert gateway.balance == 100000.0

def test_refund_transaction_partial(gateway):
    _, _, tx = gateway.process_payment("cust_789", 400.0, "USD")
    ok, msg = gateway.refund_transaction(tx.transaction_id, refund_amount=150.0)
    assert ok is True
    assert tx.status == TransactionStatus.COMPLETED
    assert tx.refund_amount == 150.0
