<script setup>
defineProps({
  visible: {
    type: Boolean,
    required: true,
  },
  title: {
    type: String,
    default: 'Conferma',
  },
  message: {
    type: String,
    default: 'Sei sicuro?',
  },
})

defineEmits(['confirm', 'cancel'])
</script>

<template>
  <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- Backdrop (sfondo scuro cliccabile per chiudere) -->
    <div class="absolute inset-0 bg-black/50" @click="$emit('cancel')" />

    <!-- Dialog -->
    <div class="relative bg-white rounded-lg shadow-lg p-6 max-w-sm w-full mx-4">
      <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ title }}</h3>
      <p class="text-sm text-gray-600 mb-6">{{ message }}</p>
      <div class="flex justify-end gap-3">
        <button
          type="button"
          class="px-4 py-2 rounded border text-sm text-gray-600 hover:bg-gray-50"
          @click="$emit('cancel')"
        >
          Annulla
        </button>
        <button
          type="button"
          class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 text-sm"
          @click="$emit('confirm')"
        >
          Elimina
        </button>
      </div>
    </div>
  </div>
</template>
