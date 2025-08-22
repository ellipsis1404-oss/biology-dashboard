<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '@/api/axios';
import ClassManager from '@/components/ClassManager.vue';
import StudentManager from '@/components/StudentManager.vue';
import TestManager from '@/components/TestManager.vue';

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
  <div>
    <header class="page-header">
      <h1>Admin Panel</h1>
      <p>Manage classes, students, tests, and scores from this page.</p>
    </header>
    <section class="admin-section">
      <h2>Manage Tests & Scores</h2>
      <div v-if="isLoadingClasses">Loading...</div>
      <TestManager v-else :classes="classes" />
    </section>
    <section class="admin-section">
      <h2>Manage Classes</h2>
      <ClassManager />
    </section>
    <section class="admin-section">
      <h2>Manage Students</h2>
      <div v-if="isLoadingClasses">Loading...</div>
      <StudentManager v-else :classes="classes" />
    </section>
  </div>
</template>

<style scoped>
.page-header {
  margin-bottom: 2rem;
}
.page-header h1 {
  border-bottom: 2px solid #76D7C4;
  padding-bottom: 10px;
}
.admin-section {
  background-color: #34495e;
  padding: 1.5rem;
  border-radius: 8px;
  margin-top: 2rem;
}
.admin-section h2 {
  margin-top: 0;
  color: #95a5a6;
  font-weight: 500;
  text-transform: uppercase;
  font-size: 0.9rem;
  letter-spacing: 1px;
  border-bottom: 1px solid #2c50;
  padding-bottom: 8px;
  margin-bottom: 1rem;
}
</style>