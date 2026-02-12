const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export async function fetchAPI(endpoint) {
  const response = await fetch(`${API_BASE}${endpoint}`)
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  return response.json()
}
