import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import EmployeeList from '../components/EmployeeList.vue'

// Mock del modulo api
vi.mock('@/api', () => ({
  fetchAPI: vi.fn(),
  deleteEmployee: vi.fn(),
}))

import { fetchAPI, deleteEmployee } from '@/api'

const mockEmployees = {
  count: 2,
  results: [
    {
      id: 1,
      first_name: 'Mario',
      last_name: 'Rossi',
      email: 'mario@test.com',
      role: 'employee',
      department: 'Sales',
      hire_date: '2024-01-15',
    },
    {
      id: 2,
      first_name: 'Giulia',
      last_name: 'Bianchi',
      email: 'giulia@test.com',
      role: 'manager',
      department: 'Engineering',
      hire_date: '2023-06-01',
    },
  ],
}

// createMemoryHistory NON fa navigazione iniziale —
// serve un push esplicito perché router.isReady() risolva.
function createTestRouter(query = {}) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div />' } },
      { path: '/employees/:id/edit', component: { template: '<div />' } },
    ],
  })
  router.push({ path: '/', query })
  return router
}

async function mountList(query = {}) {
  fetchAPI.mockResolvedValue(mockEmployees)
  const router = createTestRouter(query)
  await router.isReady()
  const wrapper = mount(EmployeeList, {
    global: { plugins: [router] },
  })
  await flushPromises()
  return wrapper
}

describe('EmployeeList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders employee rows', async () => {
    const wrapper = await mountList()
    const rows = wrapper.findAll('tbody tr')
    expect(rows).toHaveLength(2)
    expect(wrapper.text()).toContain('Rossi, Mario')
    expect(wrapper.text()).toContain('Bianchi, Giulia')
  })

  it('shows action links for each employee', async () => {
    const wrapper = await mountList()
    const editLinks = wrapper.findAll('a[href*="/edit"]')
    expect(editLinks).toHaveLength(2)
    expect(editLinks[0].attributes('href')).toBe('/employees/1/edit')
  })

  it('shows delete buttons for each employee', async () => {
    const wrapper = await mountList()
    const eliminaButtons = wrapper.findAll('button').filter((b) => b.text() === 'Elimina')
    expect(eliminaButtons).toHaveLength(2)
  })

  it('shows confirm dialog when clicking Elimina', async () => {
    const wrapper = await mountList()
    const deleteButton = wrapper.findAll('button').find((b) => b.text() === 'Elimina')
    await deleteButton.trigger('click')

    expect(wrapper.text()).toContain('Elimina dipendente')
    expect(wrapper.text()).toContain('Vuoi eliminare Rossi, Mario')
  })

  it('deletes employee on confirm and refreshes list', async () => {
    deleteEmployee.mockResolvedValue({ data: null, error: null, status: 204 })

    const wrapper = await mountList()

    // Clicco Elimina sul primo dipendente
    const deleteButton = wrapper.findAll('button').find((b) => b.text() === 'Elimina')
    await deleteButton.trigger('click')

    // Simulo la lista aggiornata dopo delete (solo il secondo dipendente)
    fetchAPI.mockResolvedValue({
      count: 1,
      results: [mockEmployees.results[1]],
    })

    // Confermo l'eliminazione nel dialog
    const confirmBtn = wrapper.findAll('.fixed button').find((b) => b.text() === 'Elimina')
    await confirmBtn.trigger('click')
    await flushPromises()

    expect(deleteEmployee).toHaveBeenCalledWith(1)
    expect(wrapper.text()).toContain('eliminato con successo')
  })

  it('closes dialog on cancel without calling API', async () => {
    const wrapper = await mountList()

    const deleteButton = wrapper.findAll('button').find((b) => b.text() === 'Elimina')
    await deleteButton.trigger('click')

    // Clicco Annulla
    const cancelBtn = wrapper.findAll('.fixed button').find((b) => b.text() === 'Annulla')
    await cancelBtn.trigger('click')

    expect(deleteEmployee).not.toHaveBeenCalled()
    expect(wrapper.find('.fixed').exists()).toBe(false)
  })

  it('displays success message from query string', async () => {
    const wrapper = await mountList({ message: 'Dipendente creato con successo.' })
    expect(wrapper.text()).toContain('Dipendente creato con successo.')
  })

  it('shows error state on fetch failure', async () => {
    fetchAPI.mockRejectedValue(new Error('Network error'))
    const router = createTestRouter()
    await router.isReady()
    const wrapper = mount(EmployeeList, {
      global: { plugins: [router] },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('Errore nel caricamento dei dipendenti.')
  })
})
