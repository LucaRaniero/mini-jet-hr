<script setup>
// View wrapper: estrae employeeId dalla route e lo passa al componente.
import { useRoute } from 'vue-router'
import OnboardingChecklist from '@/components/OnboardingChecklist.vue'

const route = useRoute()
const employeeId = Number(route.params.employeeId)
</script>

<template>
  <OnboardingChecklist :employee-id="employeeId" />
</template>
