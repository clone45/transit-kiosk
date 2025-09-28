from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from repositories.transit_card_repository import TransitCardRepository
from repositories.transaction_repository import TransactionRepository
from repositories.trip_repository import TripRepository

router = APIRouter()

# Initialize repositories
card_db = TransitCardRepository("transit_kiosk.db")
transaction_db = TransactionRepository("transit_kiosk.db")
trip_db = TripRepository("transit_kiosk.db")

# Pydantic models for cards
class TransitCardCreate(BaseModel):
    initial_balance: Decimal = Field(default=Decimal('0.00'), ge=0, description="Initial balance for the card")
    uuid: Optional[str] = Field(default=None, description="Optional UUID for the card (generated if not provided)")

class TransitCardResponse(BaseModel):
    id: int
    balance: float
    created_at: datetime
    last_used_at: Optional[datetime]
    usage_count: int

class AddFundsRequest(BaseModel):
    amount: Decimal = Field(gt=0, description="Amount to add to the card")

class UseCardRequest(BaseModel):
    fare: Decimal = Field(gt=0, description="Fare amount to deduct")


class TransactionResponse(BaseModel):
    id: int
    card_id: int
    transaction_time: datetime
    amount: float
    previous_balance: float
    new_balance: float
    station_id: Optional[int]

class TripResponse(BaseModel):
    id: int
    card_id: int
    start_time: datetime
    completion_time: Optional[datetime]
    source_station_id: int
    destination_station_id: Optional[int]
    cost: float
    status: str

@router.post("/", response_model=TransitCardResponse)
async def create_card(card_data: TransitCardCreate):
    """Create a new transit card with optional initial balance and UUID."""
    card = card_db.create(card_data.initial_balance, card_data.uuid)
    return TransitCardResponse(**card.to_dict())

@router.get("/", response_model=List[TransitCardResponse])
async def get_all_cards():
    """Get all transit cards."""
    cards = card_db.get_all()
    return [TransitCardResponse(**card.to_dict()) for card in cards]

@router.get("/{card_id}", response_model=TransitCardResponse)
async def get_card(card_id: int):
    """Get a specific transit card by ID."""
    card = card_db.get_by_id(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return TransitCardResponse(**card.to_dict())

@router.get("/uuid/{card_uuid}", response_model=TransitCardResponse)
async def get_card_by_uuid(card_uuid: str):
    """Get a specific transit card by UUID."""
    card = card_db.get_by_uuid(card_uuid)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return TransitCardResponse(**card.to_dict())

@router.post("/{card_id}/add-funds", response_model=TransitCardResponse)
async def add_funds(card_id: int, request: AddFundsRequest):
    """Add funds to a transit card."""
    card = card_db.add_funds(card_id, request.amount)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return TransitCardResponse(**card.to_dict())

@router.post("/{card_id}/use", response_model=TransitCardResponse)
async def use_card(card_id: int, request: UseCardRequest):
    """Use a transit card - deduct fare and record usage."""
    try:
        card = card_db.record_usage(card_id, request.fare)
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        return TransitCardResponse(**card.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{card_id}/history")
async def get_card_history(card_id: int):
    """Get usage history for a card (placeholder for future enhancement)."""
    card = card_db.get_by_id(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    return {
        "card_id": card_id,
        "total_uses": card.usage_count,
        "last_used": card.last_used_at,
        "message": "Detailed history tracking coming soon"
    }

@router.get("/{card_id}/transactions", response_model=List[TransactionResponse])
async def get_card_transactions(card_id: int):
    """Get all transactions for a specific card."""
    # Verify card exists
    card = card_db.get_by_id(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    transactions = transaction_db.get_by_card_id(card_id)
    return [TransactionResponse(**transaction.to_dict()) for transaction in transactions]

@router.get("/{card_id}/transactions/credits", response_model=List[TransactionResponse])
async def get_card_credits(card_id: int):
    """Get all credit transactions for a card."""
    # Verify card exists
    card = card_db.get_by_id(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    transactions = transaction_db.get_credits_by_card(card_id)
    return [TransactionResponse(**transaction.to_dict()) for transaction in transactions]

@router.get("/{card_id}/transactions/debits", response_model=List[TransactionResponse])
async def get_card_debits(card_id: int):
    """Get all debit transactions for a card."""
    # Verify card exists
    card = card_db.get_by_id(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    transactions = transaction_db.get_debits_by_card(card_id)
    return [TransactionResponse(**transaction.to_dict()) for transaction in transactions]

@router.get("/{card_id}/transaction-summary")
async def get_card_transaction_summary(card_id: int):
    """Get transaction summary for a card."""
    # Verify card exists
    card = card_db.get_by_id(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    total_spent = transaction_db.get_total_spent_by_card(card_id)
    total_added = transaction_db.get_total_added_by_card(card_id)
    latest_transaction = transaction_db.get_latest_transaction_by_card(card_id)

    return {
        "card_id": card_id,
        "current_balance": float(card.balance),
        "total_spent": float(total_spent),
        "total_added": float(total_added),
        "transaction_count": len(transaction_db.get_by_card_id(card_id)),
        "latest_transaction": TransactionResponse(**latest_transaction.to_dict()) if latest_transaction else None
    }

@router.get("/{card_id}/trips", response_model=List[TripResponse])
async def get_card_trips(card_id: int):
    """Get all trips for a specific card."""
    # Verify card exists
    card = card_db.get_by_id(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    trips = trip_db.get_by_card_id(card_id)
    return [TripResponse(**trip.to_dict()) for trip in trips]

@router.get("/{card_id}/active-trip", response_model=Optional[TripResponse])
async def get_card_active_trip(card_id: int):
    """Get active trip for a card (if any)."""
    # Verify card exists
    card = card_db.get_by_id(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    trip = trip_db.get_active_trip_by_card(card_id)
    if trip:
        return TripResponse(**trip.to_dict())
    return None

