<script setup>
import { useRouter } from 'vue-router';

const props = defineProps({
  bioClass: { type: Object, required: true }
});
const router = useRouter();

function navigateToClassDetail() {
  router.push({ name: 'class-detail', params: { id: props.bioClass.id } });
}
</script>

<template>
  <v-card @click="navigateToClassDetail" hover>
    <v-card-title>{{ bioClass.name }}</v-card-title>
    <v-card-subtitle>{{ bioClass.description || 'No description provided.' }}</v-card-subtitle>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn append-icon="mdi-arrow-right" color="primary" variant="text">
        View Details
      </v-btn>
    </v-card-actions>
  </v-card>
</template>