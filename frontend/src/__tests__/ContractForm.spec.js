import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import ContractForm from '../components/ContractForm.vue'

vi.mock('@/api', () => ({
  createContract: vi.fn(),
  updateContract: vi.fn(),
}))

import { createContract, updateContract } from '@/api'

function createTestRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div />' } },
      { path: '/employees/:employeeId/contracts', component: { template: '<div />' } },
    ],
  })
}

function mountForm(props = {}) {
  return mount(ContractForm, {
    props: { employeeId: 1, ...props },
    global: { plugins: [createTestRouter()] },
  })
}

describe('ContractForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // --- Modalità CREATE ---
  describe('create mode', () => {
    it('shows "Nuovo Contratto" title when no contract prop', () => {
      const wrapper = mountForm()
      expect(wrapper.text()).toContain('Nuovo Contratto')
    })

    it('has default values for dropdowns', () => {
      const wrapper = mountForm()
      expect(wrapper.find('#contract_type').element.value).toBe('indeterminato')
      expect(wrapper.find('#ccnl').element.value).toBe('metalmeccanico')
    })

    it('end_date field is not required', () => {
      const wrapper = mountForm()
      expect(wrapper.find('#end_date').element.required).toBe(false)
    })

    it('calls createContract with employeeId and emits saved', async () => {
      const mockResult = {
        data: { id: 10, contract_type: 'indeterminato', ral: '35000.00' },
        error: null,
        status: 201,
      }
      createContract.mockResolvedValue(mockResult)

      const wrapper = mountForm()

      await wrapper.find('#ral').setValue('35000')
      await wrapper.find('#start_date').setValue('2024-01-15')

      await wrapper.find('form').trigger('submit')
      await flushPromises()

      // Verifica: employeeId, payload, file (null = nessun file selezionato)
      // Nota: type="number" + v-model converte a Number (non stringa)
      // end_date vuoto viene rimosso dal payload (testato a parte)
      expect(createContract).toHaveBeenCalledWith(1, {
        contract_type: 'indeterminato',
        ccnl: 'metalmeccanico',
        ral: 35000,
        start_date: '2024-01-15',
      }, null)
      expect(wrapper.emitted('saved')).toBeTruthy()
    })

    it('strips empty end_date from payload', async () => {
      createContract.mockResolvedValue({
        data: { id: 10 },
        error: null,
        status: 201,
      })

      const wrapper = mountForm()
      await wrapper.find('#ral').setValue('30000')
      await wrapper.find('#start_date').setValue('2024-01-01')
      // end_date lasciato vuoto

      await wrapper.find('form').trigger('submit')
      await flushPromises()

      // Il payload NON deve contenere end_date (viene rimosso se vuoto)
      const payload = createContract.mock.calls[0][1]
      expect(payload).not.toHaveProperty('end_date')
    })

    it('displays server validation errors per field', async () => {
      createContract.mockResolvedValue({
        data: null,
        error: { ral: ['Assicurati che questo valore sia maggiore o uguale a 0.'] },
        status: 400,
      })

      const wrapper = mountForm()
      await wrapper.find('#ral').setValue('-1000')
      await wrapper.find('#start_date').setValue('2024-01-01')

      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(wrapper.text()).toContain('Assicurati che questo valore sia maggiore o uguale a 0.')
      expect(wrapper.emitted('saved')).toBeFalsy()
    })
  })

  // --- Modalità EDIT ---
  describe('edit mode', () => {
    const contract = {
      id: 10,
      employee: 1,
      contract_type: 'determinato',
      ccnl: 'commercio',
      ral: '28000.00',
      start_date: '2023-01-01',
      end_date: '2023-12-31',
    }

    it('shows "Modifica Contratto" title', () => {
      const wrapper = mountForm({ contract })
      expect(wrapper.text()).toContain('Modifica Contratto')
    })

    it('pre-fills form with contract data', () => {
      const wrapper = mountForm({ contract })
      expect(wrapper.find('#contract_type').element.value).toBe('determinato')
      expect(wrapper.find('#ccnl').element.value).toBe('commercio')
      expect(wrapper.find('#ral').element.value).toBe('28000.00')
      expect(wrapper.find('#start_date').element.value).toBe('2023-01-01')
      expect(wrapper.find('#end_date').element.value).toBe('2023-12-31')
    })

    it('calls updateContract with employeeId, contractId, and payload', async () => {
      updateContract.mockResolvedValue({
        data: { ...contract, ral: '30000.00' },
        error: null,
        status: 200,
      })

      const wrapper = mountForm({ contract })
      await wrapper.find('#ral').setValue('30000.00')

      await wrapper.find('form').trigger('submit')
      await flushPromises()

      // Verifica: employeeId, contractId, payload, file (null)
      // type="number" converte a Number → 30000 (non "30000.00")
      expect(updateContract).toHaveBeenCalledWith(1, 10, expect.objectContaining({
        ral: 30000,
        contract_type: 'determinato',
      }), null)
      expect(wrapper.emitted('saved')).toBeTruthy()
    })
  })

  // --- File upload ---
  describe('document upload', () => {
    it('renders file input with accept=".pdf"', () => {
      const wrapper = mountForm()
      const input = wrapper.find('#document')
      expect(input.exists()).toBe(true)
      expect(input.attributes('accept')).toBe('.pdf')
    })

    it('passes file to createContract as third argument', async () => {
      createContract.mockResolvedValue({ data: { id: 10 }, error: null, status: 201 })

      const wrapper = mountForm()
      await wrapper.find('#ral').setValue('35000')
      await wrapper.find('#start_date').setValue('2024-01-15')

      // Simula la selezione di un file PDF
      const file = new File(['%PDF-dummy'], 'contratto.pdf', { type: 'application/pdf' })
      Object.defineProperty(file, 'size', { value: 1024 })
      const input = wrapper.find('#document')
      Object.defineProperty(input.element, 'files', { value: [file] })
      await input.trigger('change')

      await wrapper.find('form').trigger('submit')
      await flushPromises()

      // Terzo argomento = il file selezionato
      expect(createContract).toHaveBeenCalledWith(1, expect.any(Object), file)
    })

    it('shows validation error for non-PDF file', async () => {
      const wrapper = mountForm()
      const file = new File(['not a pdf'], 'document.txt', { type: 'text/plain' })
      Object.defineProperty(file, 'size', { value: 100 })
      const input = wrapper.find('#document')
      Object.defineProperty(input.element, 'files', { value: [file] })
      await input.trigger('change')

      expect(wrapper.text()).toContain('Solo file PDF sono accettati.')
    })

    it('shows validation error for oversized file', async () => {
      const wrapper = mountForm()
      const file = new File(['%PDF-big'], 'big.pdf', { type: 'application/pdf' })
      Object.defineProperty(file, 'size', { value: 6 * 1024 * 1024 })
      const input = wrapper.find('#document')
      Object.defineProperty(input.element, 'files', { value: [file] })
      await input.trigger('change')

      expect(wrapper.text()).toContain('Il file non può superare 5 MB.')
    })

    it('shows existing document link in edit mode', () => {
      const contract = {
        id: 10,
        employee: 1,
        contract_type: 'indeterminato',
        ccnl: 'metalmeccanico',
        ral: '35000.00',
        start_date: '2024-01-15',
        end_date: null,
        document_url: 'http://localhost:8000/media/contracts/2026/02/test.pdf',
      }
      const wrapper = mountForm({ contract })
      const link = wrapper.find('a[target="_blank"]')
      expect(link.exists()).toBe(true)
      expect(link.text()).toBe('Visualizza PDF')
      expect(link.attributes('href')).toBe('http://localhost:8000/media/contracts/2026/02/test.pdf')
    })

    it('does not show document link when no document_url', () => {
      const contract = {
        id: 10,
        employee: 1,
        contract_type: 'indeterminato',
        ccnl: 'metalmeccanico',
        ral: '35000.00',
        start_date: '2024-01-15',
        end_date: null,
        document_url: null,
      }
      const wrapper = mountForm({ contract })
      expect(wrapper.text()).not.toContain('Visualizza PDF')
    })
  })

  // --- Stato submit ---
  it('disables submit button while submitting', async () => {
    createContract.mockReturnValue(new Promise(() => {}))

    const wrapper = mountForm()
    await wrapper.find('#ral').setValue('30000')
    await wrapper.find('#start_date').setValue('2024-01-01')

    await wrapper.find('form').trigger('submit')

    const button = wrapper.find('button[type="submit"]')
    expect(button.element.disabled).toBe(true)
    expect(button.text()).toContain('Salvataggio...')
  })
})
