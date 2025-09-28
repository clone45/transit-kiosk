from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from routers import cards, stations, trips, transactions, pricing, admin

app = FastAPI(title="Transit Kiosk API", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cards.router, prefix="/api/cards", tags=["cards"])
app.include_router(stations.router, prefix="/api/stations", tags=["stations"])
app.include_router(trips.router, prefix="/api/trips", tags=["trips"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(pricing.router, prefix="/api/pricing", tags=["pricing"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.get("/")
async def root():
    return {"message": "Transit Kiosk API", "status": "running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)