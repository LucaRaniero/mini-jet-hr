import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import ContractList from '../components/ContractList.vue'

// Mock del modulo api — solo le funzioni usate da ContractList
vi.mock('@/api', () => ({
  fetchEmployee: vi.fn(),
  fetchContracts: vi.fn(),
  deleteContract: vi.fn(),
}))

import { fetchEmployee, fetchContracts, deleteContract } from '@/api'

const mockEmployee = {
  id: 1,
  first_name: 'Mario',
  last_name: 'Rossi',
  email: 'mario@test.com',
}

const mockContracts = {
  count: 2,
  results: [
    {
      id: 10,
      employee: 1,
      contract_type: 'indeterminato',
      ccnl: 'metalmeccanico',
      ral: '35000.00',
      start_date: '2024-01-15',
      end_date: null,
      document_url: 'http://localhost:8000/media/contracts/2026/02/contratto.pdf',
    },
    {
      id: 11,
      employee: 1,
      contract_type: 'determinato',
      ccnl: 'commercio',
      ral: '28000.00',
      start_date: '2023-01-01',
      end_date: '2023-12-31',
      document_url: null,
    },
  ],
}

// Route minime per risolvere i RouterLink nel template
function createTestRouter(query = {}) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div />' } },
      { path: '/employees/:employeeId/contracts', name: 'contract-list', component: { template: '<div />' } },
      { path: '/employees/:employeeId/contracts/new', component: { template: '<div />' } },
      { path: '/employees/:employeeId/contracts/:contractId/edit', component: { template: '<div />' } },
    ],
  })
  // Push alla route dei contratti per impostare route.params e query
  router.push({ path: '/employees/1/contracts', query })
  return router
}

async function mountList(query = {}) {
  // fetchEmployee e fetchContracts restituiscono { data, error, status }
  // perché usano apiRequest (diverso da fetchAPI usato in EmployeeList)
  fetchEmployee.mockResolvedValue({ data: mockEmployee, error: null, status: 200 })
  fetchContracts.mockResolvedValue({ data: mockContracts, error: null, status: 200 })

  const router = createTestRouter(query)
  await router.isReady()
  const wrapper = mount(ContractList, {
    props: { employeeId: 1 },
    global: { plugins: [router] },
  })
  await flushPromises()
  return wrapper
}

describe('ContractList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders contract rows', async () => {
    const wrapper = await mountList()
    const rows = wrapper.findAll('tbody tr')
    expect(rows).toHaveLength(2)
  })

  it('shows employee name in header', async () => {
    const wrapper = await mountList()
    expect(wrapper.text()).toContain('Contratti di Rossi, Mario')
  })

  it('shows active badge for contract without end_date', async () => {
    const wrapper = await mountList()
    const badges = wrapper.findAll('.rounded-full')
    // Primo contratto: end_date null → Attivo
    expect(badges[0].text()).toBe('Attivo')
    expect(badges[0].classes()).toContain('bg-green-100')
  })

  it('shows closed badge for contract with end_date', async () => {
    const wrapper = await mountList()
    const badges = wrapper.findAll('.rounded-full')
    // Secondo contratto: end_date set → Chiuso
    expect(badges[1].text()).toBe('Chiuso')
    expect(badges[1].classes()).toContain('bg-gray-100')
  })

  it('formats RAL as currency', async () => {
    const wrapper = await mountList()
    // Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' })
    // 35000 → qualcosa come "35.000,00 €" o "€ 35.000,00"
    expect(wrapper.text()).toMatch(/35\.000/)
  })

  it('shows action links for each contract', async () => {
    const wrapper = await mountList()
    const editLinks = wrapper.findAll('a[href*="/edit"]')
    expect(editLinks).toHaveLength(2)
    expect(editLinks[0].attributes('href')).toBe('/employees/1/contracts/10/edit')
  })

  it('shows confirm dialog when clicking Elimina', async () => {
    const wrapper = await mountList()
    const deleteButton = wrapper.findAll('button').find((b) => b.text() === 'Elimina')
    await deleteButton.trigger('click')

    expect(wrapper.text()).toContain('Elimina contratto')
    expect(wrapper.text()).toContain('irreversibile')
  })

  it('deletes contract on confirm and refreshes list', async () => {
    deleteContract.mockResolvedValue({ data: null, error: null, status: 204 })

    const wrapper = await mountList()

    const deleteButton = wrapper.findAll('button').find((b) => b.text() === 'Elimina')
    await deleteButton.trigger('click')

    // Mock lista aggiornata dopo delete
    fetchContracts.mockResolvedValue({
      data: { count: 1, results: [mockContracts.results[1]] },
      error: null,
      status: 200,
    })

    const confirmBtn = wrapper.findAll('.fixed button').find((b) => b.text() === 'Elimina')
    await confirmBtn.trigger('click')
    await flushPromises()

    expect(deleteContract).toHaveBeenCalledWith(1, 10)
    expect(wrapper.text()).toContain('eliminato con successo')
  })

  it('closes dialog on cancel without calling API', async () => {
    const wrapper = await mountList()

    const deleteButton = wrapper.findAll('button').find((b) => b.text() === 'Elimina')
    await deleteButton.trigger('click')

    const cancelBtn = wrapper.findAll('.fixed button').find((b) => b.text() === 'Annulla')
    await cancelBtn.trigger('click')

    expect(deleteContract).not.toHaveBeenCalled()
    expect(wrapper.find('.fixed').exists()).toBe(false)
  })

  it('shows success message from query string', async () => {
    const wrapper = await mountList({ message: 'Contratto creato con successo.' })
    expect(wrapper.text()).toContain('Contratto creato con successo.')
  })

  it('shows Visualizza link when document_url exists', async () => {
    const wrapper = await mountList()
    // Primo contratto ha document_url
    const pdfLinks = wrapper.findAll('a[target="_blank"]')
    expect(pdfLinks.length).toBeGreaterThanOrEqual(1)
    expect(pdfLinks[0].text()).toBe('Visualizza')
    expect(pdfLinks[0].attributes('href')).toBe(
      'http://localhost:8000/media/contracts/2026/02/contratto.pdf',
    )
  })

  it('shows dash when document_url is null', async () => {
    const wrapper = await mountList()
    const rows = wrapper.findAll('tbody tr')
    // Secondo contratto (index 1) non ha document → mostra "—"
    const pdfCell = rows[1].findAll('td')[6] // colonna PDF (index 6, 0-based)
    expect(pdfCell.text()).toBe('—')
  })

  it('shows empty state when no contracts', async () => {
    fetchEmployee.mockResolvedValue({ data: mockEmployee, error: null, status: 200 })
    fetchContracts.mockResolvedValue({ data: { count: 0, results: [] }, error: null, status: 200 })

    const router = createTestRouter()
    await router.isReady()
    const wrapper = mount(ContractList, {
      props: { employeeId: 1 },
      global: { plugins: [router] },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('Nessun contratto trovato')
  })

  it('shows error state on fetch failure', async () => {
    fetchEmployee.mockRejectedValue(new Error('Network error'))
    fetchContracts.mockRejectedValue(new Error('Network error'))

    const router = createTestRouter()
    await router.isReady()
    const wrapper = mount(ContractList, {
      props: { employeeId: 1 },
      global: { plugins: [router] },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('Errore nel caricamento dei contratti.')
  })
})
