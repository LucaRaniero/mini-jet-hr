import { createRouter, createWebHistory } from 'vue-router'
import EmployeeListView from '@/views/EmployeeListView.vue'
import EmployeeCreateView from '@/views/EmployeeCreateView.vue'
import EmployeeEditView from '@/views/EmployeeEditView.vue'
import ContractListView from '@/views/ContractListView.vue'
import ContractCreateView from '@/views/ContractCreateView.vue'
import ContractEditView from '@/views/ContractEditView.vue'

const routes = [
  {
    path: '/',
    name: 'employee-list',
    component: EmployeeListView,
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
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
