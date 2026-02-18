<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { RouterLink } from 'vue-router'
import { fetchAPI, deleteEmployee } from '@/api'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const route = useRoute()

// Reactive state
const employees = ref([])
const loading = ref(true)
const error = ref(null)

// Messaggio di successo (arriva da query string dopo create/edit, o da delete inline)
const successMessage = ref(route.query.message || '')

// Delete state
const employeeToDelete = ref(null)
const showDeleteDialog = ref(false)

// Auto-clear del messaggio di successo dopo 3 secondi
if (successMessage.value) {
  setTimeout(() => {
    successMessage.value = ''
  }, 3000)
}

async function fetchEmployees() {
  try {
    loading.value = true
    error.value = null
    const data = await fetchAPI('/employees/')
    employees.value = data.results
  } catch {
    error.value = 'Errore nel caricamento dei dipendenti.'
  } finally {
    loading.value = false
  }
}

function confirmDelete(emp) {
  employeeToDelete.value = emp
  showDeleteDialog.value = true
}

async function handleDelete() {
  try {
    await deleteEmployee(employeeToDelete.value.id)
    successMessage.value =
      `${employeeToDelete.value.last_name}, ${employeeToDelete.value.first_name} eliminato con successo.`
    showDeleteDialog.value = false
    employeeToDelete.value = null
    await fetchEmployees()
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch {
    error.value = "Errore durante l'eliminazione."
    showDeleteDialog.value = false
    employeeToDelete.value = null
  }
}

function cancelDelete() {
  showDeleteDialog.value = false
  employeeToDelete.value = null
}

onMounted(() => {
  fetchEmployees()
})
</script>

<template>
  <div class="max-w-5xl mx-auto p-6">
    <h1 class="text-2xl font-bold mb-6 text-gray-800">Dipendenti</h1>

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
      v-else-if="employees.length > 0"
      class="min-w-full bg-white shadow rounded-lg overflow-hidden"
    >
      <thead class="bg-gray-50 border-b">
        <tr>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Nome</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Email</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Ruolo</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Reparto</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Data Assunzione</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Azioni</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="emp in employees"
          :key="emp.id"
          class="border-b last:border-b-0 hover:bg-gray-50"
        >
          <td class="px-4 py-3 text-sm">{{ emp.last_name }}, {{ emp.first_name }}</td>
          <td class="px-4 py-3 text-sm text-gray-600">{{ emp.email }}</td>
          <td class="px-4 py-3 text-sm">
            <span
              class="inline-block px-2 py-1 text-xs font-medium rounded-full"
              :class="{
                'bg-blue-100 text-blue-700': emp.role === 'employee',
                'bg-purple-100 text-purple-700': emp.role === 'manager',
                'bg-amber-100 text-amber-700': emp.role === 'admin',
              }"
            >
              {{ emp.role }}
            </span>
          </td>
          <td class="px-4 py-3 text-sm text-gray-600">{{ emp.department || '—' }}</td>
          <td class="px-4 py-3 text-sm text-gray-600">{{ emp.hire_date }}</td>
          <td class="px-4 py-3 text-sm">
            <RouterLink
              :to="`/employees/${emp.id}/contracts`"
              class="text-blue-600 hover:underline mr-3"
            >
              Contratti
            </RouterLink>
            <RouterLink
              :to="`/employees/${emp.id}/edit`"
              class="text-blue-600 hover:underline mr-3"
            >
              Modifica
            </RouterLink>
            <button
              type="button"
              class="text-red-600 hover:underline"
              @click="confirmDelete(emp)"
            >
              Elimina
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Empty state -->
    <p v-else class="text-gray-500">Nessun dipendente trovato.</p>

    <!-- Dialog di conferma eliminazione -->
    <ConfirmDialog
      :visible="showDeleteDialog"
      title="Elimina dipendente"
      :message="
        employeeToDelete
          ? `Vuoi eliminare ${employeeToDelete.last_name}, ${employeeToDelete.first_name}? L'operazione è reversibile.`
          : ''
      "
      @confirm="handleDelete"
      @cancel="cancelDelete"
    />
  </div>
</template>
