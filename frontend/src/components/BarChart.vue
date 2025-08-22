<script setup>
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';

// This registers the necessary components for Chart.js to work.
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

// This component expects to receive the chart data and options as props.
const props = defineProps({
  chartData: {
    type: Object,
    required: true
  },
  chartOptions: {
    type: Object,
    default: () => ({
      responsive: true,
      maintainAspectRatio: false,
    })
  }
});
</script>

<template>
  <Bar
    :data="chartData"
    :options="chartOptions"
  />
</template>