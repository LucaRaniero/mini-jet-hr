<script setup>
import { ref, computed, onMounted } from 'vue'
import { Line, Doughnut } from 'vue-chartjs'
import {
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { fetchDashboardStats } from '@/api'

// Registra i componenti Chart.js che usiamo (tree-shaking).
// CategoryScale = asse X con labels (mesi), LinearScale = asse Y numerico,
// PointElement/LineElement = punti e linee, ArcElement = spicchi del doughnut,
// Filler = area sotto la linea (gradient).
Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Tooltip,
  Legend,
  Filler
)

const stats = ref(null)
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    stats.value = await fetchDashboardStats()
  } catch {
    error.value = 'Errore nel caricamento della dashboard.'
  } finally {
    loading.value = false
  }
})

// --- KPI cards: estrae i numeri dalle stats ---
const kpiCards = computed(() => {
  if (!stats.value) return []
  const { employees, contracts, onboarding } = stats.value
  return [
    {
      label: 'Dipendenti Attivi',
      value: employees.active,
      color: 'bg-blue-500',
      textColor: 'text-blue-600',
      bgLight: 'bg-blue-50',
    },
    {
      label: 'Nuove Assunzioni (mese)',
      value: employees.new_hires,
      color: 'bg-green-500',
      textColor: 'text-green-600',
      bgLight: 'bg-green-50',
    },
    {
      label: 'Contratti in Scadenza',
      value: contracts.expiring,
      color: 'bg-amber-500',
      textColor: 'text-amber-600',
      bgLight: 'bg-amber-50',
    },
    {
      label: 'Onboarding in Corso',
      value: onboarding.in_progress,
      color: 'bg-purple-500',
      textColor: 'text-purple-600',
      bgLight: 'bg-purple-50',
    },
  ]
})

// --- Line chart: headcount trend ---
// Struttura dati Chart.js: { labels: [...], datasets: [{ data: [...] }] }
// labels = asse X (mesi), data = asse Y (conteggi)
const headcountChartData = computed(() => {
  if (!stats.value?.charts?.headcount_trend) {
    return { labels: [], datasets: [] }
  }
  const trend = stats.value.charts.headcount_trend
  return {
    labels: trend.map((entry) => entry.month),
    datasets: [
      {
        label: 'Nuovi dipendenti',
        data: trend.map((entry) => entry.count),
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.3,
      },
    ],
  }
})

const headcountChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { stepSize: 1 },
    },
  },
}

// --- Doughnut chart: distribuzione dipartimenti ---
// Palette colori per le fette del doughnut
const DEPARTMENT_COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
  '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16',
]

const departmentChartData = computed(() => {
  if (!stats.value?.charts?.department_distribution) {
    return { labels: [], datasets: [] }
  }
  const dist = stats.value.charts.department_distribution
  return {
    labels: dist.map((entry) => entry.department),
    datasets: [
      {
        data: dist.map((entry) => entry.count),
        backgroundColor: DEPARTMENT_COLORS.slice(0, dist.length),
      },
    ],
  }
})

const doughnutChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom' },
  },
}
</script>

<template>
  <div class="max-w-5xl mx-auto px-6">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Dashboard HR</h1>

    <!-- Loading state -->
    <p v-if="loading" class="text-gray-500">Caricamento dashboard...</p>

    <!-- Error state -->
    <p v-else-if="error" class="text-red-600">{{ error }}</p>

    <!-- Dashboard content -->
    <div v-else>
      <!-- KPI Cards: grid 4 colonne su desktop, 2 su tablet, 1 su mobile -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div
          v-for="card in kpiCards"
          :key="card.label"
          class="bg-white rounded-lg shadow-sm p-5"
        >
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-500">{{ card.label }}</p>
              <p class="text-3xl font-bold mt-1" :class="card.textColor">
                {{ card.value }}
              </p>
            </div>
            <div class="w-10 h-10 rounded-full flex items-center justify-center" :class="card.bgLight">
              <div class="w-3 h-3 rounded-full" :class="card.color"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts: 2 colonne su desktop, stack su mobile -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Line chart: headcount trend -->
        <div class="bg-white rounded-lg shadow-sm p-5">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">
            Trend Assunzioni
          </h2>
          <div class="h-64">
            <Line
              v-if="headcountChartData.labels.length > 0"
              :data="headcountChartData"
              :options="headcountChartOptions"
            />
            <p v-else class="text-gray-400 text-sm">Nessun dato disponibile.</p>
          </div>
        </div>

        <!-- Doughnut chart: distribuzione dipartimenti -->
        <div class="bg-white rounded-lg shadow-sm p-5">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">
            Distribuzione Dipartimenti
          </h2>
          <div class="h-64">
            <Doughnut
              v-if="departmentChartData.labels.length > 0"
              :data="departmentChartData"
              :options="doughnutChartOptions"
            />
            <p v-else class="text-gray-400 text-sm">Nessun dato disponibile.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
