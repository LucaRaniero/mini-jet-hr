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
  // FormData: il browser setta Content-Type automaticamente (con boundary).
  // JSON: serve settarlo noi esplicitamente.
  // Settare Content-Type manualmente su FormData ROMPE la request.
  const headers = options.body instanceof FormData
    ? {}
    : { 'Content-Type': 'application/json' }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers,
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

// --- GET singolo contratto ---
export function fetchContract(employeeId, contractId) {
  if (!employeeId) throw new Error('Employee ID is required')
  if (!contractId) throw new Error('Contract ID is required')
  return apiRequest(`/employees/${employeeId}/contracts/${contractId}/`)
}

// --- GET contratti di un dipendente ---
export function fetchContracts(employeeId) {
  if (!employeeId) throw new Error('Employee ID is required')
  return apiRequest(`/employees/${employeeId}/contracts/`)
}

/**
 * Costruisce il body per le request dei contratti.
 * Se c'è un file → FormData (multipart), altrimenti → JSON (come prima).
 */
function buildContractBody(payload, file) {
  if (!file) return JSON.stringify(payload)

  const formData = new FormData()
  for (const [key, value] of Object.entries(payload)) {
    // Salta campi vuoti/null — stessa logica del cleanup end_date
    if (value !== null && value !== undefined && value !== '') {
      formData.append(key, value)
    }
  }
  formData.append('document', file)
  return formData
}

// --- POST nuovo contratto (con file opzionale) ---
export function createContract(employeeId, payload, file = null) {
  if (!employeeId) throw new Error('Employee ID is required')
  return apiRequest(`/employees/${employeeId}/contracts/`, {
    method: 'POST',
    body: buildContractBody(payload, file),
  })
}

// --- PATCH aggiornamento parziale contratto (con file opzionale) ---
export function updateContract(employeeId, contractId, payload, file = null) {
  if (!employeeId) throw new Error('Employee ID is required')
  if (!contractId) throw new Error('Contract ID is required')
  return apiRequest(`/employees/${employeeId}/contracts/${contractId}/`, {
    method: 'PATCH',
    body: buildContractBody(payload, file),
  })
}

// --- DELETE (hard delete) contratto ---
export function deleteContract(employeeId, contractId) {
  if (!employeeId) throw new Error('Employee ID is required')
  if (!contractId) throw new Error('Contract ID is required')
  return apiRequest(`/employees/${employeeId}/contracts/${contractId}/`, {
    method: 'DELETE',
  })
}

// ===================== Onboarding Templates =====================

// --- GET lista template attivi ---
export function fetchOnboardingTemplates() {
  return apiRequest('/onboarding-templates/')
}

// --- GET singolo template ---
export function fetchOnboardingTemplate(id) {
  return apiRequest(`/onboarding-templates/${id}/`)
}

// --- POST nuovo template ---
export function createOnboardingTemplate(payload) {
  return apiRequest('/onboarding-templates/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

// --- PATCH aggiornamento template ---
export function updateOnboardingTemplate(id, payload) {
  return apiRequest(`/onboarding-templates/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

// --- DELETE (soft delete) template ---
export function deleteOnboardingTemplate(id) {
  return apiRequest(`/onboarding-templates/${id}/`, {
    method: 'DELETE',
  })
}

// ===================== Onboarding Steps =====================

// --- GET step di onboarding per un dipendente ---
export function fetchOnboardingSteps(employeeId) {
  if (!employeeId) throw new Error('Employee ID is required')
  return apiRequest(`/employees/${employeeId}/onboarding/`)
}

// --- POST avvia onboarding (bulk create da template attivi, no body) ---
export function startOnboarding(employeeId) {
  if (!employeeId) throw new Error('Employee ID is required')
  return apiRequest(`/employees/${employeeId}/onboarding/`, {
    method: 'POST',
    body: JSON.stringify({}),
  })
}

// --- PATCH toggle completamento step ---
export function updateOnboardingStep(employeeId, stepId, payload) {
  if (!employeeId) throw new Error('Employee ID is required')
  if (!stepId) throw new Error('Step ID is required')
  return apiRequest(`/employees/${employeeId}/onboarding/${stepId}/`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}
