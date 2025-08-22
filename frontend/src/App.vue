<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { useAuthStore } from './stores/auth';

const authStore = useAuthStore();

// Initialize the store on app startup
authStore.initializeStore();
</script>

<template>
  <v-app>
    <v-app-bar app>
      <v-app-bar-title>
        <RouterLink to="/" class="toolbar-title">
          Biology Progress Dashboard
        </RouterLink>
      </v-app-bar-title>
      <v-spacer></v-spacer>
      
      <!-- Only show these links if the user is authenticated -->
      <div v-if="authStore.isAuthenticated">
        <v-btn to="/" text>Dashboard</v-btn>
        <v-btn to="/classes" text>Classes</v-btn> 
        <v-btn to="/admin" text>Admin</v-btn>
        <v-btn @click="authStore.logout()" text>Logout</v-btn>
      </div>
    </v-app-bar>

    <v-main>
      <RouterView />
    </v-main>
  </v-app>
</template>

<style>
/* Global styles for our app */
body {
  background-color: #1E1E1E !important; /* Vuetify dark theme background */
}
.toolbar-title {
  color: inherit;
  text-decoration: none;
}
</style>