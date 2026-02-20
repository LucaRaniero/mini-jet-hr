<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import {
  fetchEmployee,
  fetchOnboardingSteps,
  startOnboarding,
  updateOnboardingStep,
} from '@/api'

const props = defineProps({
  employeeId: {
    type: Number,
    required: true,
  },
})

// State
const employee = ref(null)
const steps = ref([])
const loading = ref(true)
const error = ref(null)
const starting = ref(false)

// --- Computed: progress bar ---
// Equivalente SQL:
//   SELECT COUNT(*) AS total,
//          COUNT(CASE WHEN is_completed THEN 1 END) AS completed
//   FROM onboarding_steps WHERE employee_id = @id
const totalSteps = computed(() => steps.value.length)
const completedSteps = computed(() => steps.value.filter((s) => s.is_completed).length)
const progressPercent = computed(() =>
  totalSteps.value > 0 ? Math.round((completedSteps.value / totalSteps.value) * 100) : 0,
)
const isFullyCompleted = computed(() =>
  totalSteps.value > 0 && completedSteps.value === totalSteps.value,
)

// --- Fetch data ---
async function loadData() {
  try {
    loading.value = true
    error.value = null

    const [empResult, stepsResult] = await Promise.all([
      fetchEmployee(props.employeeId),
      fetchOnboardingSteps(props.employeeId),
    ])

    employee.value = empResult.data
    steps.value = stepsResult.data.results
  } catch {
    error.value = 'Errore nel caricamento dati.'
  } finally {
    loading.value = false
  }
}

// --- Avvia onboarding (POST senza body → bulk create) ---
async function handleStart() {
  try {
    starting.value = true
    error.value = null
    const result = await startOnboarding(props.employeeId)
    // POST ritorna lista non paginata (il nostro create() override)
    steps.value = result.data
  } catch {
    error.value = "Errore nell'avvio dell'onboarding."
  } finally {
    starting.value = false
  }
}

// --- Toggle step completion ---
async function toggleStep(step) {
  const newValue = !step.is_completed
  try {
    error.value = null
    const result = await updateOnboardingStep(props.employeeId, step.id, {
      is_completed: newValue,
    })
    // Aggiorna lo step locale con i dati dal server (completed_at incluso)
    const index = steps.value.findIndex((s) => s.id === step.id)
    if (index !== -1) {
      steps.value[index] = result.data
    }
  } catch {
    error.value = "Errore nell'aggiornamento dello step."
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="max-w-5xl mx-auto p-6">
    <!-- Loading -->
    <div v-if="loading" class="text-gray-500">Caricamento...</div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 text-red-700 p-4 rounded mb-4">
      {{ error }}
    </div>

    <template v-if="employee && !loading">
      <!-- Header con nome dipendente -->
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">
            Onboarding: {{ employee.last_name }}, {{ employee.first_name }}
          </h1>
          <p class="text-sm text-gray-500 mt-1">
            <RouterLink
              :to="`/employees/${employeeId}/contracts`"
              class="text-blue-600 hover:underline"
            >
              Contratti
            </RouterLink>
            <span class="mx-2">|</span>
            <RouterLink to="/" class="text-blue-600 hover:underline">
              Lista dipendenti
            </RouterLink>
          </p>
        </div>
      </div>

      <!-- Stato: nessun step → bottone "Avvia Onboarding" -->
      <div v-if="steps.length === 0" class="bg-white shadow rounded-lg p-8 text-center">
        <p class="text-gray-500 mb-4">
          L'onboarding non è ancora stato avviato per questo dipendente.
        </p>
        <button
          type="button"
          :disabled="starting"
          class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 text-sm disabled:opacity-50"
          @click="handleStart"
        >
          {{ starting ? 'Avvio in corso...' : 'Avvia Onboarding' }}
        </button>
      </div>

      <!-- Stato: step presenti → checklist con progress bar -->
      <div v-else class="bg-white shadow rounded-lg overflow-hidden">
        <!-- Progress bar -->
        <div class="p-4 border-b">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-gray-700">
              Progresso: {{ completedSteps }} / {{ totalSteps }}
            </span>
            <span
              class="text-sm font-semibold"
              :class="isFullyCompleted ? 'text-green-600' : 'text-blue-600'"
            >
              {{ progressPercent }}%
            </span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-3">
            <div
              class="h-3 rounded-full transition-all duration-300"
              :class="isFullyCompleted ? 'bg-green-500' : 'bg-blue-500'"
              :style="{ width: progressPercent + '%' }"
            />
          </div>
          <!-- Badge completato -->
          <div v-if="isFullyCompleted" class="mt-3">
            <span class="inline-block px-3 py-1 text-xs font-medium rounded-full bg-green-100 text-green-700">
              Onboarding completato
            </span>
          </div>
        </div>

        <!-- Checklist -->
        <ul>
          <li
            v-for="step in steps"
            :key="step.id"
            class="flex items-start gap-3 px-4 py-3 border-b last:border-b-0 hover:bg-gray-50 cursor-pointer"
            @click="toggleStep(step)"
          >
            <!-- Checkbox -->
            <input
              type="checkbox"
              :checked="step.is_completed"
              class="mt-1 h-4 w-4 text-blue-600 rounded cursor-pointer"
              @click.stop="toggleStep(step)"
            />
            <!-- Task info -->
            <div class="flex-1">
              <span
                class="text-sm font-medium"
                :class="step.is_completed ? 'text-gray-400 line-through' : 'text-gray-800'"
              >
                {{ step.template_name }}
              </span>
              <p
                v-if="step.template_description"
                class="text-xs mt-1"
                :class="step.is_completed ? 'text-gray-300' : 'text-gray-500'"
              >
                {{ step.template_description }}
              </p>
            </div>
            <!-- Completed timestamp -->
            <span v-if="step.completed_at" class="text-xs text-gray-400 whitespace-nowrap">
              {{ new Date(step.completed_at).toLocaleDateString('it-IT') }}
            </span>
          </li>
        </ul>
      </div>
    </template>
  </div>
</template>
