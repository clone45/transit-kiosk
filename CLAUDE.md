# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## user requests

- Please use unique ids when creating important HTML elements so that I can refer to them more easily
- Please avoid using "fallback" code that can mask errors that are important to catch

## Project Overview

Transit Kiosk is a full-stack transit card management system with a Python FastAPI backend and Vue.js frontend. The system manages transit cards, stations, trips, transactions, and pricing for a public transit system.

## Architecture

### Backend (Python/FastAPI)
- **Repository Pattern**: All database operations use the repository pattern inheriting from `BaseRepository` (backend/repositories/base.py)
  - Repositories manage SQLite connections and provide CRUD operations
  - Each model has a corresponding repository (e.g., `TransitCardRepository`, `TripRepository`)

- **Models**: Dataclasses in backend/models/ represent domain entities
  - `TransitCard`: Manages card balance, usage tracking
  - `Trip`: Tracks journeys with states (active/completed/cancelled) via `TripStatus` enum
  - `Transaction`: Records all financial transactions (credits/debits)
  - `Station`: Transit system locations
  - `Pricing`: Distance-based fare calculation

- **Routers**: FastAPI routers in backend/routers/ expose REST endpoints
  - `/api/cards`: Card management, balance operations
  - `/api/trips`: Trip start/complete/cancel operations
  - `/api/stations`: Station management
  - `/api/transactions`: Transaction history
  - `/api/pricing`: Fare calculations
  - `/api/admin`: Administrative operations

### Frontend (Vue 3)
- Single-page application using Vue 3 Composition API
- API client in frontend/src/api/client.js uses Axios
- Environment variable `VITE_API_URL` configures backend connection (defaults to `/api`)

### Database
- SQLite database file: `transit_kiosk.db` (created automatically, gitignored)
- Raw SQL queries with connection management handled by `BaseRepository`
- **Database Migrations**: Schema managed via SQL migration files
  - Migrations: `backend/db/migrations/*.sql`
  - Run with: `python migrate.py`
  - Tracked in `_migrations` table
- **Database Seeding**: Uses explicit CLI-based seeding (not automatic in repositories)
  - Development seeds: `backend/db/seeds/dev/*.sql`
  - Run with: `python seed.py --tag dev` (automatically runs migrations first)
  - Tracked in `_seed_runs` table
  - Includes test transit card with UUID `12345678-1234-1234-1234-123456789abc`

## Common Development Commands

### Backend
```bash
cd backend

# Setup (first time)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Run migrations and seed development data (includes test transit card)
python seed.py --tag dev
# Or run migrations separately: python migrate.py

# Run development server (with hot reload)
python main.py
# Or: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# API documentation
# Visit http://localhost:8000/docs after starting server
```

### Frontend
```bash
cd frontend

# Setup (first time)
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### Docker
```bash
# Start both services
docker-compose up

# Rebuild containers
docker-compose up --build
```

## Key Development Patterns

### Adding a New Model
1. Create dataclass in backend/models/ with `to_dict()` method
2. Create repository inheriting from `BaseRepository` with `_init_db()` implementation
3. Create router with Pydantic request/response models
4. Register router in backend/main.py with `app.include_router()`

### Adding API Endpoints
- Use Pydantic models for request/response validation
- Initialize repositories at router module level
- Verify entity existence before operations (return 404 if not found)
- Use HTTPException for error responses
- Follow RESTful conventions

### Frontend API Integration
- Add new API methods to frontend/src/api/client.js
- All requests go through the configured apiClient instance
- Handle loading states and errors in components
- **State Management**: `fareStore` (frontend/src/stores/fareStore.js) currently caches minimum fare
  - TODO: When implementing station-to-station pricing, consider caching fare calculations in fareStore to avoid repeated API calls

## Important Notes

- The backend uses raw SQL (via sqlite3) not an ORM
- All decimal/currency values use Python's `Decimal` type, converted to float for JSON
- Trip status is managed via `TripStatus` enum (active/completed/cancelled)
- Card balance validation happens in repository layer before transactions
- CORS is configured for localhost:5173 and localhost:3000
- Database path is hardcoded as "transit_kiosk.db" in repository constructors