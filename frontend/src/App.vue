<script setup>
import EmployeeList from './components/EmployeeList.vue'
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <header class="bg-white shadow-sm">
      <div class="max-w-5xl mx-auto px-6 py-4">
        <h1 class="text-xl font-bold text-gray-900">Mini Jet HR</h1>
      </div>
    </header>
    <main class="py-6">
      <EmployeeList />
    </main>
  </div>
</template>
