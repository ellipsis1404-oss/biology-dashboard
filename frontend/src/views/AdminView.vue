<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '@/api/axios';
import ClassManager from '@/components/ClassManager.vue';
import StudentManager from '@/components/StudentManager.vue';
import TestManager from '@/components/TestManager.vue';

// This ref will control which tab is currently active.
const tab = ref('tests'); // Default to the 'tests' tab

// We still need to fetch the list of classes to pass to our child components.
const classes = ref([]);
const isLoadingClasses = ref(true);

async function fetchClasses() {
  try {
    const response = await apiClient.get('/api/classes/');
    classes.value = response.data;
  } catch (error) {
    console.error("Failed to load classes for admin view", error);
  } finally {
    isLoadingClasses.value = false;
  }
}

onMounted(fetchClasses);
</script>

<template>
  <!-- v-container is a Vuetify component for content layout -->
  <v-container fluid>
    <header class="page-header">
      <h1>Admin Panel</h1>
      <p>Manage classes, students, tests, and scores from this page.</p>
    </header>

    <!-- v-card provides a nice container for our tabs -->
    <v-card>
      <!-- v-tabs is the main component for the tab navigation -->
      <v-tabs v-model="tab" bg-color="primary" fixed-tabs>
        <v-tab value="tests">Tests & Scores</v-tab>
        <v-tab value="students">Students</v-tab>
        <v-tab value="classes">Classes</v-tab>
      </v-tabs>

      <!-- v-card-text will hold the content of the selected tab -->
      <v-card-text>
        <!-- v-window acts as a container for the different tab contents -->
        <v-window v-model="tab">
          
          <!-- Content for the "Tests & Scores" tab -->
          <v-window-item value="tests">
            <div v-if="isLoadingClasses">Loading class data...</div>
            <TestManager v-else :classes="classes" />
          </v-window-item>

          <!-- Content for the "Students" tab -->
          <v-window-item value="students">
            <div v-if="isLoadingClasses">Loading class data...</div>
            <StudentManager v-else :classes="classes" />
          </v-window-item>

          <!-- Content for the "Classes" tab -->
          <v-window-item value="classes">
            <div v-if="isLoadingClasses">Loading class data...</div>
            <ClassManager v-else :classes="classes" />
          </v-window-item>

        </v-window>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<style scoped>
.page-header {
  margin-bottom: 2rem;
}
.page-header h1 {
  /* Use Vuetify's theme color variables for a consistent look */
  border-bottom: 2px solid rgb(var(--v-theme-primary));
  padding-bottom: 10px;
}
</style>