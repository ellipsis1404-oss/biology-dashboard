<script setup>
import CalendarWidget from '@/components/CalendarWidget.vue';
</script>

<template>
  <v-container fluid>
    <header class="page-header">
      <h1>Dashboard</h1>
      <p>Welcome! Here is your at-a-glance overview.</p>
    </header>
    
    <v-row>
      <!-- Main Content Column -->
      <v-col cols="12" md="7">
        <v-card>
            <v-card-title>Quick Stats</v-card-title>
            <v-card-text>
                <p>High-level statistics and summary graphs will be displayed here soon.</p>
                <!-- We will add new charts here in the next step -->
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
</style>