# Transit Kiosk Application

A full-stack transit card management system with Python FastAPI backend and Vue.js frontend. The system manages transit cards, stations, trips, transactions, and pricing for a public transit system with offline capabilities.

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLite with raw SQL queries
- **Frontend**: Vue 3 Composition API, Vite, Tailwind CSS, Axios
- **Database**: SQLite (local file, included in repository)
- **Architecture**: Repository pattern, offline-first design

## Project Structure

```
transit_kiosk/
├── backend/                     # Python FastAPI application
│   ├── models/                  # Domain models (TransitCard, Trip, etc.)
│   ├── repositories/            # Data access layer with repository pattern
│   ├── routers/                 # API endpoints
│   ├── db/                      # Database migrations and seeds
│   ├── test_transit.py          # Unit tests
│   └── transit_kiosk.db         # SQLite database (included)
├── frontend/                    # Vue.js kiosk application
│   ├── src/
│   │   ├── views/              # Kiosk workflow views
│   │   ├── stores/             # State management
│   │   ├── services/           # Business logic and API integration
│   │   └── config/
│   │       └── transitConfig.json  # Static configuration fallback
└── README.md
```

## Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm

### Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Run development server
python main.py
# API will be available at http://localhost:8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
# Kiosk interface will be available at http://localhost:5173
```

## How to Run

### Development Mode
1. Start the backend: `cd backend && python main.py`
2. Start the frontend: `cd frontend && npm run dev`
3. Access the kiosk interface at http://localhost:5173

### Production Mode
```bash
# Backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run build
# Serve the dist/ folder with any static file server
```

## How to Run Tests

### Backend Unit Tests
```bash
cd backend
python -m pytest test_transit.py -v
```

The tests cover:
- **Fare Calculation**: Price lookup, station ordering, edge cases, minimum fare
- **Tap Flow**: Card entry/exit validation, trip lifecycle, balance checking

### Frontend
Currently no frontend tests configured, but the structure supports:
```bash
cd frontend
npm run test  # When tests are added
```

## Database Setup

**⚠️ No database setup required!** The SQLite database file (`transit_kiosk.db`) is included in the repository with seeded data for demonstration purposes.

The database includes:
- 8 sample transit stations
- Station-to-station pricing matrix
- Test transit card with UUID: `12345678-1234-1234-1234-123456789abc`
- Sample transaction history

### Manual Database Operations (Optional)
```bash
cd backend

# Run migrations (creates tables if needed)
python migrate.py

# Seed development data (includes test card)
python seed.py --tag dev
```

## Transit Configuration File

### Location
`frontend/src/config/transitConfig.json`

### How to Edit
This JSON file serves as an offline fallback configuration. You can edit it directly:

```bash
# Edit the configuration
nano frontend/src/config/transitConfig.json
# or use any text editor
```

### File Format
```json
{
  "lastUpdated": "2025-09-28T23:16:00Z",
  "version": "1.0.0",
  "stations": [
    { "id": 1, "name": "Central Station" },
    { "id": 2, "name": "Union Square" }
  ],
  "pricing": [
    { "stationA": 1, "stationB": 2, "fare": 3.25 }
  ],
  "minimumFare": 2.25
}
```

**Schema:**
- `lastUpdated`: ISO timestamp of last update
- `version`: Configuration version
- `stations`: Array of station objects with `id` and `name`
- `pricing`: Array of pricing objects with `stationA`, `stationB`, and `fare`
- `minimumFare`: System-wide minimum fare amount

### Important: Why This File May Not Be the Source of Truth

⚠️ **The database is the primary source of truth, not the JSON configuration file.**

**How the system works:**
1. **Online Mode**: The application fetches live data from the backend database
2. **Offline Mode**: Falls back to the static JSON configuration when the backend is unavailable
3. **Data Priority**: Database data always takes precedence over JSON configuration

**Key implications:**
- Changes to `transitConfig.json` only affect offline operation
- To update live system data, modify the database through the API or admin interface
- The JSON file should be updated periodically to match database state for offline consistency
- Database migrations and seeding are the authoritative way to manage system data


## API Documentation

Visit http://localhost:8000/docs for API documentation and schema information.

**⚠️ Note**: Most endpoints require API key authentication. The interactive docs are useful for viewing schemas but testing requires a valid API key in the `X-API-Key` header.

**Key endpoints:**
- `POST /api/cards` - Create transit card
- `GET /api/cards/uuid/{uuid}` - Get card by UUID
- `POST /api/trips` - Start trip (card entry)
- `POST /api/trips/{id}/complete` - Complete trip (card exit)
- `GET /api/stations` - List all stations
- `GET /api/pricing` - Get all pricing information
- `GET /api/pricing/minimum` - Get minimum fare

**Authentication:**
All API endpoints require an `X-API-Key` header. API keys can be created through the admin interface or directly in the database.

**Note for Development/Testing:**
The API key requirement makes interactive testing through the Swagger UI challenging. In a production system, this would typically be addressed by providing development API keys in documentation or implementing environment-based authentication exemptions for local development.

