import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('@/components/HelloWorld.vue') },
  { path: '/pipe/:id', component: () => import('@/components/Pipe.vue'), props: true },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/components/404.vue') },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
})

export default router
