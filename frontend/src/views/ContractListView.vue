<script setup>
// View wrapper: estrae employeeId dalla route e lo passa al componente.
// A differenza di EmployeeListView (che non ha props),
// qui il componente ha bisogno di sapere "di quale dipendente?"
import { useRoute } from 'vue-router'
import ContractList from '@/components/ContractList.vue'

const route = useRoute()
// route.params sono sempre stringhe → Number() converte in numero
const employeeId = Number(route.params.employeeId)
</script>

<template>
  <ContractList :employee-id="employeeId" />
</template>
