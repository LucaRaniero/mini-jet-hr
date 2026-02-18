<script setup>
// Come EmployeeEditView: fetch dati → loading/error → passa al form.
// Differenza: due parametri dalla route (employeeId + contractId)
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchContract } from '@/api'
import ContractForm from '@/components/ContractForm.vue'

const route = useRoute()
const router = useRouter()
const employeeId = Number(route.params.employeeId)
const contractId = Number(route.params.contractId)

const contract = ref(null)
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    const result = await fetchContract(employeeId, contractId)
    contract.value = result.data
  } catch {
    error.value = 'Contratto non trovato.'
  } finally {
    loading.value = false
  }
})

function onSaved() {
  router.push({
    name: 'contract-list',
    params: { employeeId },
    query: { message: 'Contratto aggiornato con successo.' },
  })
}
</script>

<template>
  <div class="max-w-5xl mx-auto p-6">
    <div v-if="loading" class="text-gray-500">Caricamento...</div>
    <div v-else-if="error" class="bg-red-50 text-red-700 p-4 rounded">{{ error }}</div>
    <ContractForm v-else :employee-id="employeeId" :contract="contract" @saved="onSaved" />
  </div>
</template>
