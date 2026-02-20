<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { fetchOnboardingTemplates, deleteOnboardingTemplate } from '@/api'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const route = useRoute()

// Reactive state
const templates = ref([])
const loading = ref(true)
const error = ref(null)

// Messaggio di successo (da query string dopo create/edit)
const successMessage = ref(route.query.message || '')

// Delete state
const templateToDelete = ref(null)
const showDeleteDialog = ref(false)

if (successMessage.value) {
  setTimeout(() => {
    successMessage.value = ''
  }, 3000)
}

async function loadTemplates() {
  try {
    loading.value = true
    error.value = null
    const result = await fetchOnboardingTemplates()
    templates.value = result.data.results
  } catch {
    error.value = 'Errore nel caricamento dei template.'
  } finally {
    loading.value = false
  }
}

function confirmDelete(tmpl) {
  templateToDelete.value = tmpl
  showDeleteDialog.value = true
}

async function handleDelete() {
  try {
    await deleteOnboardingTemplate(templateToDelete.value.id)
    successMessage.value = `Template "${templateToDelete.value.name}" eliminato con successo.`
    showDeleteDialog.value = false
    templateToDelete.value = null
    await loadTemplates()
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch {
    error.value = "Errore durante l'eliminazione."
    showDeleteDialog.value = false
    templateToDelete.value = null
  }
}

function cancelDelete() {
  showDeleteDialog.value = false
  templateToDelete.value = null
}

onMounted(() => {
  loadTemplates()
})
</script>

<template>
  <div class="max-w-5xl mx-auto p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-800">Template Onboarding</h1>
      <RouterLink
        to="/onboarding/templates/new"
        class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm"
      >
        + Nuovo Template
      </RouterLink>
    </div>

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
      v-else-if="templates.length > 0"
      class="min-w-full bg-white shadow rounded-lg overflow-hidden"
    >
      <thead class="bg-gray-50 border-b">
        <tr>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Ordine</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Nome</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Descrizione</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-600">Azioni</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="tmpl in templates"
          :key="tmpl.id"
          class="border-b last:border-b-0 hover:bg-gray-50"
        >
          <td class="px-4 py-3 text-sm text-gray-600">{{ tmpl.order }}</td>
          <td class="px-4 py-3 text-sm font-medium">{{ tmpl.name }}</td>
          <td class="px-4 py-3 text-sm text-gray-600">
            {{ tmpl.description ? tmpl.description.substring(0, 80) + (tmpl.description.length > 80 ? '...' : '') : '—' }}
          </td>
          <td class="px-4 py-3 text-sm">
            <RouterLink
              :to="`/onboarding/templates/${tmpl.id}/edit`"
              class="text-blue-600 hover:underline mr-3"
            >
              Modifica
            </RouterLink>
            <button
              type="button"
              class="text-red-600 hover:underline"
              @click="confirmDelete(tmpl)"
            >
              Elimina
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Empty state -->
    <p v-else class="text-gray-500">
      Nessun template onboarding configurato.
      <RouterLink to="/onboarding/templates/new" class="text-blue-600 hover:underline">
        Crea il primo template
      </RouterLink>
    </p>

    <!-- Dialog di conferma eliminazione -->
    <ConfirmDialog
      :visible="showDeleteDialog"
      title="Elimina template"
      :message="
        templateToDelete
          ? `Vuoi eliminare il template &quot;${templateToDelete.name}&quot;? I task già assegnati ai dipendenti non verranno modificati.`
          : ''
      "
      @confirm="handleDelete"
      @cancel="cancelDelete"
    />
  </div>
</template>
