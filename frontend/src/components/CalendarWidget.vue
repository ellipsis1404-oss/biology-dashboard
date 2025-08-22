<script setup>
import { ref } from 'vue';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import googleCalendarPlugin from '@fullcalendar/google-calendar';

// --- IMPORTANT: REPLACE THESE WITH YOUR OWN VALUES ---
const GOOGLE_CALENDAR_API_KEY = 'AIzaSyAPbZj8CPcD88_bDaX_xNrwGDxqHHIVA9s';
const GOOGLE_CALENDAR_ID = 'fd7c363825719579fcfcc17e4c237af700a9f54f37853b4a35cfd78792275c4b@group.calendar.google.com';
// ----------------------------------------------------

const calendarOptions = ref({
  plugins: [dayGridPlugin, googleCalendarPlugin],
  initialView: 'dayGridMonth',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,dayGridWeek'
  },
  // This is the magic part that connects to Google Calendar
  googleCalendarApiKey: GOOGLE_CALENDAR_API_KEY,
  events: {
    googleCalendarId: GOOGLE_CALENDAR_ID
  },
  // Styling to match our dark theme
  eventColor: '#1abc9c',
  height: 'auto', // Adjusts height to container
});
</script>

<template>
  <div class="calendar-container">
    <FullCalendar :options="calendarOptions" />
  </div>
</template>

<style>
/* FullCalendar's CSS is complex, so we apply some global overrides. */
/* We remove 'scoped' so these styles can affect the FullCalendar elements. */

.calendar-container {
    background-color: #34495e;
    padding: 1.5rem;
    border-radius: 8px;
}

/* Toolbar buttons */
.fc .fc-button-primary {
    background-color: #16a085;
    border-color: #16a085;
}
.fc .fc-button-primary:hover {
    background-color: #1abc9c;
    border-color: #1abc9c;
}

/* Calendar text color */
.fc {
    color: #ecf0f1;
}

/* Day header text color */
.fc .fc-col-header-cell-cushion {
    color: #bdc3c7;
    text-decoration: none;
}

/* Hide the border between header and content */
.fc .fc-scrollgrid-section-header > * {
    border-bottom-width: 0;
}
</style>