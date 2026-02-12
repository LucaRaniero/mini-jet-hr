<script setup>
import { ref, onMounted } from 'vue'
import { fetchAPI } from '@/api'

// Reactive state — like DECLARE @variable in T-SQL
// When these change, the template auto-updates (no manual DOM manipulation)
const employees = ref([])
const loading = ref(true)
const error = ref(null)

async function fetchEmployees() {
  try {
    loading.value = true
    error.value = null
    const data = await fetchAPI('/employees/')
    employees.value = data.results
  } catch (err) {
    error.value = 'Errore nel caricamento dei dipendenti.'
  } finally {
    loading.value = false
  }
}

// onMounted = runs when the component appears on the page
// Like an AFTER INSERT trigger on the DOM
onMounted(() => {
  fetchEmployees()
})
</script>

<template>
  <div class="max-w-5xl mx-auto p-6">
    <h1 class="text-2xl font-bold mb-6 text-gray-800">Dipendenti</h1>

    <!-- Loading state -->
    <div v-if="loading" class="text-gray-500">Caricamento...</div>

    <!-- Error state -->
    <div v-else-if="error" class="bg-red-50 text-red-700 p-4 rounded">
      {{ error }}
    </div>

    <!-- Data state -->
    <table v-else-if="employees.length > 0" class="min-w-full bg-white shadow rounded-lg overflow-hidden">
      <thead class="bg-gray-50 border-b">
        <tr>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Nome</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Email</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Ruolo</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Reparto</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Data Assunzione</th>
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
            <span class="inline-block px-2 py-1 text-xs font-medium rounded-full"
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
        </tr>
      </tbody>
    </table>

    <!-- Empty state -->
    <p v-else class="text-gray-500">Nessun dipendente trovato.</p>
  </div>
</template>
