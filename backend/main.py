import os
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

API_KEY  = os.getenv("SWEDAVIA_API_KEY", "")
BASE_URL = "https://api.swedavia.se/flightinfo/v2"

HEADERS = {
    "Ocp-Apim-Subscription-Key": API_KEY,
    "Accept": "application/json",
}

app = FastAPI(title="Flight Info API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["GET"],
    allow_headers=["*"],
)


async def _fetch(url: str) -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, headers=HEADERS)
    if resp.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid API key")
    if resp.status_code == 400:
        raise HTTPException(status_code=400, detail="Bad request — check airport code or date format")
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text[:300])
    return resp.json()


@app.get("/api/arrivals/{airport}/{date}")
async def arrivals(airport: str, date: str):
    """Returns arrivals for a given airport (IATA) and date (YYYY-MM-DD)."""
    data = await _fetch(f"{BASE_URL}/{airport.upper()}/arrivals/{date}")
    return data.get("flights", [])


@app.get("/api/departures/{airport}/{date}")
async def departures(airport: str, date: str):
    """Returns departures for a given airport (IATA) and date (YYYY-MM-DD)."""
    data = await _fetch(f"{BASE_URL}/{airport.upper()}/departures/{date}")
    return data.get("flights", [])


@app.get("/api/search")
async def search_flight(
    flight: str = Query(..., description="Flight number e.g. SK456"),
    airport: str = Query(..., description="IATA code e.g. ARN"),
    date: str   = Query(..., description="Date YYYY-MM-DD"),
):
    """Search a specific flight number across arrivals and departures."""
    found = []
    for endpoint in ("arrivals", "departures"):
        try:
            data = await _fetch(f"{BASE_URL}/{airport.upper()}/{endpoint}/{date}")
            for f in data.get("flights", []):
                if flight.upper() in f.get("flightId", "").upper():
                    found.append(f)
        except HTTPException:
            pass
    return found


@app.get("/api/heartbeat")
async def heartbeat():
    """Check if Swedavia API is reachable."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{BASE_URL}/heartBeat", headers=HEADERS)
    return {"status": resp.status_code, "ok": resp.status_code == 200}


@app.get("/api/airports")
async def airports():
    """Returns the list of supported airports."""
    return [
        {"code": "ARN", "name": "Stockholm Arlanda"},
        {"code": "GOT", "name": "Göteborg Landvetter"},
        {"code": "BMA", "name": "Stockholm Bromma"},
        {"code": "MMX", "name": "Malmö"},
        {"code": "LLA", "name": "Luleå"},
        {"code": "UME", "name": "Umeå"},
        {"code": "OSD", "name": "Östersund"},
        {"code": "VBY", "name": "Visby"},
        {"code": "RNB", "name": "Ronneby"},
        {"code": "KRN", "name": "Kiruna"},
    ]
