import requests
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Dict, List

# ─────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────
API_KEY = ""  # <- Pega tu API Key aquí
BASE_URL = "https://api.swedavia.se/flightinfo/v2"
HEADERS = {
    "Ocp-Apim-Subscription-Key": API_KEY,
    "Accept": "application/json"
}

AIRPORTS = {
    "ARN": "Stockholm Arlanda",
    "GOT": "Göteborg Landvetter",
    "BMA": "Stockholm Bromma",
    "MMX": "Malmö",
    "LLA": "Luleå",
    "UME": "Umeå",
    "OSD": "Östersund",
    "VBY": "Visby",
    "RNB": "Ronneby",
    "KRN": "Kiruna"
}

# ─────────────────────────────────────────
# Helper: convert UTC time to Swedish time
# ─────────────────────────────────────────
def _fmt_time(utc_str):
    if not utc_str or utc_str == "N/A":
        return "-"
    try:
        utc_str_clean = utc_str.replace("Z", "+00:00")
        dt_utc = datetime.fromisoformat(utc_str_clean)
        # Sweden is UTC+1 (CET) in winter, UTC+2 (CEST) in summer
        dt_se = dt_utc.astimezone(timezone(timedelta(hours=1)))
        return f"{dt_utc.strftime('%H:%M')} UTC -> {dt_se.strftime('%H:%M')} CET"
    except Exception:
        return utc_str

# ─────────────────────────────────────────
# Helper: make a GET request to the API
# ─────────────────────────────────────────
def _get(url, params=None):
    print(f"\n  -> GET {url}")
    if params:
        print(f"     params: {params}")
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
        print(f"     HTTP {resp.status_code}")
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 400:
            print("   x HTTP 400 - Bad request")
            print("     Make sure the date is YYYY-MM-DD and airport is valid")
        elif resp.status_code == 401:
            print("   x HTTP 401 - Invalid API Key")
            print("     Check your API_KEY at the top of this file")
        else:
            print(f"   x Error: {resp.text[:300]}")
        return None
    except requests.exceptions.RequestException as exc:
        print(f"   x Request failed: {exc}")
        return None

# ─────────────────────────────────────────
# Helper: choose airport
# ─────────────────────────────────────────
def _choose_airport():
    print("\nAvailable airports:")
    for code, name in AIRPORTS.items():
        print(f"  {code} - {name}")
    while True:
        raw = input("Enter airport IATA code (e.g. ARN): ").strip()
        if raw.upper() in AIRPORTS:
            return raw.upper()
        print("  ! Unknown airport, try again")

# ─────────────────────────────────────────
# Helper: choose date
# ─────────────────────────────────────────
def _choose_date():
    while True:
        raw = input("Enter date (YYYY-MM-DD / today / tomorrow): ").strip().lower()
        if raw == "today":
            return datetime.now().strftime("%Y-%m-%d")
        if raw == "tomorrow":
            return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        try:
            datetime.strptime(raw, "%Y-%m-%d")
            return raw
        except ValueError:
            print("  ! Invalid date format, try again")

# ─────────────────────────────────────────
# Helper: print a single flight
# ─────────────────────────────────────────
def _print_flight(flight, index=None, home_airport=None):
    prefix   = "[{}] ".format(index) if index is not None else ""
    fid      = flight.get("flightId", "N/A")
    airline  = flight.get("airlineOperator", {})
    arr_time = flight.get("arrivalTime") or flight.get("departureTime") or {}
    loc      = flight.get("locationAndStatus", {})
    baggage  = flight.get("baggage", {})

    frm = flight.get("departureAirportEnglish") or ("({})".format(home_airport) if home_airport else "N/A")
    to  = flight.get("arrivalAirportEnglish")   or ("({})".format(home_airport) if home_airport else "N/A")

    print("─" * 55)
    print("{}{} | {} ({})".format(prefix, fid, airline.get("name", "N/A"), airline.get("iata", "")))
    print("  From    : {}".format(frm))
    print("  To      : {}".format(to))
    print("  Status  : {}".format(loc.get("flightLegStatus", "N/A")))
    print("  Terminal: {}  Gate: {}".format(loc.get("terminal", "N/A"), loc.get("gate", "N/A")))
    print("  Baggage : {}".format(baggage.get("claimUnit", "N/A")))
    print("  Sched   : {}".format(_fmt_time(arr_time.get("scheduledUtc"))))
    print("  Est     : {}".format(_fmt_time(arr_time.get("estimatedUtc"))))
    print("  Actual  : {}".format(_fmt_time(arr_time.get("actualUtc"))))

# ─────────────────────────────────────────
# Helper: print flights with pagination
# ─────────────────────────────────────────
PAGE_SIZE = 50

def _print_flights_paged(flights, home_airport=None):
    total = len(flights)
    for start in range(0, total, PAGE_SIZE):
        page_flights = flights[start:start + PAGE_SIZE]
        for i, f in enumerate(page_flights, start + 1):
            _print_flight(f, i, home_airport)
        shown     = min(start + PAGE_SIZE, total)
        remaining = total - shown
        print("\n-- Showing {}/{} -- ({} remaining)".format(shown, total, remaining))
        if remaining <= 0:
            break
        nav = input("[Enter] next page  |  [a] show all  |  [q] back to menu: ").strip().lower()
        if nav == "q":
            break
        if nav == "a":
            for i, f in enumerate(flights[shown:], shown + 1):
                _print_flight(f, i, home_airport)
            break

# ─────────────────────────────────────────
# Option 1 - Arrivals
# ─────────────────────────────────────────
def get_arrivals():
    airport = _choose_airport()
    date    = _choose_date()
    url     = "{}/{}/arrivals/{}".format(BASE_URL, airport, date)
    data    = _get(url)
    if data:
        flights = data.get("flights", [])
        print("\nFound {} arrivals for {} on {}".format(len(flights), airport, date))
        if flights:
            _print_flights_paged(flights, home_airport=airport)
        else:
            print("  No flights found for this date.")

# ─────────────────────────────────────────
# Option 2 - Departures
# ─────────────────────────────────────────
def get_departures():
    airport = _choose_airport()
    date    = _choose_date()
    url     = "{}/{}/departures/{}".format(BASE_URL, airport, date)
    data    = _get(url)
    if data:
        flights = data.get("flights", [])
        print("\nFound {} departures for {} on {}".format(len(flights), airport, date))
        if flights:
            _print_flights_paged(flights, home_airport=airport)
        else:
            print("  No flights found for this date.")

# ─────────────────────────────────────────
# Option 3 - Search specific flight number
# ─────────────────────────────────────────
def search_flight():
    flight_num = input("Enter flight number (e.g. SK456): ").strip().upper()
    airport    = _choose_airport()
    date       = _choose_date()

    found = []
    for endpoint in ("arrivals", "departures"):
        url  = "{}/{}/{}/{}".format(BASE_URL, airport, endpoint, date)
        data = _get(url)
        if data:
            for f in data.get("flights", []):
                if flight_num in f.get("flightId", ""):
                    found.append(f)

    if found:
        print("\nFound {} result(s) for {}:".format(len(found), flight_num))
        for f in found:
            _print_flight(f, home_airport=airport)
    else:
        print("  No flights found for {} on {} at {}.".format(flight_num, date, airport))

# ─────────────────────────────────────────
# Option 5 - HeartBeat
# ─────────────────────────────────────────
def heartbeat():
    url = "{}/heartBeat".format(BASE_URL)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        print("\n  Status code: {}".format(resp.status_code))
        if resp.status_code == 200:
            print("  API is up and running!")
        else:
            print("  API returned an error")
    except requests.exceptions.RequestException as e:
        print("  Connection error: {}".format(e))

# ─────────────────────────────────────────
# Menu
# ─────────────────────────────────────────
def print_menu():
    print("\n" + "="*50)
    print(" Swedavia FlightInfo API v2 - Python Client")
    print("="*50)
    print("1. Arrivals   - for an airport and date")
    print("2. Departures - for an airport and date")
    print("3. Search specific flight number")
    print("4. OData query endpoint")
    print("5. HeartBeat  - API health check")
    print("6. Demo all endpoints automatically")
    print("q. Quit")
    print("="*50)

def main():
    while True:
        print_menu()
        choice = input("Choose [1-6] or q: ").strip().lower()

        if choice == "q":
            print("Goodbye!")
            break
        elif choice == "1":
            get_arrivals()
        elif choice == "2":
            get_departures()
        elif choice == "3":
            search_flight()
        elif choice == "4":
            print("OData query - coming soon!")
        elif choice == "5":
            heartbeat()
        elif choice == "6":
            print("Demo - coming soon!")
        else:
            print("  Invalid option: {}".format(choice))

if __name__ == "__main__":
    main()
