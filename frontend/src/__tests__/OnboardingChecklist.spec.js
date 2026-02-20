import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import OnboardingChecklist from '@/components/OnboardingChecklist.vue'

// Mock API
vi.mock('@/api', () => ({
  fetchEmployee: vi.fn(),
  fetchOnboardingSteps: vi.fn(),
  startOnboarding: vi.fn(),
  updateOnboardingStep: vi.fn(),
}))

import {
  fetchEmployee,
  fetchOnboardingSteps,
  startOnboarding,
  updateOnboardingStep,
} from '@/api'

const mockEmployee = {
  id: 1,
  first_name: 'Mario',
  last_name: 'Rossi',
  email: 'mario@test.com',
}

const mockSteps = [
  {
    id: 10,
    template: 1,
    template_name: 'Firma contratto',
    template_description: 'Firmare tutti i documenti.',
    is_completed: false,
    completed_at: null,
  },
  {
    id: 11,
    template: 2,
    template_name: 'Setup email',
    template_description: '',
    is_completed: true,
    completed_at: '2026-02-15T10:00:00Z',
  },
  {
    id: 12,
    template: 3,
    template_name: 'Training sicurezza',
    template_description: 'Completare il corso online.',
    is_completed: false,
    completed_at: null,
  },
]

function createTestRouter() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div />' } },
      { path: '/employees/:employeeId/onboarding', component: { template: '<div />' } },
      { path: '/employees/:employeeId/contracts', component: { template: '<div />' } },
    ],
  })
  router.push('/employees/1/onboarding')
  return router
}

async function mountChecklist(stepsData = mockSteps) {
  fetchEmployee.mockResolvedValue({ data: mockEmployee, error: null, status: 200 })
  fetchOnboardingSteps.mockResolvedValue({
    data: { results: stepsData },
    error: null,
    status: 200,
  })

  const router = createTestRouter()
  await router.isReady()

  const wrapper = mount(OnboardingChecklist, {
    props: { employeeId: 1 },
    global: { plugins: [router] },
  })

  await flushPromises()
  return wrapper
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('OnboardingChecklist', () => {
  describe('with steps', () => {
    it('shows employee name in header', async () => {
      const wrapper = await mountChecklist()
      expect(wrapper.text()).toContain('Rossi, Mario')
    })

    it('renders all 3 steps', async () => {
      const wrapper = await mountChecklist()
      expect(wrapper.text()).toContain('Firma contratto')
      expect(wrapper.text()).toContain('Setup email')
      expect(wrapper.text()).toContain('Training sicurezza')
    })

    it('shows progress bar with correct count', async () => {
      const wrapper = await mountChecklist()
      // 1 out of 3 completed
      expect(wrapper.text()).toContain('1 / 3')
      expect(wrapper.text()).toContain('33%')
    })

    it('shows template description when available', async () => {
      const wrapper = await mountChecklist()
      expect(wrapper.text()).toContain('Firmare tutti i documenti.')
      expect(wrapper.text()).toContain('Completare il corso online.')
    })

    it('applies line-through to completed steps', async () => {
      const wrapper = await mountChecklist()
      // "Setup email" is completed → should have line-through class
      const completedSpan = wrapper.findAll('span').find((s) => s.text() === 'Setup email')
      expect(completedSpan.classes()).toContain('line-through')
    })

    it('shows completed_at date for completed steps', async () => {
      const wrapper = await mountChecklist()
      // completed_at: '2026-02-15T10:00:00Z' → should show date
      expect(wrapper.text()).toMatch(/15\/2\/2026|15\/02\/2026/)
    })

    it('does not show "Onboarding completato" badge when not all done', async () => {
      const wrapper = await mountChecklist()
      expect(wrapper.text()).not.toContain('Onboarding completato')
    })

    it('shows "Onboarding completato" badge when all steps done', async () => {
      const allDone = mockSteps.map((s) => ({
        ...s,
        is_completed: true,
        completed_at: '2026-02-15T10:00:00Z',
      }))
      const wrapper = await mountChecklist(allDone)
      expect(wrapper.text()).toContain('Onboarding completato')
      expect(wrapper.text()).toContain('100%')
    })

    it('calls updateOnboardingStep when checkbox clicked', async () => {
      updateOnboardingStep.mockResolvedValue({
        data: { ...mockSteps[0], is_completed: true, completed_at: '2026-02-20T10:00:00Z' },
        error: null,
        status: 200,
      })

      const wrapper = await mountChecklist()

      // Click the first checkbox (Firma contratto, currently unchecked)
      const checkboxes = wrapper.findAll('input[type="checkbox"]')
      await checkboxes[0].trigger('click')
      await flushPromises()

      expect(updateOnboardingStep).toHaveBeenCalledWith(1, 10, { is_completed: true })
    })
  })

  describe('without steps (not started)', () => {
    it('shows "Avvia Onboarding" button', async () => {
      const wrapper = await mountChecklist([])
      expect(wrapper.text()).toContain('Avvia Onboarding')
      expect(wrapper.text()).toContain('non è ancora stato avviato')
    })

    it('calls startOnboarding on button click', async () => {
      // Fresh steps: tutti non completati (come li creerebbe il backend)
      const freshSteps = mockSteps.map((s) => ({
        ...s,
        is_completed: false,
        completed_at: null,
      }))
      startOnboarding.mockResolvedValue({
        data: freshSteps,
        error: null,
        status: 201,
      })

      const wrapper = await mountChecklist([])

      const startBtn = wrapper.find('button')
      await startBtn.trigger('click')
      await flushPromises()

      expect(startOnboarding).toHaveBeenCalledWith(1)
      // After start, steps should appear — tutti non completati
      expect(wrapper.text()).toContain('Firma contratto')
      expect(wrapper.text()).toContain('0 / 3')
    })
  })

  it('shows navigation links', async () => {
    const wrapper = await mountChecklist()
    expect(wrapper.text()).toContain('Contratti')
    expect(wrapper.text()).toContain('Lista dipendenti')
  })
})
