<script setup>
// View wrapper: fetch template data → passa al form in edit mode.
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchOnboardingTemplate } from '@/api'
import OnboardingTemplateForm from '@/components/OnboardingTemplateForm.vue'

const route = useRoute()
const router = useRouter()
const templateId = Number(route.params.id)

const template = ref(null)
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    const result = await fetchOnboardingTemplate(templateId)
    template.value = result.data
  } catch {
    error.value = 'Template non trovato.'
  } finally {
    loading.value = false
  }
})

function onSaved() {
  router.push({
    name: 'onboarding-template-list',
    query: { message: 'Template aggiornato con successo.' },
  })
}
</script>

<template>
  <div class="max-w-5xl mx-auto p-6">
    <div v-if="loading" class="text-gray-500">Caricamento...</div>
    <div v-else-if="error" class="bg-red-50 text-red-700 p-4 rounded">{{ error }}</div>
    <OnboardingTemplateForm v-else :template="template" @saved="onSaved" />
  </div>
</template>
