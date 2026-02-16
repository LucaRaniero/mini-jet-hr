<script setup>
import { RouterView, RouterLink } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <header class="bg-white shadow-sm">
      <div class="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
        <RouterLink to="/" class="text-xl font-bold text-gray-900 hover:text-blue-600">
          Mini Jet HR
        </RouterLink>
        <nav>
          <RouterLink
            to="/employees/new"
            class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm"
          >
            + Nuovo Dipendente
          </RouterLink>
        </nav>
      </div>
    </header>
    <main class="py-6">
      <RouterView />
    </main>
  </div>
</template>
