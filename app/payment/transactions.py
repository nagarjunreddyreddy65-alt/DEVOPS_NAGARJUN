from dataclasses import dataclass, field
from enum import Enum
import time
import uuid
from typing import Optional

class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

@dataclass
class TransactionRecord:
    amount: float
    currency: str
    customer_id: str
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: TransactionStatus = TransactionStatus.PENDING
    timestamp: float = field(default_factory=time.time)
    failure_reason: Optional[str] = None
    refund_amount: float = 0.0
