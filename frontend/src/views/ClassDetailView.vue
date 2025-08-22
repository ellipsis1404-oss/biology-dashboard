<script setup>
import { useRoute } from 'vue-router';
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/api/axios';
import BarChart from '@/components/BarChart.vue';
import StudentModal from '@/components/StudentModal.vue';

const route = useRoute();
const classId = ref(route.params.id);
const classData = ref(null);
const isLoading = ref(true);
const error = ref(null);
const selectedStudentId = ref(null);

function openStudentModal(studentId) {
  selectedStudentId.value = studentId;
}
function closeStudentModal() {
  selectedStudentId.value = null;
}

onMounted(async () => {
  try {
    const response = await apiClient.get(`/api/classes/${classId.value}/details/`);
    classData.value = response.data;
  } catch (err) {
    error.value = "Failed to load class details. Please try again later.";
    console.error(err);
  } finally {
    isLoading.value = false;
  }
});

const histogramChartData = computed(() => {
  if (!classData.value || !classData.value.summary.histogram_data) return null;
  return {
    labels: classData.value.summary.histogram_data.labels,
    datasets: [{
      label: 'Number of Students',
      backgroundColor: '#76D7C4',
      data: classData.value.summary.histogram_data.data
    }]
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    y: { beginAtZero: true, ticks: { stepSize: 1, color: '#ecf0f1' }, grid: { color: 'rgba(236, 240, 241, 0.1)' } },
    x: { ticks: { color: '#ecf0f1' }, grid: { color: 'rgba(236, 240, 241, 0.1)' } }
  }
};
</script>

<template>
  <div>
    <StudentModal :studentId="selectedStudentId" @close="closeStudentModal" />
    <div v-if="isLoading"><p>Loading class details...</p></div>
    <div v-else-if="error"><p class="error-message">{{ error }}</p></div>
    <div v-else-if="classData">
      <header class="page-header">
        <h1>{{ classData.class_info.name }}</h1>
        <p>{{ classData.class_info.description || 'Class details and overview.' }}</p>
      </header>
      <div class="content-grid">
        <div class="summary-section">
          <h2>Latest Test Summary</h2>
          <div v-if="classData.summary.message" class="info-box">{{ classData.summary.message }}</div>
          <div v-else class="summary-grid">
            <div class="summary-item"><strong>Class Average</strong><span>{{ classData.summary.average_score_percentage }}%</span></div>
            <div class="summary-item"><strong>Red Flags (&lt;70%)</strong><span>{{ classData.summary.red_flag_count }}</span></div>
            <div class="summary-item chart-container"><strong>Score Distribution</strong><BarChart v-if="histogramChartData" :chartData="histogramChartData" :chartOptions="chartOptions" /></div>
          </div>
        </div>
        <div class="student-list-section">
          <h2>Student Roster ({{ classData.students.length }})</h2>
          <ul class="student-list">
            <li v-for="student in classData.students" :key="student.id" class="student-item">
              <span>{{ student.first_name }} {{ student.last_name }}</span>
              <button class="view-btn" @click="openStudentModal(student.id)">View Progress</button>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header{margin-bottom:2rem}.page-header h1{border-bottom:2px solid #76D7C4;padding-bottom:10px;margin-bottom:.5rem}.page-header p{color:#bdc3c7;font-size:1.1rem}.content-grid{display:grid;grid-template-columns:2fr 1fr;gap: