<script setup>
import { ref, computed, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { createEmployee, updateEmployee } from '@/api'

// --- Props e Emit ---
// employee = null → modalità CREATE
// employee = {...} → modalità EDIT
const props = defineProps({
  employee: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['saved'])

const isEditMode = computed(() => props.employee !== null)

// --- Stato del form (come le colonne di una staging table) ---
const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  role: 'employee',
  department: '',
  hire_date: '',
})

// Errori server per campo: { field_name: ["messaggio"] }
const errors = ref({})
const submitting = ref(false)

// Data massima selezionabile = oggi (impedisce date future nel date picker)
const todayISO = computed(() => new Date().toISOString().split('T')[0])

// --- watch: popola il form quando il parent passa i dati del dipendente ---
// immediate: true perché i dati potrebbero già essere pronti al mount
watch(
  () => props.employee,
  (emp) => {
    if (emp) {
      form.value = {
        first_name: emp.first_name,
        last_name: emp.last_name,
        email: emp.email,
        role: emp.role,
        department: emp.department || '',
        hire_date: emp.hire_date,
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
      // PATCH: invia solo i campi modificabili (esclude email — è immutabile)
      const payload = { ...form.value }
      delete payload.email
      result = await updateEmployee(props.employee.id, payload)
    } else {
      result = await createEmployee(form.value)
    }

    if (result.error) {
      // Server ha ritornato 400 con errori per campo
      errors.value = result.error
      return
    }

    // Successo — segnala al parent
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
      {{ isEditMode ? 'Modifica Dipendente' : 'Nuovo Dipendente' }}
    </h2>

    <!-- Errori generici (non legati a un campo specifico) -->
    <div v-if="errors.non_field_errors" class="bg-red-50 text-red-700 p-3 rounded mb-4">
      <p v-for="msg in errors.non_field_errors" :key="msg">{{ msg }}</p>
    </div>

    <!-- Nome -->
    <div class="mb-4">
      <label for="first_name" class="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
      <input
        id="first_name"
        v-model="form.first_name"
        type="text"
        required
        maxlength="100"
        class="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        :class="{ 'border-red-500': errors.first_name }"
      />
      <p v-if="errors.first_name" class="text-red-600 text-xs mt-1">{{ errors.first_name[0] }}</p>
    </div>

    <!-- Cognome -->
    <div class="mb-4">
      <label for="last_name" class="block text-sm font-medium text-gray-700 mb-1">Cognome *</label>
      <input
        id="last_name"
        v-model="form.last_name"
        type="text"
        required
        maxlength="100"
        class="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        :class="{ 'border-red-500': errors.last_name }"
      />
      <p v-if="errors.last_name" class="text-red-600 text-xs mt-1">{{ errors.last_name[0] }}</p>
    </div>

    <!-- Email -->
    <div class="mb-4">
      <label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email *</label>
      <input
        id="email"
        v-model="form.email"
        type="email"
        required
        :disabled="isEditMode"
        class="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        :class="{
          'border-red-500': errors.email,
          'bg-gray-100 cursor-not-allowed text-gray-500': isEditMode,
        }"
      />
      <p v-if="errors.email" class="text-red-600 text-xs mt-1">{{ errors.email[0] }}</p>
      <p v-else-if="isEditMode" class="text-gray-400 text-xs mt-1">
        L'email non può essere modificata.
      </p>
    </div>

    <!-- Ruolo -->
    <div class="mb-4">
      <label for="role" class="block text-sm font-medium text-gray-700 mb-1">Ruolo</label>
      <select
        id="role"
        v-model="form.role"
        class="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        :class="{ 'border-red-500': errors.role }"
      >
        <option value="employee">Employee</option>
        <option value="manager">Manager</option>
        <option value="admin">Admin</option>
      </select>
      <p v-if="errors.role" class="text-red-600 text-xs mt-1">{{ errors.role[0] }}</p>
    </div>

    <!-- Dipartimento -->
    <div class="mb-4">
      <label for="department" class="block text-sm font-medium text-gray-700 mb-1"
        >Dipartimento</label
      >
      <input
        id="department"
        v-model="form.department"
        type="text"
        maxlength="100"
        class="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        :class="{ 'border-red-500': errors.department }"
      />
      <p v-if="errors.department" class="text-red-600 text-xs mt-1">
        {{ errors.department[0] }}
      </p>
    </div>

    <!-- Data Assunzione -->
    <div class="mb-6">
      <label for="hire_date" class="block text-sm font-medium text-gray-700 mb-1"
        >Data Assunzione *</label
      >
      <input
        id="hire_date"
        v-model="form.hire_date"
        type="date"
        required
        :max="todayISO"
        class="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        :class="{ 'border-red-500': errors.hire_date }"
      />
      <p v-if="errors.hire_date" class="text-red-600 text-xs mt-1">{{ errors.hire_date[0] }}</p>
    </div>

    <!-- Bottoni -->
    <div class="flex gap-3">
      <button
        type="submit"
        :disabled="submitting"
        class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ submitting ? 'Salvataggio...' : isEditMode ? 'Aggiorna' : 'Crea Dipendente' }}
      </button>
      <RouterLink
        to="/"
        class="px-4 py-2 rounded border text-sm text-gray-600 hover:bg-gray-50"
      >
        Annulla
      </RouterLink>
    </div>
  </form>
</template>
