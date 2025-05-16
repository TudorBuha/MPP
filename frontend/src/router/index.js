import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../components/Login.vue'
import ContactList from '../components/ContactList.vue'
import AdminDashboard from '../components/AdminDashboard.vue'

const routes = [
  {
    path: '/login',
    name: 'LoginPage',
    component: LoginPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Home',
    component: ContactList,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  // If route requires auth and user is not logged in
  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }

  // If route requires admin and user is not admin
  if (to.meta.requiresAdmin && user.role !== 'admin') {
    next('/')
    return
  }

  // If user is logged in and tries to access login page
  if (to.path === '/login' && token) {
    next(user.role === 'admin' ? '/admin' : '/')
    return
  }

  next()
})

export default router 