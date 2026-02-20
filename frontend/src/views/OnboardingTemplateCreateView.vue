<script setup>
// View wrapper: redirect dopo creazione template.
import { useRouter } from 'vue-router'
import OnboardingTemplateForm from '@/components/OnboardingTemplateForm.vue'

const router = useRouter()

function onSaved() {
  router.push({
    name: 'onboarding-template-list',
    query: { message: 'Template creato con successo.' },
  })
}
</script>

<template>
  <div class="max-w-5xl mx-auto p-6">
    <OnboardingTemplateForm @saved="onSaved" />
  </div>
</template>
