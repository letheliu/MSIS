import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('../views/Search.vue')
  },
  {
    path: '/templates',
    name: 'Templates',
    component: () => import('../views/Templates.vue')
  },
  {
    path: '/templates/:id/edit',
    name: 'TemplateEditor',
    component: () => import('../views/TemplateEditor.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
