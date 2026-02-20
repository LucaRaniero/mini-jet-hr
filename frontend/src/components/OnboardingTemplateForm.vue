<script setup>
import { ref, computed, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { createOnboardingTemplate, updateOnboardingTemplate } from '@/api'

// --- Props e Emit ---
// template = null → modalità CREATE
// template = {...} → modalità EDIT
const props = defineProps({
  template: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['saved'])

const isEditMode = computed(() => props.template !== null)

// --- Stato del form ---
const form = ref({
  name: '',
  description: '',
  order: 0,
})

const errors = ref({})
const submitting = ref(false)

// --- watch: popola il form in edit mode ---
watch(
  () => props.template,
  (tmpl) => {
    if (tmpl) {
      form.value = {
        name: tmpl.name,
        description: tmpl.description || '',
        order: tmpl.order,
      }
    }
  },
  { immediate: true },
)

// --- Submit ---
async function handleSubmit() {
  errors.value = {}
  submitting.value = true

  try {
    let result
    if (isEditMode.value) {
      result = await updateOnboardingTemplate(props.template.id, form.value)
    } else {
      result = await createOnboardingTemplate(form.value)
    }

    if (result.error) {
      errors.value = result.error
      return
    }

    emit('saved', result.data)
  } catch {
    errors.value = { non_field_errors: ['Errore di rete. Riprova.'] }
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <form @submit.prevent="handleSubmit" class="max-w-lg mx-auto bg-white p-6 rounded-lg shadow">
    <h2 class="text-xl font-bold mb-6 text-gray-800">
      {{ isEditMode ? 'Modifica Template' : 'Nuovo Template' }}
    </h2>

    <!-- Errori generici -->
    <div v-if="errors.non_field_errors" class="bg-red-50 text-red-700 p-3 rounded mb-4">
      <p v-for="msg in errors.non_field_errors" :key="msg">{{ msg }}</p>
    </div>

    <!-- Nome -->
    <div class="mb-4">
      <label for="name" class="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
      <input
        id="name"
        v-model="form.name"
        type="text"
        required
        maxlength="200"
        placeholder="es. Firma contratto"
        class="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        :class="{ 'border-red-500': errors.name }"
      />
      <p v-if="errors.name" class="text-red-600 text-xs mt-1">{{ errors.name[0] }}</p>
    </div>

    <!-- Descrizione -->
    <div class="mb-4">
      <label for="description" class="block text-sm font-medium text-gray-700 mb-1">
        Descrizione
      </label>
      <textarea
        id="description"
        v-model="form.description"
        rows="3"
        placeholder="Istruzioni dettagliate per il dipendente..."
        class="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        :class="{ 'border-red-500': errors.description }"
      />
      <p v-if="errors.description" class="text-red-600 text-xs mt-1">
        {{ errors.description[0] }}
      </p>
    </div>

    <!-- Ordine -->
    <div class="mb-6">
      <label for="order" class="block text-sm font-medium text-gray-700 mb-1">Ordine *</label>
      <input
        id="order"
        v-model="form.order"
        type="number"
        required
        min="0"
        class="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        :class="{ 'border-red-500': errors.order }"
      />
      <p v-if="errors.order" class="text-red-600 text-xs mt-1">{{ errors.order[0] }}</p>
      <p class="text-gray-400 text-xs mt-1">
        Determina l'ordine di visualizzazione nella checklist (0 = primo).
      </p>
    </div>

    <!-- Bottoni -->
    <div class="flex gap-3">
      <button
        type="submit"
        :disabled="submitting"
        class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ submitting ? 'Salvataggio...' : isEditMode ? 'Aggiorna' : 'Crea Template' }}
      </button>
      <RouterLink
        to="/onboarding/templates"
        class="px-4 py-2 rounded border text-sm text-gray-600 hover:bg-gray-50"
      >
        Annulla
      </RouterLink>
    </div>
  </form>
</template>
