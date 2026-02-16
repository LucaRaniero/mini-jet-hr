<script setup>
import { useRouter } from 'vue-router'
import EmployeeForm from '@/components/EmployeeForm.vue'

const router = useRouter()

function onSaved() {
  router.push({ name: 'employee-list', query: { message: 'Dipendente creato con successo.' } })
}
</script>

<template>
  <div class="max-w-5xl mx-auto p-6">
    <EmployeeForm @saved="onSaved" />
  </div>
</template>