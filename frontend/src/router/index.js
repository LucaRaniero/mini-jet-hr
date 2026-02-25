import { createRouter, createWebHistory } from 'vue-router'
import EmployeeListView from '@/views/EmployeeListView.vue'
import EmployeeCreateView from '@/views/EmployeeCreateView.vue'
import EmployeeEditView from '@/views/EmployeeEditView.vue'
import ContractListView from '@/views/ContractListView.vue'
import ContractCreateView from '@/views/ContractCreateView.vue'
import ContractEditView from '@/views/ContractEditView.vue'
import OnboardingTemplateListView from '@/views/OnboardingTemplateListView.vue'
import OnboardingTemplateCreateView from '@/views/OnboardingTemplateCreateView.vue'
import OnboardingTemplateEditView from '@/views/OnboardingTemplateEditView.vue'
import OnboardingChecklistView from '@/views/OnboardingChecklistView.vue'
import DashboardView from '@/views/DashboardView.vue'

const routes = [
  {
    path: '/',
    name: 'employee-list',
    component: EmployeeListView,
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView,
  },
  {
    path: '/employees/new',
    name: 'employee-create',
    component: EmployeeCreateView,
  },
  {
    path: '/employees/:id/edit',
    name: 'employee-edit',
    component: EmployeeEditView,
  },
  // --- Contract routes (nested sotto employee) ---
  {
    path: '/employees/:employeeId/contracts',
    name: 'contract-list',
    component: ContractListView,
  },
  {
    path: '/employees/:employeeId/contracts/new',
    name: 'contract-create',
    component: ContractCreateView,
  },
  {
    path: '/employees/:employeeId/contracts/:contractId/edit',
    name: 'contract-edit',
    component: ContractEditView,
  },
  // --- Onboarding template routes (top-level, HR management) ---
  {
    path: '/onboarding/templates',
    name: 'onboarding-template-list',
    component: OnboardingTemplateListView,
  },
  {
    path: '/onboarding/templates/new',
    name: 'onboarding-template-create',
    component: OnboardingTemplateCreateView,
  },
  {
    path: '/onboarding/templates/:id/edit',
    name: 'onboarding-template-edit',
    component: OnboardingTemplateEditView,
  },
  // --- Onboarding checklist (nested sotto employee) ---
  {
    path: '/employees/:employeeId/onboarding',
    name: 'onboarding-checklist',
    component: OnboardingChecklistView,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
