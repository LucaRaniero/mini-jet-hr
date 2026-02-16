import { createRouter, createWebHistory } from 'vue-router'
import EmployeeListView from '@/views/EmployeeListView.vue'
import EmployeeCreateView from '@/views/EmployeeCreateView.vue'
import EmployeeEditView from '@/views/EmployeeEditView.vue'

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
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
