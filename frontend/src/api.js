const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

/**
 * Base request — gestisce tutti i casi HTTP in modo uniforme.
 *
 * Ritorna: { data, error, status }
 *   - Successo (2xx):  { data: body,  error: null, status }
 *   - Validazione (400): { data: null, error: { field: [msgs] }, status: 400 }
 *   - 204 No Content:    { data: null, error: null, status: 204 }
 *   - Altro errore:      throw Error
 */
async function apiRequest(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (response.status === 204) {
    return { data: null, error: null, status: 204 }
  }

  const body = await response.json()

  if (response.ok) {
    return { data: body, error: null, status: response.status }
  }

  if (response.status === 400) {
    return { data: null, error: body, status: 400 }
  }

  throw new Error(`HTTP ${response.status}`)
}

// --- GET (lista paginata) — usato da EmployeeList ---
export async function fetchAPI(endpoint) {
  const response = await fetch(`${API_BASE}${endpoint}`)
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  return response.json()
}

// --- GET singolo dipendente ---
export function fetchEmployee(id) {
  return apiRequest(`/employees/${id}/`)
}

// --- POST nuovo dipendente ---
export function createEmployee(payload) {
  return apiRequest('/employees/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

// --- PATCH aggiornamento parziale ---
export function updateEmployee(id, payload) {
  return apiRequest(`/employees/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

// --- DELETE (soft delete) ---
export function deleteEmployee(id) {
  return apiRequest(`/employees/${id}/`, {
    method: 'DELETE',
  })
}
