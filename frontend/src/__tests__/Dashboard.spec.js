import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import DashboardPanel from '@/components/DashboardPanel.vue'

// Mock Chart.js components — in unit test non abbiamo <canvas>,
// quindi sostituiamo Line e Doughnut con stub che espongono le props.
// È come mockare una stored procedure: verifichi i parametri, non l'esecuzione.
vi.mock('vue-chartjs', () => ({
  Line: {
    name: 'Line',
    props: ['data', 'options'],
    template: '<div class="mock-line-chart" />',
  },
  Doughnut: {
    name: 'Doughnut',
    props: ['data', 'options'],
    template: '<div class="mock-doughnut-chart" />',
  },
}))

// Mock API
vi.mock('@/api', () => ({
  fetchDashboardStats: vi.fn(),
}))

import { fetchDashboardStats } from '@/api'

const mockStats = {
  employees: { active: 42, inactive: 5, new_hires: 3 },
  contracts: { expiring: 2 },
  onboarding: { in_progress: 7 },
  charts: {
    headcount_trend: [
      { month: '2025-10', count: 5 },
      { month: '2025-11', count: 3 },
      { month: '2025-12', count: 8 },
    ],
    department_distribution: [
      { department: 'Engineering', count: 20 },
      { department: 'HR', count: 8 },
      { department: 'Sales', count: 14 },
    ],
  },
}

async function mountDashboard(statsData = mockStats) {
  fetchDashboardStats.mockResolvedValue(statsData)
  const wrapper = mount(DashboardPanel)
  await flushPromises()
  return wrapper
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('DashboardPanel', () => {
  describe('loading state', () => {
    it('shows loading message before data arrives', () => {
      // Non risolvere la promise → rimane in loading
      fetchDashboardStats.mockReturnValue(new Promise(() => {}))
      const wrapper = mount(DashboardPanel)
      expect(wrapper.text()).toContain('Caricamento dashboard...')
    })
  })

  describe('error state', () => {
    it('shows error message when API fails', async () => {
      fetchDashboardStats.mockRejectedValue(new Error('Network error'))
      const wrapper = mount(DashboardPanel)
      await flushPromises()
      expect(wrapper.text()).toContain('Errore nel caricamento della dashboard.')
    })
  })

  describe('KPI cards', () => {
    it('shows all 4 KPI cards with correct values', async () => {
      const wrapper = await mountDashboard()
      expect(wrapper.text()).toContain('Dipendenti Attivi')
      expect(wrapper.text()).toContain('42')
      expect(wrapper.text()).toContain('Nuove Assunzioni (mese)')
      expect(wrapper.text()).toContain('3')
      expect(wrapper.text()).toContain('Contratti in Scadenza')
      expect(wrapper.text()).toContain('2')
      expect(wrapper.text()).toContain('Onboarding in Corso')
      expect(wrapper.text()).toContain('7')
    })

    it('shows zero values correctly', async () => {
      const emptyStats = {
        employees: { active: 0, inactive: 0, new_hires: 0 },
        contracts: { expiring: 0 },
        onboarding: { in_progress: 0 },
        charts: { headcount_trend: [], department_distribution: [] },
      }
      const wrapper = await mountDashboard(emptyStats)
      expect(wrapper.text()).toContain('Dipendenti Attivi')
      // All values should be 0
      const cards = wrapper.findAll('.text-3xl')
      expect(cards).toHaveLength(4)
      cards.forEach((card) => {
        expect(card.text()).toBe('0')
      })
    })
  })

  describe('charts', () => {
    it('renders headcount line chart with data', async () => {
      const wrapper = await mountDashboard()
      const lineChart = wrapper.findComponent({ name: 'Line' })
      expect(lineChart.exists()).toBe(true)
      expect(lineChart.props('data').labels).toEqual(['2025-10', '2025-11', '2025-12'])
      expect(lineChart.props('data').datasets[0].data).toEqual([5, 3, 8])
    })

    it('renders department doughnut chart with data', async () => {
      const wrapper = await mountDashboard()
      const doughnutChart = wrapper.findComponent({ name: 'Doughnut' })
      expect(doughnutChart.exists()).toBe(true)
      expect(doughnutChart.props('data').labels).toEqual([
        'Engineering',
        'HR',
        'Sales',
      ])
      expect(doughnutChart.props('data').datasets[0].data).toEqual([20, 8, 14])
    })

    it('shows fallback message when headcount trend is empty', async () => {
      const noTrend = {
        ...mockStats,
        charts: { ...mockStats.charts, headcount_trend: [] },
      }
      const wrapper = await mountDashboard(noTrend)
      // Line chart should NOT render, fallback message shown instead
      const lineChart = wrapper.findComponent({ name: 'Line' })
      expect(lineChart.exists()).toBe(false)
      expect(wrapper.text()).toContain('Nessun dato disponibile.')
    })

    it('shows fallback message when department distribution is empty', async () => {
      const noDept = {
        ...mockStats,
        charts: { ...mockStats.charts, department_distribution: [] },
      }
      const wrapper = await mountDashboard(noDept)
      const doughnutChart = wrapper.findComponent({ name: 'Doughnut' })
      expect(doughnutChart.exists()).toBe(false)
    })
  })

  describe('section headers', () => {
    it('shows page title and chart headers', async () => {
      const wrapper = await mountDashboard()
      expect(wrapper.text()).toContain('Dashboard HR')
      expect(wrapper.text()).toContain('Trend Assunzioni')
      expect(wrapper.text()).toContain('Distribuzione Dipartimenti')
    })
  })
})
