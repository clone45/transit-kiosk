from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from repositories.station_repository import StationRepository
from repositories.trip_repository import TripRepository
from repositories.transaction_repository import TransactionRepository
from repositories.pricing_repository import PricingRepository

router = APIRouter()

# Initialize repositories
station_db = StationRepository("transit_kiosk.db")
trip_db = TripRepository("transit_kiosk.db")
transaction_db = TransactionRepository("transit_kiosk.db")
pricing_db = PricingRepository("transit_kiosk.db")

# Pydantic models for stations
class StationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, description="Station name")

class StationResponse(BaseModel):
    id: int
    name: str

# Cross-domain response models
class TripResponse(BaseModel):
    id: int
    card_id: int
    start_time: datetime
    completion_time: Optional[datetime]
    source_station_id: int
    destination_station_id: Optional[int]
    cost: float
    status: str

class TransactionResponse(BaseModel):
    id: int
    card_id: int
    transaction_time: datetime
    amount: float
    previous_balance: float
    new_balance: float
    station_id: Optional[int]

class PricingResponse(BaseModel):
    id: int
    station_a_id: int
    station_b_id: int
    price: float

@router.post("", response_model=StationResponse)
async def create_station(station_data: StationCreate):
    """Create a new station."""
    try:
        station = station_db.create(station_data.name)
        return StationResponse(**station.to_dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail="Station name already exists")

@router.get("", response_model=List[StationResponse])
async def get_all_stations():
    """Get all stations."""
    stations = station_db.get_all()
    return [StationResponse(**station.to_dict()) for station in stations]

@router.get("/{station_id}", response_model=StationResponse)
async def get_station(station_id: int):
    """Get a specific station by ID."""
    station = station_db.get_by_id(station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return StationResponse(**station.to_dict())

@router.put("/{station_id}", response_model=StationResponse)
async def update_station(station_id: int, station_data: StationCreate):
    """Update a station's name."""
    station = station_db.update(station_id, station_data.name)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return StationResponse(**station.to_dict())

@router.delete("/{station_id}")
async def delete_station(station_id: int):
    """Delete a station."""
    success = station_db.delete(station_id)
    if not success:
        raise HTTPException(status_code=404, detail="Station not found")
    return {"message": "Station deleted successfully"}

# Cross-domain endpoints
@router.get("/{station_id}/trips")
async def get_station_trips(station_id: int, as_source: bool = True):
    """Get trips for a station (as source or destination)."""
    # Verify station exists
    station = station_db.get_by_id(station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    trips = trip_db.get_trips_by_station(station_id, as_source)
    return {
        "station_id": station_id,
        "station_name": station.name,
        "role": "source" if as_source else "destination",
        "trips": [TripResponse(**trip.to_dict()) for trip in trips]
    }

@router.get("/{station_id}/transactions", response_model=List[TransactionResponse])
async def get_station_transactions(station_id: int):
    """Get all transactions for a specific station."""
    # Verify station exists
    station = station_db.get_by_id(station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    transactions = transaction_db.get_by_station_id(station_id)
    return [TransactionResponse(**transaction.to_dict()) for transaction in transactions]

@router.get("/{station_id}/revenue")
async def get_station_revenue(station_id: int):
    """Get revenue summary for a station."""
    # Verify station exists
    station = station_db.get_by_id(station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    revenue = transaction_db.get_station_revenue(station_id)
    transactions = transaction_db.get_by_station_id(station_id)

    return {
        "station_id": station_id,
        "station_name": station.name,
        "total_revenue": float(revenue),
        "transaction_count": len([t for t in transactions if t.amount < 0])  # Only count debits
    }

@router.get("/{station_id}/pricing", response_model=List[PricingResponse])
async def get_station_pricing(station_id: int):
    """Get all pricing entries for a specific station."""
    # Verify station exists
    station = station_db.get_by_id(station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    pricing_entries = pricing_db.get_prices_for_station(station_id)
    return [PricingResponse(**pricing.to_dict()) for pricing in pricing_entries]