# Project Documentation — Swedavia Flight Info

> All documentation is written in English.

---

## Phase 1: Research (Pre-study)

### What was included

- Research on available flight data APIs for Sweden
- Found the **Swedavia FlightInfo API v2** — the official API for Swedish airports
- Registered at https://developer.swedavia.com to obtain an API key
- Studied the API endpoints: arrivals, departures, flight search, heartbeat
- Evaluated tools and technologies:
  - **Python** for initial CLI testing (`airport.py`)
  - **React + Vite** for the frontend web interface
  - **FastAPI + httpx** for the backend server
  - **axios** for HTTP requests from the frontend
- Planned the architecture: React frontend → FastAPI backend → Swedavia API

### Problems and Solutions

| Problem | Solution |
|---------|----------|
| Difficult to understand the API response structure | Tested the API directly in Python CLI first to inspect the raw JSON data |
| Unclear how to protect the API key in a web project | Decided to use a FastAPI backend so the key stays server-side in a `.env` file, never exposed to the browser |
| CORS issues when calling the API directly from the browser | Solved by routing all requests through the FastAPI backend, which handles CORS properly |

---

## Phase 2: Starting the Work (Implementation)

### What was included

- Started with a Python CLI client (`airport.py`) to verify the API worked and understand the data structure
- Built the FastAPI backend (`backend/main.py`) with four endpoints:
  - `GET /api/arrivals/{airport}/{date}`
  - `GET /api/departures/{airport}/{date}`
  - `GET /api/search?flight=&airport=&date=`
  - `GET /api/heartbeat`
  - `GET /api/airports`
- Configured the Vite dev server proxy to forward `/api` requests to the FastAPI backend
- Built the React frontend with:
  - Tab navigation (Arrivals / Departures / Search Flight)
  - Airport selector with all 10 Swedish airports
  - Date picker defaulting to today
  - Flight results table with status badges
  - Loading spinner and error handling
  - Responsive design with dark mode support

### Problems and Solutions

| Problem | Solution |
|---------|----------|
| API key was hardcoded in `airport.py` — not safe for a web project | Moved the key to `backend/.env` and loaded it with `python-dotenv` |
| The Vite dev server blocked requests to the external API (CORS) | Configured a proxy in `vite.config.js` to forward `/api` calls to `http://localhost:8000` |
| Flight times came in UTC format and were hard to read | Added a `formatTime()` function to convert UTC to Swedish time (Europe/Stockholm) |
| Status labels from the API were inconsistent | Created a `statusClass()` function to map status text to color-coded badges (green/yellow/red) |
| Backend was started from the wrong directory | Must run `uvicorn main:app --reload` from inside the `backend/` folder |

---

## Phase 3: Finishing the Work (Completion & Improvement)

### What was included

- Tested all three tabs: Arrivals, Departures, and Flight Search
- Verified the API key loaded correctly from `.env`
- Added the `.env` file and `venv/` folder to `.gitignore` to prevent secrets from being pushed to GitHub
- Cleaned up the default Vite template (removed placeholder content, logos, and unused styles)
- Updated `index.html` title to "Swedavia Flight Info"
- Pushed the project to GitHub: https://github.com/datorprogrammerare-hub/flight-project
- Wrote a README with setup instructions in English

### Problems and Solutions

| Problem | Solution |
|---------|----------|
| `.env` was not in `.gitignore` — API key could have been pushed to GitHub | Added `.env`, `backend/.env`, and `venv/` to `.gitignore` before the first commit |
| Git branch was named `master` instead of `main` | Used `git push -u origin master` to match the local branch name |
| Backend returned "Invalid API key" error | The key in `.env` was not copied correctly — fixed by reading it directly from `airport.py` |

---

## Phase 4: Problems & Solutions (Summary)

| Problem | Solution |
|---------|----------|
| API key security in a web project | Stored in `backend/.env`, loaded server-side only, never sent to the browser |
| CORS blocking browser requests to Swedavia API | FastAPI backend acts as a proxy; Vite dev server forwards `/api` to `localhost:8000` |
| UTC times were confusing | Converted to Swedish local time using `toLocaleTimeString` with `timeZone: 'Europe/Stockholm'` |
| Flight status labels inconsistent across flights | Color-coded badge system based on keyword matching in status text |
| API key not loading after editing `.env` | Backend must be restarted after changes to `.env` |
| Wrong working directory when starting uvicorn | Must `cd backend` first, then run `uvicorn main:app --reload` |
| Git push failed with "src refspec main does not match" | Local branch was `master` — pushed with `git push -u origin master` |

---

## Conclusion

The project resulted in a fully working web application that displays real-time flight data from all 10 Swedish airports managed by Swedavia. Users can view arrivals, departures, and search for specific flight numbers by date and airport.

### What was achieved
- A secure full-stack web app (React + FastAPI) connected to a live external API
- API key protection using environment variables and a backend proxy
- Clean, responsive UI with dark mode support
- Project published on GitHub with a clear README

### What was learned
- How to work with external REST APIs and handle authentication headers
- How to structure a full-stack project with a separate frontend and backend
- How to protect secrets using `.env` files and why it matters
- How to use Git for version control and publish to GitHub

### What could be improved
- Add auto-refresh so flight data updates without manually clicking Search
- Add filtering by airline or status
- Deploy the app online (e.g. frontend on Vercel, backend on Render) so it works without running locally
- Support more airports across Europe using a different API (e.g. AviationStack or OpenSky)
