<script setup>
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/api/axios';
import CalendarWidget from '@/components/CalendarWidget.vue';
import BarChart from '@/components/BarChart.vue'; // We reuse our chart component

// --- STATE ---
const dashboardData = ref(null);
const isLoading = ref(true);
const error = ref(null);

// --- DATA FETCHING ---
onMounted(async () => {
  try {
    const response = await apiClient.get('/api/dashboard-stats/');
    dashboardData.value = response.data;
  } catch (err) {
    error.value = "Failed to load dashboard statistics.";
    console.error(err);
  } finally {
    isLoading.value = false;
  }
});

// --- COMPUTED for Chart ---
const performanceChartData = computed(() => {
  if (!dashboardData.value || !dashboardData.value.class_performance_chart) {
    return null;
  }
  return {
    labels: dashboardData.value.class_performance_chart.labels,
    datasets: [
      {
        label: 'Average Score (%) on Latest Test',
        backgroundColor: '#3498db',
        borderColor: '#2980b9',
        data: dashboardData.value.class_performance_chart.data,
      }
    ]
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y', // Makes it a horizontal bar chart, which is better for comparing categories
  plugins: {
    legend: {
      display: true,
    },
    title: {
        display: true,
        text: 'Class Performance Comparison'
    }
  },
  scales: {
    x: {
        beginAtZero: true,
        max: 100, // Scores are percentages
        ticks: { color: 'rgba(255,255,255,0.7)' },
    },
    y: {
        ticks: { color: 'rgba(255,255,255,0.7)' },
    }
  }
};

</script>

<template>
  <v-container fluid>
    <header class="page-header">
      <h1>Dashboard</h1>
      <p>Welcome! Here is your at-a-glance overview.</p>
    </header>
    
    <div v-if="isLoading" class="text-center pa-4">
        <v-progress-circular indeterminate></v-progress-circular>
    </div>
    <div v-else-if="error" class="error-message">{{ error }}</div>

    <v-row v-else>
      <!-- Main Content Column -->
      <v-col cols="12" md="7">
        <v-card class="fill-height">
            <v-card-text>
                <!-- We render the BarChart component with our new data -->
                <BarChart v-if="performanceChartData" :chartData="performanceChartData" :chartOptions="chartOptions" />
            </v-card-text>
        </v-card>
      </v-col>

      <!-- Calendar Column -->
      <v-col cols="12" md="5">
        <v-card>
            <v-card-title>Calendar & Events</v-card-title>
            <v-card-text>
                <CalendarWidget />
            </v-card-text>
        </v-card>
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
.fill-height {
    height: 100%;
}
.error-message {
  color: rgb(var(--v-theme-error));
}
</style>