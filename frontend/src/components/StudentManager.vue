<script setup>
import { ref, watch } from 'vue';
import apiClient from '@/api/axios';

const props = defineProps({
  classes: { type: Array, required: true },
});

// --- STATE MANAGEMENT ---
const selectedClassId = ref(null);
const students = ref([]);
const isLoading = ref(false);
const error = ref(null);

// Form for adding a new student
const newStudentForm = ref({ first_name: '', last_name: '' });

// --- NEW: State for the Edit Dialog ---
const isEditDialogOpen = ref(false); // Controls if the dialog is visible
const studentToEdit = ref(null); // Holds the data of the student being edited

// --- WATCHER ---
watch(selectedClassId, async (newId) => {
  if (newId) {
    await fetchStudents(newId);
  } else {
    students.value = [];
  }
});

// --- API METHODS ---
async function fetchStudents(classId) {
  isLoading.value = true;
  error.value = null;
  students.value = [];
  try {
    const response = await apiClient.get(`/api/students/?search=${classId}`);
    students.value = response.data;
  } catch (err) {
    error.value = "Failed to load students for this class.";
    console.error(err);
  } finally {
    isLoading.value = false;
  }
}

async function handleAddStudent() {
  if (!newStudentForm.value.first_name.trim() || !newStudentForm.value.last_name.trim()) {
    return;
  }
  try {
    await apiClient.post('/api/students/', {
      ...newStudentForm.value,
      biology_class: selectedClassId.value,
    });
    newStudentForm.value = { first_name: '', last_name: '' };
    await fetchStudents(selectedClassId.value);
  } catch (err) {
    alert('An error occurred while adding the student.');
    console.error(err);
  }
}

// --- NEW: Methods for Handling the Edit Dialog ---

// This function is called when the "Edit" button is clicked.
function openEditDialog(student) {
  // Make a copy of the student object to avoid modifying the list directly.
  studentToEdit.value = { ...student };
  isEditDialogOpen.value = true;
}

// This function is called when the "Save" button in the dialog is clicked.
async function handleUpdateStudent() {
  if (!studentToEdit.value || !studentToEdit.value.first_name.trim() || !studentToEdit.value.last_name.trim()) {
    return;
  }
  try {
    // Send a PUT request to update the student data.
    await apiClient.put(`/api/students/${studentToEdit.value.id}/`, studentToEdit.value);
    
    // Close the dialog and refresh the list to show the changes.
    isEditDialogOpen.value = false;
    await fetchStudents(selectedClassId.value);
  } catch (err) {
    alert('An error occurred while updating the student.');
    console.error(err);
  }
}
</script>

<template>
  <div class="manager-container">
    <!-- Class Selector Dropdown -->
    <div class="class-selector">
      <label for="class-select">Select a Class to Manage Students:</label>
      <v-select
        id="class-select"
        v-model="selectedClassId"
        :items="classes"
        item-title="name"
        item-value="id"
        label="-- Please choose a class --"
        dense
        solo
      ></v-select>
    </div>

    <!-- Student Management Content -->
    <div v-if="selectedClassId" class="student-content">
      <v-card>
        <v-card-title>Student Roster ({{ students.length }})</v-card-title>
        <v-card-text>
          <div v-if="isLoading">Loading students...</div>
          <div v-else-if="error" class="error-message">{{ error }}</div>
          <v-list v-else lines="one">
            <v-list-item v-for="student in students" :key="student.id">
              <v-list-item-title>{{ student.first_name }} {{ student.last_name }}</v-list-item-title>
              <template v-slot:append>
                <!-- NEW: Edit Button -->
                <v-btn icon="mdi-pencil" variant="text" size="small" @click="openEditDialog(student)"></v-btn>
              </template>
            </v-list-item>
          </v-list>
        </v-card-text>
      </v-card>

      <!-- Form to add a new student -->
      <v-card>
        <v-card-title>Add New Student to {{ classes.find(c => c.id === selectedClassId)?.name }}</v-card-title>
        <v-card-text>
          <v-form @submit.prevent="handleAddStudent">
            <v-text-field label="First Name" v-model="newStudentForm.first_name" required></v-text-field>
            <v-text-field label="Last Name" v-model="newStudentForm.last_name" required></v-text-field>
            <v-btn type="submit" color="primary">Add Student</v-btn>
          </v-form>
        </v-card-text>
      </v-card>
    </div>

    <!-- NEW: Edit Student Dialog (Modal) -->
    <v-dialog v-model="isEditDialogOpen" max-width="500px">
      <v-card>
        <v-card-title>Edit Student</v-card-title>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  label="First Name"
                  v-model="studentToEdit.first_name"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-text-field
                  label="Last Name"
                  v-model="studentToEdit.last_name"
                  required
                ></v-text-field>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="isEditDialogOpen = false">Cancel</v-btn>
          <v-btn color="primary" @click="handleUpdateStudent">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
.manager-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
.student-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}
.error-message { color: rgb(var(--v-theme-error)); }
</style>