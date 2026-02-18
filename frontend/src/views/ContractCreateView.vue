<script setup>
// Come EmployeeCreateView, ma con employeeId dalla route.
// onSaved redirect: torna alla lista contratti (non dipendenti)
import { useRoute, useRouter } from 'vue-router'
import ContractForm from '@/components/ContractForm.vue'

const route = useRoute()
const router = useRouter()
const employeeId = Number(route.params.employeeId)

function onSaved() {
  router.push({
    name: 'contract-list',
    params: { employeeId },
    query: { message: 'Contratto creato con successo.' },
  })
}
</script>

<template>
  <div class="max-w-5xl mx-auto p-6">
    <ContractForm :employee-id="employeeId" @saved="onSaved" />
  </div>
</template>
