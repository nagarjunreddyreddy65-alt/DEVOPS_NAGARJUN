from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from app.payment.payment_gateway import PaymentGateway
from app.payment.transactions import TransactionStatus

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])

gateway = PaymentGateway()

class PaymentRequest(BaseModel):
    customer_id: str
    amount: float = Field(gt=0, description="Amount must be positive")
    currency: Optional[str] = "USD"

class RefundRequest(BaseModel):
    transaction_id: str
    amount: Optional[float] = None

class TransactionResponse(BaseModel):
    transaction_id: str
    customer_id: str
    amount: float
    currency: str
    status: str
    timestamp: float
    refund_amount: float
    failure_reason: Optional[str] = None

@router.post("/charge", response_model=TransactionResponse)
def charge_payment(req: PaymentRequest):
    success, msg, tx = gateway.process_payment(
        customer_id=req.customer_id,
        amount=req.amount,
        currency=req.currency or "USD"
    )
    if not success or not tx:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg
        )
    return TransactionResponse(
        transaction_id=tx.transaction_id,
        customer_id=tx.customer_id,
        amount=tx.amount,
        currency=tx.currency,
        status=tx.status.value,
        timestamp=tx.timestamp,
        refund_amount=tx.refund_amount,
        failure_reason=tx.failure_reason
    )

@router.post("/refund")
def refund_payment(req: RefundRequest):
    success, msg = gateway.refund_transaction(
        transaction_id=req.transaction_id,
        refund_amount=req.amount
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    return {"message": msg, "transaction_id": req.transaction_id}

@router.get("/transaction/{tx_id}", response_model=TransactionResponse)
def get_transaction_status(tx_id: str):
    tx = gateway.get_transaction(tx_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return TransactionResponse(
        transaction_id=tx.transaction_id,
        customer_id=tx.customer_id,
        amount=tx.amount,
        currency=tx.currency,
        status=tx.status.value,
        timestamp=tx.timestamp,
        refund_amount=tx.refund_amount,
        failure_reason=tx.failure_reason
    )
