import { defineStore } from 'pinia'
import apiClient from '@/api/axios'
import router from '@/router'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(credentials) {
      try {
        // The relative URL path to the login endpoint.
        // This will be appended to the baseURL from apiClient.
        // Final URL: http://127.0.0.1:8000/api/auth/login/
        const response = await apiClient.post('/api/auth/login/', credentials);
        const token = response.data.key;

        this.token = token;
        localStorage.setItem('token', token);
        apiClient.defaults.headers.common['Authorization'] = `Token ${token}`;
        
        // Use replace so the user can't click "back" to the login page
        router.replace({ name: 'home' });
      } catch (error) {
        this.logout();
        throw error;
      }
    },

    logout() {
      this.token = null;
      localStorage.removeItem('token');
      delete apiClient.defaults.headers.common['Authorization'];
      router.push('/login');
    },

    initializeStore() {
      if (this.token) {
        apiClient.defaults.headers.common['Authorization'] = `Token ${this.token}`;
      }
    }
  }
})