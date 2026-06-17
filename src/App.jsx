import { useState, useEffect, useCallback } from 'react'
import { getAirports, getArrivals, getDepartures, searchFlight } from './api'
import './App.css'

const TODAY = new Date().toISOString().slice(0, 10)

function formatTime(utcStr) {
  if (!utcStr) return '—'
  try {
    return new Date(utcStr).toLocaleTimeString('sv-SE', {
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'Europe/Stockholm',
    })
  } catch {
    return utcStr
  }
}

function statusClass(status) {
  if (!status) return ''
  const s = status.toLowerCase()
  if (s.includes('land') || s.includes('arr') || s.includes('dep')) return 'status-ok'
  if (s.includes('delay') || s.includes('late'))                      return 'status-warn'
  if (s.includes('cancel'))                                            return 'status-error'
  return ''
}

function FlightTable({ flights, type }) {
  if (!flights.length) return <p className="empty">No flights found.</p>

  return (
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Flight</th>
            <th>Airline</th>
            <th>{type === 'arrivals' ? 'From' : 'To'}</th>
            <th>Scheduled</th>
            <th>Estimated</th>
            <th>Actual</th>
            <th>Terminal</th>
            <th>Gate</th>
            {type === 'arrivals' && <th>Baggage</th>}
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {flights.map((f, i) => {
            const time    = f.arrivalTime || f.departureTime || {}
            const loc     = f.locationAndStatus || {}
            const airline = f.airlineOperator || {}
            const dest    = type === 'arrivals'
              ? (f.departureAirportEnglish || '—')
              : (f.arrivalAirportEnglish   || '—')

            return (
              <tr key={i}>
                <td><strong>{f.flightId || '—'}</strong></td>
                <td>{airline.name || '—'}</td>
                <td>{dest}</td>
                <td>{formatTime(time.scheduledUtc)}</td>
                <td>{formatTime(time.estimatedUtc)}</td>
                <td>{formatTime(time.actualUtc)}</td>
                <td>{loc.terminal || '—'}</td>
                <td>{loc.gate     || '—'}</td>
                {type === 'arrivals' && <td>{f.baggage?.claimUnit || '—'}</td>}
                <td>
                  <span className={`badge ${statusClass(loc.flightLegStatus)}`}>
                    {loc.flightLegStatus || '—'}
                  </span>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export default function App() {
  const [airports,  setAirports]  = useState([])
  const [airport,   setAirport]   = useState('ARN')
  const [date,      setDate]      = useState(TODAY)
  const [tab,       setTab]       = useState('arrivals')   // arrivals | departures | search
  const [flights,   setFlights]   = useState([])
  const [loading,   setLoading]   = useState(false)
  const [error,     setError]     = useState(null)
  const [searchNum, setSearchNum] = useState('')

  useEffect(() => {
    getAirports().then(setAirports).catch(() => {})
  }, [])

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    setFlights([])
    try {
      let data
      if (tab === 'arrivals')   data = await getArrivals(airport, date)
      if (tab === 'departures') data = await getDepartures(airport, date)
      if (tab === 'search')     data = await searchFlight(searchNum, airport, date)
      setFlights(data || [])
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [tab, airport, date, searchNum])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (tab === 'search' && !searchNum.trim()) return
    load()
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>✈ Swedavia Flight Info</h1>
        <p className="subtitle">Real-time flight data for Swedish airports</p>
      </header>

      {/* Tabs */}
      <nav className="tabs">
        {['arrivals', 'departures', 'search'].map(t => (
          <button
            key={t}
            className={`tab ${tab === t ? 'active' : ''}`}
            onClick={() => { setTab(t); setFlights([]); setError(null) }}
          >
            {t === 'arrivals'   && '🛬 Arrivals'}
            {t === 'departures' && '🛫 Departures'}
            {t === 'search'     && '🔍 Search Flight'}
          </button>
        ))}
      </nav>

      {/* Form */}
      <form className="search-form" onSubmit={handleSubmit}>
        <div className="form-row">
          <label>
            Airport
            <select value={airport} onChange={e => setAirport(e.target.value)}>
              {airports.map(a => (
                <option key={a.code} value={a.code}>{a.code} — {a.name}</option>
              ))}
            </select>
          </label>

          <label>
            Date
            <input
              type="date"
              value={date}
              onChange={e => setDate(e.target.value)}
              required
            />
          </label>

          {tab === 'search' && (
            <label>
              Flight number
              <input
                type="text"
                placeholder="e.g. SK456"
                value={searchNum}
                onChange={e => setSearchNum(e.target.value.toUpperCase())}
                required
              />
            </label>
          )}

          <button type="submit" className="btn-search" disabled={loading}>
            {loading ? 'Loading…' : 'Search'}
          </button>
        </div>
      </form>

      {/* Results */}
      <main className="results">
        {error && <div className="error-banner">⚠ {error}</div>}
        {!loading && flights.length > 0 && (
          <p className="result-count">{flights.length} flight{flights.length !== 1 ? 's' : ''} found</p>
        )}
        {loading
          ? <div className="spinner" aria-label="Loading" />
          : <FlightTable flights={flights} type={tab} />
        }
      </main>
    </div>
  )
}
