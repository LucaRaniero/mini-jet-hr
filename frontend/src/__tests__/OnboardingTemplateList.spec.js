import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import OnboardingTemplateList from '@/components/OnboardingTemplateList.vue'

// Mock API
vi.mock('@/api', () => ({
  fetchOnboardingTemplates: vi.fn(),
  deleteOnboardingTemplate: vi.fn(),
}))

import { fetchOnboardingTemplates, deleteOnboardingTemplate } from '@/api'

const mockTemplates = [
  { id: 1, name: 'Firma contratto', description: 'Firmare tutti i documenti.', order: 1 },
  { id: 2, name: 'Setup email', description: '', order: 2 },
  { id: 3, name: 'Training sicurezza', description: 'Completare il corso online.', order: 3 },
]

function createTestRouter(query = {}) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div />' } },
      { path: '/onboarding/templates', component: { template: '<div />' } },
      { path: '/onboarding/templates/new', component: { template: '<div />' } },
      { path: '/onboarding/templates/:id/edit', component: { template: '<div />' } },
    ],
  })
  router.push({ path: '/onboarding/templates', query })
  return router
}

async function mountList(query = {}) {
  fetchOnboardingTemplates.mockResolvedValue({
    data: { results: mockTemplates },
    error: null,
    status: 200,
  })

  const router = createTestRouter(query)
  await router.isReady()

  const wrapper = mount(OnboardingTemplateList, {
    global: { plugins: [router] },
  })

  await flushPromises()
  return wrapper
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('OnboardingTemplateList', () => {
  it('renders template table with 3 rows', async () => {
    const wrapper = await mountList()
    const rows = wrapper.findAll('tbody tr')
    expect(rows).toHaveLength(3)
  })

  it('shows template name and order in each row', async () => {
    const wrapper = await mountList()
    expect(wrapper.text()).toContain('Firma contratto')
    expect(wrapper.text()).toContain('Setup email')
    expect(wrapper.text()).toContain('Training sicurezza')
  })

  it('shows title and "Nuovo Template" button', async () => {
    const wrapper = await mountList()
    expect(wrapper.text()).toContain('Template Onboarding')
    expect(wrapper.text()).toContain('+ Nuovo Template')
  })

  it('shows empty state when no templates', async () => {
    fetchOnboardingTemplates.mockResolvedValue({
      data: { results: [] },
      error: null,
      status: 200,
    })

    const router = createTestRouter()
    await router.isReady()

    const wrapper = mount(OnboardingTemplateList, {
      global: { plugins: [router] },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('Nessun template onboarding configurato')
  })

  it('shows success message from query string', async () => {
    const wrapper = await mountList({ message: 'Template creato con successo.' })
    expect(wrapper.text()).toContain('Template creato con successo.')
  })

  it('shows delete dialog on Elimina click', async () => {
    const wrapper = await mountList()
    const deleteButton = wrapper.findAll('button').find((b) => b.text() === 'Elimina')
    await deleteButton.trigger('click')

    expect(wrapper.text()).toContain('Elimina template')
    expect(wrapper.text()).toContain('Firma contratto')
  })

  it('calls deleteOnboardingTemplate on confirm', async () => {
    deleteOnboardingTemplate.mockResolvedValue({ data: null, error: null, status: 204 })

    const wrapper = await mountList()

    // Click Elimina on first template
    const deleteButton = wrapper.findAll('button').find((b) => b.text() === 'Elimina')
    await deleteButton.trigger('click')

    // Confirm
    const confirmBtn = wrapper.findAll('.fixed button').find((b) => b.text() === 'Elimina')
    await confirmBtn.trigger('click')
    await flushPromises()

    expect(deleteOnboardingTemplate).toHaveBeenCalledWith(1)
  })

  it('cancels delete dialog on Annulla', async () => {
    const wrapper = await mountList()

    const deleteButton = wrapper.findAll('button').find((b) => b.text() === 'Elimina')
    await deleteButton.trigger('click')
    expect(wrapper.find('.fixed').exists()).toBe(true)

    const cancelBtn = wrapper.findAll('.fixed button').find((b) => b.text() === 'Annulla')
    await cancelBtn.trigger('click')
    expect(wrapper.find('.fixed').exists()).toBe(false)
  })

  it('truncates long descriptions', async () => {
    const longDesc = 'A'.repeat(100)
    fetchOnboardingTemplates.mockResolvedValue({
      data: {
        results: [{ id: 1, name: 'Test', description: longDesc, order: 1 }],
      },
      error: null,
      status: 200,
    })

    const router = createTestRouter()
    await router.isReady()
    const wrapper = mount(OnboardingTemplateList, {
      global: { plugins: [router] },
    })
    await flushPromises()

    // Description should be truncated to 80 chars + "..."
    expect(wrapper.text()).toContain('...')
    expect(wrapper.text()).not.toContain(longDesc)
  })
})
