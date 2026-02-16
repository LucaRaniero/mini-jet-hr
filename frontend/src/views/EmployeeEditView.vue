<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchEmployee } from '@/api'
import EmployeeForm from '@/components/EmployeeForm.vue'

const route = useRoute()
const router = useRouter()

const employee = ref(null)
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    const result = await fetchEmployee(route.params.id)
    employee.value = result.data
  } catch {
    error.value = 'Dipendente non trovato.'
  } finally {
    loading.value = false
  }
})

function onSaved() {
  router.push({
    name: 'employee-list',
    query: { message: 'Dipendente aggiornato con successo.' },
  })
}
</script>

<template>
  <div class="max-w-5xl mx-auto p-6">
    <div v-if="loading" class="text-gray-500">Caricamento...</div>
    <div v-else-if="error" class="bg-red-50 text-red-700 p-4 rounded">{{ error }}</div>
    <EmployeeForm v-else :employee="employee" @saved="onSaved" />
  </div>
</template>
