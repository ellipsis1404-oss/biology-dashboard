// frontend/src/router/index.js

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import HomeView from '../views/HomeView.vue'
import ClassDetailView from '../views/ClassDetailView.vue'
import AdminView from '../views/AdminView.vue'
import LoginView from '../views/LoginView.vue'

const routes = [
  // ... your routes array is correct, no changes needed here ...
  { path: '/', name: 'home', component: HomeView, meta: { requiresAuth: true } },
  { path: '/classes/:id', name: 'class-detail', component: ClassDetailView, meta: { requiresAuth: true } },
  { path: '/admin', name: 'admin', component: AdminView, meta: { requiresAuth: true } },
  { path: '/login', name: 'login', component: LoginView }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// --- IMPROVED Navigation Guard ---
router.beforeEach(async (to, from, next) => {
  // We need to ensure the auth store is initialized before we can check isAuthenticated
  const authStore = useAuthStore();
  
  // A simple check to see if the store has been initialized
  if (!authStore.token && localStorage.getItem('token')) {
    // If not, try to initialize it by reading from localStorage
    authStore.initializeStore();
  }

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  
  // If the route requires authentication AND the user is not logged in
  if (requiresAuth && !authStore.isAuthenticated) {
    // Redirect them to the login page
    next({ name: 'login' });
  } 
  // If the user tries to go to the login page but is already authenticated
  else if (to.name === 'login' && authStore.isAuthenticated) {
    // Redirect them to the dashboard
    next({ name: 'home' });
  } 
  // Otherwise, let them proceed
  else {
    next();
  }
});

export default router