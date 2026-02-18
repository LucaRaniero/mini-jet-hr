<script setup>
import { ref, computed, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { createContract, updateContract } from '@/api'

const props = defineProps({
  employeeId: {
    type: Number,
    required: true,
  },
  contract: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['saved'])

const isEditMode = computed(() => props.contract !== null)

const form = ref({
  contract_type: 'indeterminato',
  ccnl: 'metalmeccanico',
  ral: '',
  start_date: '',
  end_date: '',
})

const errors = ref({})
const submitting = ref(false)

watch(
  () => props.contract,
  (newContract) => {
    if (newContract) {
      form.value = {
        contract_type: newContract.contract_type,
        ccnl: newContract.ccnl,
        ral: newContract.ral,
        start_date: newContract.start_date,
        end_date: newContract.end_date,
      }
    }
  },
  { immediate: true },
)

async function handleSubmit() {
  submitting.value = true
  errors.value = {}

  try {
    let result
    const payload = { ...form.value }
    if (payload.end_date === '') {
      delete payload.end_date
    }

    if (isEditMode.value) {
      result = await updateContract(props.employeeId, props.contract.id, payload)
    } else {
      result = await createContract(props.employeeId, payload)
    }

    if (result.error) {
      errors.value = result.error
      return
    }

    emit('saved', result.data)
  } catch {
    errors.value = { non_field_errors: ['Errore generico'] }
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <form @submit.prevent="handleSubmit" class="max-w-lg mx-auto bg-white p-6 rounded-lg shadow">
    <h2 class="text-xl font-bold mb-6 text-gray-800">
      {{ isEditMode ? 'Modifica Contratto' : 'Nuovo Contratto' }}
    </h2>

    <!-- Errori generici (non legati a un campo specifico) -->
    <div v-if="errors.non_field_errors" class="bg-red-50 text-red-700 p-3 rounded mb-4">
      <p v-for="msg in errors.non_field_errors" :key="msg">{{ msg }}</p>
    </div>

    <!-- Tipo Contratto -->
    <div class="mb-4">
      <label for="contract_type" class="block text-sm font-medium text-gray-700 mb-1">Tipo Contratto *</label>
      <select
        id="contract_type"
        required
        v-model="form.contract_type"
        class="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        :class="{ 'border-red-500': errors.contract_type }"
      >
        <option value="indeterminato">Indeterminato</option>
        <option value="determinato">Determinato</option>
        <option value="stagista">Stagista</option>
      </select>
      <p v-if="errors.contract_type" class="text-red-600 text-xs mt-1">{{ errors.contract_type[0] }}</p>
    </div>

    <!-- CCNL -->
    <div class="mb-4">
      <label for="ccnl" class="block text-sm font-medium text-gray-700 mb-1">CCNL *</label>
      <select
        id="ccnl"
        required
        v-model="form.ccnl"
        class="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        :class="{ 'border-red-500': errors.ccnl }"
      >
        <option value="metalmeccanico">Metalmeccanico</option>
        <option value="commercio">Commercio</option>
      </select>
      <p v-if="errors.ccnl" class="text-red-600 text-xs mt-1">{{ errors.ccnl[0] }}</p>
    </div>

    <!-- RAL -->
    <div class="mb-4">
      <label for="ral" class="block text-sm font-medium text-gray-700 mb-1">RAL *</label>
      <input
        id="ral"
        v-model="form.ral"
        type="number"
        step="0.01"
        required
        class="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        :class="{ 'border-red-500': errors.ral }"
      />
      <p v-if="errors.ral" class="text-red-600 text-xs mt-1">{{ errors.ral[0] }}</p>
    </div>

    <!-- Data Inizio -->
    <div class="mb-6">
      <label for="start_date" class="block text-sm font-medium text-gray-700 mb-1"
        >Data Inizio *</label
      >
      <input
        id="start_date"
        v-model="form.start_date"
        type="date"
        required
        class="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        :class="{ 'border-red-500': errors.start_date }"
      />
      <p v-if="errors.start_date" class="text-red-600 text-xs mt-1">{{ errors.start_date[0] }}</p>
    </div>

    <!-- Data Fine -->
    <div class="mb-6">
      <label for="end_date" class="block text-sm font-medium text-gray-700 mb-1"
        >Data Fine</label
      >
      <input
        id="end_date"
        v-model="form.end_date"
        type="date"
        class="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        :class="{ 'border-red-500': errors.end_date }"
      />
      <p v-if="errors.end_date" class="text-red-600 text-xs mt-1">{{ errors.end_date[0] }}</p>
    </div>
    
    <!-- Bottoni -->
    <div class="flex gap-3">
      <button
        type="submit"
        :disabled="submitting"
        class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ submitting ? 'Salvataggio...' : isEditMode ? 'Aggiorna' : 'Crea Contratto' }}
      </button>
      <RouterLink
        :to="`/employees/${props.employeeId}/contracts`"
        class="px-4 py-2 rounded border text-sm text-gray-600 hover:bg-gray-50"
      >
        Annulla
      </RouterLink>
    </div>
  </form>
</template>