import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const getAirports   = ()                          => api.get('/airports').then(r => r.data)
export const getArrivals   = (airport, date)             => api.get(`/arrivals/${airport}/${date}`).then(r => r.data)
export const getDepartures = (airport, date)             => api.get(`/departures/${airport}/${date}`).then(r => r.data)
export const searchFlight  = (flight, airport, date)     => api.get('/search', { params: { flight, airport, date } }).then(r => r.data)
export const heartbeat     = ()                          => api.get('/heartbeat').then(r => r.data)
