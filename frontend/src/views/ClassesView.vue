<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '@/api/axios';
import ClassSummaryCard from '@/components/ClassSummaryCard.vue';

const classes = ref([]);
const loadingError = ref(null);

onMounted(async () => {
  try {
    const response = await apiClient.get('/api/classes/');
    classes.value = response.data;
  } catch (error) {
    loadingError.value = "Failed to load the list of classes.";
    console.error(error);
  }
});
</script>

<template>
  <v-container fluid>
    <header class="page-header">
      <h1>All Classes</h1>
      <p>Select a class to view its detailed progress report.</p>
    </header>

    <div v-if="loadingError" class="error-message">{{ loadingError }}</div>
    <div v-else-if="!classes.length" class="text-center pa-4">
        <v-progress-circular indeterminate></v-progress-circular>
        <p>Loading classes...</p>
    </div>
    
    <v-row v-else>
      <v-col v-for="bioClass in classes" :key="bioClass.id" cols="12" md="6">
        <ClassSummaryCard :bioClass="bioClass" />
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.page-header {
  margin-bottom: 2rem;
}
.page-header h1 {
  border-bottom: 2px solid rgb(var(--v-theme-primary));
  padding-bottom: 10px;
}
.error-message {
  color: rgb(var(--v-theme-error));
}
</style>