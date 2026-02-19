<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { RouterLink } from 'vue-router'
import { fetchContracts, fetchEmployee, deleteContract } from '@/api'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

// Props: l'employeeId arriva dalla View, che lo estrae dalla route
const props = defineProps({
  employeeId: {
    type: Number,
    required: true,
  },
})

const route = useRoute()

// --- State ---
const contracts = ref([])
const employee = ref(null)
const loading = ref(true)
const error = ref(null)

// Messaggio di successo (da query string dopo create/edit, o da delete inline)
const successMessage = ref(route.query.message || '')

// Delete state — stesso pattern di EmployeeList
const contractToDelete = ref(null)
const showDeleteDialog = ref(false)

// Auto-clear del messaggio dopo 3 secondi
if (successMessage.value) {
  setTimeout(() => {
    successMessage.value = ''
  }, 3000)
}

// --- Helpers ---

// Formatta RAL come valuta italiana: 30000.00 → "€ 30.000,00"
// Intl.NumberFormat è l'API standard del browser per la localizzazione numerica
function formatRAL(value) {
  return new Intl.NumberFormat('it-IT', {
    style: 'currency',
    currency: 'EUR',
  }).format(value)
}

// --- Data fetching ---

async function loadData() {
  try {
    loading.value = true
    error.value = null
    // Promise.all: fetch employee e contratti IN PARALLELO
    // Equivalente SQL: due query lanciate contemporaneamente
    const [empResult, contractsResult] = await Promise.all([
      fetchEmployee(props.employeeId),
      fetchContracts(props.employeeId),
    ])
    employee.value = empResult.data
    // L'API restituisce { count, results: [...] } per via della paginazione globale
    contracts.value = contractsResult.data.results
  } catch {
    error.value = 'Errore nel caricamento dei contratti.'
  } finally {
    loading.value = false
  }
}

// --- Delete flow (stesso pattern di EmployeeList) ---

function confirmDelete(contract) {
  contractToDelete.value = contract
  showDeleteDialog.value = true
}

async function handleDelete() {
  try {
    await deleteContract(props.employeeId, contractToDelete.value.id)
    successMessage.value = 'Contratto eliminato con successo.'
    showDeleteDialog.value = false
    contractToDelete.value = null
    await loadData()
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch {
    error.value = "Errore durante l'eliminazione del contratto."
    showDeleteDialog.value = false
    contractToDelete.value = null
  }
}

function cancelDelete() {
  showDeleteDialog.value = false
  contractToDelete.value = null
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="max-w-5xl mx-auto p-6">
    <!-- Navigazione: link per tornare alla lista dipendenti -->
    <RouterLink to="/" class="text-blue-600 hover:underline text-sm">
      ← Dipendenti
    </RouterLink>

    <!-- Header con nome dipendente e bottone nuovo contratto -->
    <div class="flex items-center justify-between mt-4 mb-6">
      <h1 class="text-2xl font-bold text-gray-800">
        Contratti di {{ employee ? `${employee.last_name}, ${employee.first_name}` : '...' }}
      </h1>
      <RouterLink
        :to="`/employees/${employeeId}/contracts/new`"
        class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm"
      >
        + Nuovo Contratto
      </RouterLink>
    </div>

    <!-- Messaggio di successo -->
    <div v-if="successMessage" class="bg-green-50 text-green-700 p-3 rounded mb-4">
      {{ successMessage }}
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="text-gray-500">Caricamento...</div>

    <!-- Error state -->
    <div v-else-if="error" class="bg-red-50 text-red-700 p-4 rounded">
      {{ error }}
    </div>

    <!-- Data state -->
    <table
      v-else-if="contracts.length > 0"
      class="min-w-full bg-white shadow rounded-lg overflow-hidden"
    >
      <thead class="bg-gray-50 border-b">
        <tr>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Tipo</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">CCNL</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">RAL</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Data Inizio</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Data Fine</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Stato</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">PDF</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Azioni</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="contract in contracts"
          :key="contract.id"
          class="border-b last:border-b-0 hover:bg-gray-50"
        >
          <!-- capitalize: CSS trasforma "determinato" → "Determinato" -->
          <td class="px-4 py-3 text-sm capitalize">{{ contract.contract_type }}</td>
          <td class="px-4 py-3 text-sm capitalize">{{ contract.ccnl }}</td>
          <td class="px-4 py-3 text-sm text-gray-600">{{ formatRAL(contract.ral) }}</td>
          <td class="px-4 py-3 text-sm text-gray-600">{{ contract.start_date }}</td>
          <td class="px-4 py-3 text-sm text-gray-600">{{ contract.end_date || '—' }}</td>
          <td class="px-4 py-3 text-sm">
            <!-- Stato derivato: end_date null = attivo, altrimenti chiuso -->
            <span
              class="inline-block px-2 py-1 text-xs font-medium rounded-full"
              :class="
                contract.end_date
                  ? 'bg-gray-100 text-gray-600'
                  : 'bg-green-100 text-green-700'
              "
            >
              {{ contract.end_date ? 'Chiuso' : 'Attivo' }}
            </span>
          </td>
          <!-- Documento PDF: link di preview (apre in nuova tab) -->
          <td class="px-4 py-3 text-sm">
            <a
              v-if="contract.document_url"
              :href="contract.document_url"
              target="_blank"
              class="text-blue-600 hover:underline"
            >
              Visualizza
            </a>
            <span v-else class="text-gray-400">—</span>
          </td>
          <td class="px-4 py-3 text-sm">
            <RouterLink
              :to="`/employees/${employeeId}/contracts/${contract.id}/edit`"
              class="text-blue-600 hover:underline mr-3"
            >
              Modifica
            </RouterLink>
            <button
              type="button"
              class="text-red-600 hover:underline"
              @click="confirmDelete(contract)"
            >
              Elimina
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Empty state -->
    <p v-else class="text-gray-500">Nessun contratto trovato per questo dipendente.</p>

    <!-- Dialog di conferma eliminazione -->
    <ConfirmDialog
      :visible="showDeleteDialog"
      title="Elimina contratto"
      :message="
        contractToDelete
          ? `Vuoi eliminare il contratto ${contractToDelete.contract_type} dal ${contractToDelete.start_date}? L\u0027operazione è irreversibile.`
          : ''
      "
      @confirm="handleDelete"
      @cancel="cancelDelete"
    />
  </div>
</template>
