// frontend/src/main.js

import { createApp } from 'vue'
import { createPinia } from 'pinia'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
// --- NEW: Import mdi icons ---
import '@mdi/font/css/materialdesignicons.css' 

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth' // Import the store

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'dark'
  },
  // --- NEW: Specify the icon font ---
  icons: {
    defaultSet: 'mdi',
  },
})

const app = createApp(App)

// Use Pinia FIRST
app.use(createPinia())

// --- NEW: Initialize the auth store right after creating Pinia ---
// This ensures the token is loaded from localStorage immediately.
const authStore = useAuthStore()
authStore.initializeStore()

// Now use the router and Vuetify
app.use(router)
app.use(vuetify)

app.mount('#app')