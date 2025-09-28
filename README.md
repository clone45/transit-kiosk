# Transit Kiosk Application

A full-stack application with Python (FastAPI) backend and Vue.js frontend.

## Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, SQLite
- **Frontend**: Vue 3, Vite, Axios
- **Database**: SQLite (local file)

## Project Structure

```
transit_kiosk/
├── backend/          # Python FastAPI application
├── frontend/         # Vue.js application
├── docker-compose.yml # Docker orchestration
└── README.md
```

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd transit_kiosk

# Start both services
docker-compose up

# Access the application
# Frontend: http://localhost:5173
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

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

# Run the server
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
# Frontend will be available at http://localhost:5173
```

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

## Available Endpoints

- `GET /` - API root
- `GET /api/health` - Health check
- `GET /api/items` - List all items
- `POST /api/items` - Create new item
- `GET /api/items/{id}` - Get specific item

## Development

### Backend Development

The backend uses FastAPI with auto-reload enabled. Any changes to Python files will automatically restart the server.

### Frontend Development

The frontend uses Vite with HMR (Hot Module Replacement). Changes to Vue components will be reflected immediately in the browser.

### Database

SQLite database file (`transit_kiosk.db`) is created automatically on first run and is gitignored by default.

## Environment Variables

### Backend (.env)
- `DATABASE_URL`: SQLite connection string (default: `sqlite:///./transit_kiosk.db`)

### Frontend
- `VITE_API_URL`: Backend API URL (default: `/api` which proxies to localhost:8000)

## Testing

### Backend
```bash
cd backend
# Add your test commands here
```

### Frontend
```bash
cd frontend
npm run test  # If tests are configured
```

## Building for Production

### Backend
```bash
cd backend
# Use production ASGI server
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend
```bash
cd frontend
npm run build
# Serve the dist/ folder with any static file server
```

## License

[Your License Here]