<script setup>
import { useRouter } from 'vue-router';

// This component still accepts a 'bioClass' object as a prop.
const props = defineProps({
  bioClass: {
    type: Object,
    required: true
  }
});

// The useRouter() hook gives us access to the router instance,
// which we can use to navigate programmatically.
const router = useRouter();

function navigateToClassDetail() {
  // Use router.push to navigate to the 'class-detail' route,
  // passing the class ID as a parameter.
  router.push({ name: 'class-detail', params: { id: props.bioClass.id } });
}
</script>

<template>
  <!-- When this div is clicked, it will call our navigation function -->
  <div class="card" @click="navigateToClassDetail">
    <div class="card-header">
      <h3>{{ bioClass.name }}</h3>
      <span>Click to view details &rarr;</span>
    </div>
  </div>
</template>

<style scoped>
/* The styling remains largely the same, just simplified */
.card {
  background-color: #34495e;
  border-radius: 8px;
  margin-bottom: 1rem;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
  background-color: #46627f;
}
.card-header {
  padding: 1.5rem; /* A bit more padding for a cleaner look */
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-header h3 {
  margin: 0;
}
.card-header span {
  font-size: 0.9em;
  color: #bdc3c7;
}
</style>