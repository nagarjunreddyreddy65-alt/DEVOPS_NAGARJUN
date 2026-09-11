from dataclasses import dataclass
from typing import Optional

@dataclass
class UserRecord:
    username: str
    email: str
    role: str
    is_active: bool = True

@dataclass
class TransactionModel:
    transaction_id: str
    customer_id: str
    amount: float
    currency: str
    status: str
    created_at: float

@dataclass
class PipelineExecutionModel:
    run_id: str
    commit_id: str
    pipeline_type: str  # "baseline" or "ai_optimized"
    decision_action: str
    runtime_sec: float
    test_count: int
    cpu_usage_pct: float
    memory_usage_mb: float
    result: int  # 0: success, 1: failure
    timestamp: float
