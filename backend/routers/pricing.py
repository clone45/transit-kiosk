from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import List
from repositories.pricing_repository import PricingRepository
from repositories.station_repository import StationRepository

router = APIRouter()

# Initialize repositories
pricing_db = PricingRepository("transit_kiosk.db")
station_db = StationRepository("transit_kiosk.db")

# Pydantic models for pricing
class PricingCreate(BaseModel):
    station_a_id: int = Field(gt=0, description="First station ID")
    station_b_id: int = Field(gt=0, description="Second station ID")
    price: Decimal = Field(gt=0, description="Price for this route")

class PricingResponse(BaseModel):
    id: int
    station_a_id: int
    station_b_id: int
    price: float

@router.post("/", response_model=PricingResponse)
async def create_pricing(pricing_data: PricingCreate):
    """Create a new pricing entry between two stations."""
    # Verify both stations exist
    station_a = station_db.get_by_id(pricing_data.station_a_id)
    station_b = station_db.get_by_id(pricing_data.station_b_id)

    if not station_a:
        raise HTTPException(status_code=404, detail="Station A not found")
    if not station_b:
        raise HTTPException(status_code=404, detail="Station B not found")

    # Prevent pricing between same station
    if pricing_data.station_a_id == pricing_data.station_b_id:
        raise HTTPException(status_code=400, detail="Cannot create pricing between the same station")

    try:
        pricing = pricing_db.create(pricing_data.station_a_id, pricing_data.station_b_id, pricing_data.price)
        return PricingResponse(**pricing.to_dict())
    except Exception:
        raise HTTPException(status_code=400, detail="Pricing already exists between these stations")

@router.get("/", response_model=List[PricingResponse])
async def get_all_pricing():
    """Get all pricing entries."""
    pricing_entries = pricing_db.get_all()
    return [PricingResponse(**pricing.to_dict()) for pricing in pricing_entries]

@router.get("/minimum")
async def get_minimum_fare():
    """Get the minimum fare across all routes."""
    lowest = pricing_db.get_lowest_price()
    if not lowest:
        raise HTTPException(status_code=404, detail="No pricing data available")

    return {
        "minimum_fare": float(lowest.price)
    }

@router.get("/stats")
async def get_pricing_stats():
    """Get pricing statistics."""
    highest = pricing_db.get_highest_price()
    lowest = pricing_db.get_lowest_price()
    average = pricing_db.get_average_price()
    all_pricing = pricing_db.get_all()

    return {
        "total_routes": len(all_pricing),
        "highest_price": float(highest.price) if highest else 0.0,
        "lowest_price": float(lowest.price) if lowest else 0.0,
        "average_price": float(average),
        "highest_price_route": {
            "station_a_id": highest.station_a_id,
            "station_b_id": highest.station_b_id,
            "price": float(highest.price)
        } if highest else None,
        "lowest_price_route": {
            "station_a_id": lowest.station_a_id,
            "station_b_id": lowest.station_b_id,
            "price": float(lowest.price)
        } if lowest else None
    }

@router.get("/between/{station_a_id}/{station_b_id}")
async def get_price_between_stations(station_a_id: int, station_b_id: int):
    """Get price between two specific stations."""
    # Verify both stations exist
    station_a = station_db.get_by_id(station_a_id)
    station_b = station_db.get_by_id(station_b_id)

    if not station_a:
        raise HTTPException(status_code=404, detail="Station A not found")
    if not station_b:
        raise HTTPException(status_code=404, detail="Station B not found")

    price = pricing_db.get_price(station_a_id, station_b_id)
    if price is None:
        raise HTTPException(status_code=404, detail="No pricing found between these stations")

    return {
        "station_a_id": station_a_id,
        "station_a_name": station_a.name,
        "station_b_id": station_b_id,
        "station_b_name": station_b.name,
        "price": float(price)
    }

@router.put("/between/{station_a_id}/{station_b_id}", response_model=PricingResponse)
async def update_pricing(station_a_id: int, station_b_id: int, price_update: dict):
    """Update price between two stations."""
    # Verify both stations exist
    station_a = station_db.get_by_id(station_a_id)
    station_b = station_db.get_by_id(station_b_id)

    if not station_a:
        raise HTTPException(status_code=404, detail="Station A not found")
    if not station_b:
        raise HTTPException(status_code=404, detail="Station B not found")

    new_price = Decimal(str(price_update.get("price", 0)))
    if new_price <= 0:
        raise HTTPException(status_code=400, detail="Price must be greater than 0")

    pricing = pricing_db.update_price(station_a_id, station_b_id, new_price)
    if not pricing:
        raise HTTPException(status_code=404, detail="No pricing found between these stations")

    return PricingResponse(**pricing.to_dict())

@router.delete("/between/{station_a_id}/{station_b_id}")
async def delete_pricing(station_a_id: int, station_b_id: int):
    """Delete pricing between two stations."""
    # Verify both stations exist
    station_a = station_db.get_by_id(station_a_id)
    station_b = station_db.get_by_id(station_b_id)

    if not station_a:
        raise HTTPException(status_code=404, detail="Station A not found")
    if not station_b:
        raise HTTPException(status_code=404, detail="Station B not found")

    success = pricing_db.delete_pricing(station_a_id, station_b_id)
    if not success:
        raise HTTPException(status_code=404, detail="No pricing found between these stations")

    return {"message": "Pricing deleted successfully"}

@router.get("/{pricing_id}", response_model=PricingResponse)
async def get_pricing(pricing_id: int):
    """Get a specific pricing entry by ID."""
    pricing = pricing_db.get_by_id(pricing_id)
    if not pricing:
        raise HTTPException(status_code=404, detail="Pricing not found")
    return PricingResponse(**pricing.to_dict())