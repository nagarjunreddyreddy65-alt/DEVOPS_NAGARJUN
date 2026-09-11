from typing import Dict, Optional, Tuple
from .transactions import TransactionRecord, TransactionStatus

class PaymentGateway:
    """Handles payments, authorizations, refunds, and transaction tracking."""
    
    def __init__(self, supported_currencies: Optional[list] = None):
        self.supported_currencies = supported_currencies or ["USD", "EUR", "GBP", "INR"]
        self.transactions: Dict[str, TransactionRecord] = {}
        self.balance: float = 100000.0

    def process_payment(self, customer_id: str, amount: float, currency: str = "USD") -> Tuple[bool, str, Optional[TransactionRecord]]:
        if currency not in self.supported_currencies:
            return False, f"Unsupported currency: {currency}", None
        if amount <= 0:
            return False, "Amount must be strictly positive", None
        if amount > 50000:
            tx = TransactionRecord(amount=amount, currency=currency, customer_id=customer_id, status=TransactionStatus.FAILED, failure_reason="Amount exceeds single-transaction limit")
            self.transactions[tx.transaction_id] = tx
            return False, tx.failure_reason, tx

        tx = TransactionRecord(amount=amount, currency=currency, customer_id=customer_id, status=TransactionStatus.COMPLETED)
        self.transactions[tx.transaction_id] = tx
        self.balance += amount
        return True, "Payment succeeded", tx

    def refund_transaction(self, transaction_id: str, refund_amount: Optional[float] = None) -> Tuple[bool, str]:
        tx = self.transactions.get(transaction_id)
        if not tx:
            return False, "Transaction not found"
        if tx.status != TransactionStatus.COMPLETED:
            return False, f"Cannot refund transaction with status {tx.status}"
        
        amount_to_refund = refund_amount if refund_amount is not None else tx.amount
        if amount_to_refund <= 0 or amount_to_refund > (tx.amount - tx.refund_amount):
            return False, "Invalid refund amount"

        tx.refund_amount += amount_to_refund
        if tx.refund_amount == tx.amount:
            tx.status = TransactionStatus.REFUNDED
        self.balance -= amount_to_refund
        return True, f"Successfully refunded {amount_to_refund} {tx.currency}"

    def get_transaction(self, transaction_id: str) -> Optional[TransactionRecord]:
        return self.transactions.get(transaction_id)
