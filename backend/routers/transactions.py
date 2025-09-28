from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from repositories.transaction_repository import TransactionRepository

router = APIRouter()

# Initialize repository
transaction_db = TransactionRepository("transit_kiosk.db")

# Pydantic models for transactions
class TransactionResponse(BaseModel):
    id: int
    card_id: int
    transaction_time: datetime
    amount: float
    previous_balance: float
    new_balance: float
    station_id: Optional[int]

@router.get("/", response_model=List[TransactionResponse])
async def get_all_transactions():
    """Get all transactions."""
    transactions = transaction_db.get_all()
    return [TransactionResponse(**transaction.to_dict()) for transaction in transactions]

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int):
    """Get a specific transaction by ID."""
    transaction = transaction_db.get_by_id(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return TransactionResponse(**transaction.to_dict())

# Note: Creating transactions is typically done through other operations
# (e.g., adding funds to a card, using a card for a trip, etc.)
# so there's no direct POST endpoint for creating transactions.