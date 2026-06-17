# Swedavia Flight Info

Real-time flight data for Swedish airports using the [Swedavia FlightInfo API v2](https://api.swedavia.se).

## Stack

- **Frontend**: React 19 + Vite (axios)
- **Backend**: FastAPI + httpx (Python)

## Setup

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
```

Edit `backend/.env` and add your API key:
```
SWEDAVIA_API_KEY=your_actual_key_here
```

Start the backend:
```bash
uvicorn main:app --reload
```
Runs on http://localhost:8000

### 2. Frontend

```bash
# from project root
npm install
npm run dev
```
Runs on http://localhost:5173

## Usage

Open http://localhost:5173 in your browser.

- **Arrivals** — flights landing at an airport on a given date
- **Departures** — flights departing from an airport on a given date
- **Search Flight** — find a specific flight number (e.g. SK456)
