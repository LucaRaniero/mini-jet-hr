import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import App from '../App.vue'

// Router stub per i test — createMemoryHistory non usa il browser
function createTestRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div>list</div>' } },
      { path: '/employees/new', component: { template: '<div>create</div>' } },
    ],
  })
}

describe('App', () => {
  it('renders the app header', () => {
    const router = createTestRouter()
    const wrapper = mount(App, {
      global: { plugins: [router] },
    })
    expect(wrapper.text()).toContain('Mini Jet HR')
  })

  it('has a link to create a new employee', () => {
    const router = createTestRouter()
    const wrapper = mount(App, {
      global: { plugins: [router] },
    })
    const link = wrapper.find('a[href="/employees/new"]')
    expect(link.exists()).toBe(true)
    expect(link.text()).toContain('Nuovo Dipendente')
  })
})
