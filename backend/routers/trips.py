from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from repositories.trip_repository import TripRepository
from repositories.transit_card_repository import TransitCardRepository
from repositories.station_repository import StationRepository
from repositories.pricing_repository import PricingRepository

router = APIRouter()

# Initialize repositories
trip_db = TripRepository("transit_kiosk.db")
card_db = TransitCardRepository("transit_kiosk.db")
station_db = StationRepository("transit_kiosk.db")
pricing_db = PricingRepository("transit_kiosk.db")

# Pydantic models for trips
class TripCreate(BaseModel):
    card_uuid: str = Field(description="Transit card UUID")
    source_station_id: int = Field(gt=0, description="Starting station ID")

class TripComplete(BaseModel):
    destination_station_id: int = Field(gt=0, description="Destination station ID")
    final_cost: Optional[Decimal] = Field(default=None, ge=0, description="Final trip cost (optional)")

class TripResponse(BaseModel):
    id: int
    card_id: int
    start_time: datetime
    completion_time: Optional[datetime]
    source_station_id: int
    destination_station_id: Optional[int]
    cost: float
    status: str

@router.post("/", response_model=TripResponse)
async def create_trip(trip_data: TripCreate):
    """Start a new trip."""
    # Verify card exists by UUID
    card = card_db.get_by_uuid(trip_data.card_uuid)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found. Please speak to a station agent.")

    # Check if card has sufficient balance for minimum fare
    lowest_pricing = pricing_db.get_lowest_price()
    if lowest_pricing:
        minimum_fare = lowest_pricing.price
        if card.balance < minimum_fare:
            raise HTTPException(status_code=400, detail="Insufficient balance. Please add funds at a station kiosk.")

    # Verify station exists
    station = station_db.get_by_id(trip_data.source_station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    # Check if card already has an active trip from this station
    active_trip = trip_db.get_active_trip_by_card(card.id)
    if active_trip and active_trip.source_station_id == trip_data.source_station_id:
        # Cancel the previous incomplete trip from the same station
        trip_db.cancel_trip(active_trip.id)

    # Create the trip with zero initial cost (unknown until completion)
    trip = trip_db.create(card.id, trip_data.source_station_id, Decimal('0.00'))
    return TripResponse(**trip.to_dict())

@router.get("/", response_model=List[TripResponse])
async def get_all_trips():
    """Get all trips."""
    trips = trip_db.get_all()
    return [TripResponse(**trip.to_dict()) for trip in trips]

@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(trip_id: int):
    """Get a specific trip by ID."""
    trip = trip_db.get_by_id(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return TripResponse(**trip.to_dict())

@router.post("/{trip_id}/complete", response_model=TripResponse)
async def complete_trip(trip_id: int, completion_data: TripComplete):
    """Complete an active trip."""
    # Verify destination station exists
    station = station_db.get_by_id(completion_data.destination_station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Destination station not found")

    trip = trip_db.complete_trip(trip_id, completion_data.destination_station_id, completion_data.final_cost)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found or not active")
    return TripResponse(**trip.to_dict())

@router.post("/{trip_id}/cancel", response_model=TripResponse)
async def cancel_trip(trip_id: int):
    """Cancel an active trip."""
    trip = trip_db.cancel_trip(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found or not active")
    return TripResponse(**trip.to_dict())