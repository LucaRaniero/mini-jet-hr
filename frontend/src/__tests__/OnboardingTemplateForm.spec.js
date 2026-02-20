import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import OnboardingTemplateForm from '@/components/OnboardingTemplateForm.vue'

// Mock API
vi.mock('@/api', () => ({
  createOnboardingTemplate: vi.fn(),
  updateOnboardingTemplate: vi.fn(),
}))

import { createOnboardingTemplate, updateOnboardingTemplate } from '@/api'

function createTestRouter() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div />' } },
      { path: '/onboarding/templates', component: { template: '<div />' } },
      { path: '/onboarding/templates/new', component: { template: '<div />' } },
    ],
  })
  router.push('/')
  return router
}

async function mountForm(props = {}) {
  const router = createTestRouter()
  await router.isReady()
  return mount(OnboardingTemplateForm, {
    props,
    global: { plugins: [router] },
  })
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('OnboardingTemplateForm', () => {
  describe('create mode', () => {
    it('shows "Nuovo Template" title when no template prop', async () => {
      const wrapper = await mountForm()
      expect(wrapper.text()).toContain('Nuovo Template')
    })

    it('has empty default values', async () => {
      const wrapper = await mountForm()
      expect(wrapper.find('#name').element.value).toBe('')
      expect(wrapper.find('#description').element.value).toBe('')
      expect(wrapper.find('#order').element.value).toBe('0')
    })

    it('calls createOnboardingTemplate on submit and emits saved', async () => {
      createOnboardingTemplate.mockResolvedValue({
        data: { id: 1, name: 'Test', description: '', order: 1 },
        error: null,
        status: 201,
      })

      const wrapper = await mountForm()

      await wrapper.find('#name').setValue('Firma contratto')
      await wrapper.find('#description').setValue('Firmare tutti i documenti.')
      await wrapper.find('#order').setValue('1')

      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(createOnboardingTemplate).toHaveBeenCalledWith({
        name: 'Firma contratto',
        description: 'Firmare tutti i documenti.',
        order: 1,
      })
      expect(wrapper.emitted('saved')).toBeTruthy()
    })

    it('shows validation errors from server', async () => {
      createOnboardingTemplate.mockResolvedValue({
        data: null,
        error: { name: ['Questo campo è obbligatorio.'] },
        status: 400,
      })

      const wrapper = await mountForm()
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(wrapper.text()).toContain('Questo campo è obbligatorio.')
    })
  })

  describe('edit mode', () => {
    const existingTemplate = {
      id: 5,
      name: 'Setup email',
      description: 'Configurare email aziendale.',
      order: 2,
    }

    it('shows "Modifica Template" title', async () => {
      const wrapper = await mountForm({ template: existingTemplate })
      expect(wrapper.text()).toContain('Modifica Template')
    })

    it('pre-fills form with template data', async () => {
      const wrapper = await mountForm({ template: existingTemplate })
      expect(wrapper.find('#name').element.value).toBe('Setup email')
      expect(wrapper.find('#description').element.value).toBe('Configurare email aziendale.')
      expect(wrapper.find('#order').element.value).toBe('2')
    })

    it('calls updateOnboardingTemplate on submit', async () => {
      updateOnboardingTemplate.mockResolvedValue({
        data: { ...existingTemplate, name: 'Setup email aggiornato' },
        error: null,
        status: 200,
      })

      const wrapper = await mountForm({ template: existingTemplate })
      await wrapper.find('#name').setValue('Setup email aggiornato')
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(updateOnboardingTemplate).toHaveBeenCalledWith(5, {
        name: 'Setup email aggiornato',
        description: 'Configurare email aziendale.',
        order: 2,
      })
      expect(wrapper.emitted('saved')).toBeTruthy()
    })
  })

  it('disables submit button while submitting', async () => {
    // Never-resolving promise to keep submitting=true
    createOnboardingTemplate.mockReturnValue(new Promise(() => {}))

    const wrapper = await mountForm()
    await wrapper.find('#name').setValue('Test')
    await wrapper.find('form').trigger('submit')

    const submitBtn = wrapper.find('button[type="submit"]')
    expect(submitBtn.element.disabled).toBe(true)
    expect(submitBtn.text()).toBe('Salvataggio...')
  })

  it('has Annulla link to template list', async () => {
    const wrapper = await mountForm()
    const cancelLink = wrapper.findAll('a').find((a) => a.text() === 'Annulla')
    expect(cancelLink.attributes('href')).toBe('/onboarding/templates')
  })
})
