<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import ClassSummaryCard from '@/components/ClassSummaryCard.vue';
import CalendarWidget from '@/components/CalendarWidget.vue'; // <-- Import the new widget
import apiClient from '@/api/axios';


const response = await apiClient.get('/api/classes/');

const classes = ref([]);
const loadingError = ref(null);

onMounted(async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/classes/');
    classes.value = response.data;
  } catch (error) {
    loadingError.value = "Failed to load the list of classes. Is the server running?";
    console.error(loadingError.value, error);
  }
});
</script>

<template>
  <div>
    <!-- The main layout is now a grid -->
    <div class="dashboard-grid">
      <div class="class-list-section">
        <h2>Classes</h2>
        <div v-if="loadingError">{{ loadingError }}</div>
        <div v-else-if="classes.length === 0">Loading classes...</div>
        <div v-else class="class-cards-container">
          <ClassSummaryCard 
            v-for="bioClass in classes" 
            :key="bioClass.id" 
            :bioClass="bioClass"
          />
        </div>
      </div>
      
      <!-- The new calendar section -->
      <div class="calendar-section">
        <h2>Calendar & Events</h2>
        <CalendarWidget />
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr; /* Two equal columns */
  gap: 2rem;
}

.class-list-section h2, .calendar-section h2 {
  color: #95a5a6;
  font-weight: 500;
  text-transform: uppercase;
  font-size: 0.9rem;
  letter-spacing: 1px;
  border-bottom: 1px solid #34495e;
  padding-bottom: 8px;
  margin-top: 0;
  margin-bottom: 1rem;
}
</style>