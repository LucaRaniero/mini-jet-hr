import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import EmployeeForm from '../components/EmployeeForm.vue'

// Mock dell'intero modulo api
vi.mock('@/api', () => ({
  createEmployee: vi.fn(),
  updateEmployee: vi.fn(),
}))

import { createEmployee, updateEmployee } from '@/api'

function createTestRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/', component: { template: '<div />' } }],
  })
}

function mountForm(props = {}) {
  return mount(EmployeeForm, {
    props,
    global: { plugins: [createTestRouter()] },
  })
}

describe('EmployeeForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // --- Modalità CREATE ---
  describe('create mode', () => {
    it('shows "Nuovo Dipendente" title when no employee prop', () => {
      const wrapper = mountForm()
      expect(wrapper.text()).toContain('Nuovo Dipendente')
    })

    it('has email field enabled', () => {
      const wrapper = mountForm()
      const email = wrapper.find('#email')
      expect(email.element.disabled).toBe(false)
    })

    it('calls createEmployee and emits saved on success', async () => {
      const mockResult = { data: { id: 1, first_name: 'Mario' }, error: null, status: 201 }
      createEmployee.mockResolvedValue(mockResult)

      const wrapper = mountForm()

      // Compilo il form
      await wrapper.find('#first_name').setValue('Mario')
      await wrapper.find('#last_name').setValue('Rossi')
      await wrapper.find('#email').setValue('mario@test.com')
      await wrapper.find('#hire_date').setValue('2024-01-15')

      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(createEmployee).toHaveBeenCalledWith({
        first_name: 'Mario',
        last_name: 'Rossi',
        email: 'mario@test.com',
        role: 'employee',
        department: '',
        hire_date: '2024-01-15',
      })
      expect(wrapper.emitted('saved')).toBeTruthy()
    })

    it('displays server validation errors per field', async () => {
      createEmployee.mockResolvedValue({
        data: null,
        error: { email: ['Questo campo deve essere unico.'] },
        status: 400,
      })

      const wrapper = mountForm()
      await wrapper.find('#first_name').setValue('Mario')
      await wrapper.find('#last_name').setValue('Rossi')
      await wrapper.find('#email').setValue('duplicato@test.com')
      await wrapper.find('#hire_date').setValue('2024-01-15')

      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(wrapper.text()).toContain('Questo campo deve essere unico.')
      expect(wrapper.emitted('saved')).toBeFalsy()
    })
  })

  // --- Modalità EDIT ---
  describe('edit mode', () => {
    const employee = {
      id: 5,
      first_name: 'Giulia',
      last_name: 'Bianchi',
      email: 'giulia@test.com',
      role: 'manager',
      department: 'Engineering',
      hire_date: '2023-06-01',
    }

    it('shows "Modifica Dipendente" title', () => {
      const wrapper = mountForm({ employee })
      expect(wrapper.text()).toContain('Modifica Dipendente')
    })

    it('pre-fills form with employee data', () => {
      const wrapper = mountForm({ employee })
      expect(wrapper.find('#first_name').element.value).toBe('Giulia')
      expect(wrapper.find('#last_name').element.value).toBe('Bianchi')
      expect(wrapper.find('#email').element.value).toBe('giulia@test.com')
      expect(wrapper.find('#role').element.value).toBe('manager')
      expect(wrapper.find('#department').element.value).toBe('Engineering')
      expect(wrapper.find('#hire_date').element.value).toBe('2023-06-01')
    })

    it('has email field disabled', () => {
      const wrapper = mountForm({ employee })
      expect(wrapper.find('#email').element.disabled).toBe(true)
    })

    it('calls updateEmployee WITHOUT email in payload', async () => {
      const mockResult = { data: { ...employee }, error: null, status: 200 }
      updateEmployee.mockResolvedValue(mockResult)

      const wrapper = mountForm({ employee })

      // Modifico il nome
      await wrapper.find('#first_name').setValue('Giuliana')

      await wrapper.find('form').trigger('submit')
      await flushPromises()

      // Verifica: email NON è nel payload
      expect(updateEmployee).toHaveBeenCalledWith(5, {
        first_name: 'Giuliana',
        last_name: 'Bianchi',
        role: 'manager',
        department: 'Engineering',
        hire_date: '2023-06-01',
      })
      expect(wrapper.emitted('saved')).toBeTruthy()
    })
  })

  // --- Stato submit ---
  it('disables submit button while submitting', async () => {
    // createEmployee che non risolve mai (simula latenza)
    createEmployee.mockReturnValue(new Promise(() => {}))

    const wrapper = mountForm()
    await wrapper.find('#first_name').setValue('Test')
    await wrapper.find('#last_name').setValue('Test')
    await wrapper.find('#email').setValue('test@test.com')
    await wrapper.find('#hire_date').setValue('2024-01-01')

    await wrapper.find('form').trigger('submit')

    const button = wrapper.find('button[type="submit"]')
    expect(button.element.disabled).toBe(true)
    expect(button.text()).toContain('Salvataggio...')
  })
})
