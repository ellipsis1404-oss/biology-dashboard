<script setup>
import { ref, watch } from 'vue';
import axios from 'axios';

// This component receives the list of all classes as a "prop" from its parent (AdminView).
const props = defineProps({
  classes: {
    type: Array,
    required: true,
  },
});

// Reactive state
const selectedClassId = ref(null);
const students = ref([]);
const isLoading = ref(false);
const error = ref(null);

// Form state for adding a new student
const form = ref({
  first_name: '',
  last_name: '',
});

// A "watcher" that automatically fetches students whenever the selectedClassId changes.
watch(selectedClassId, async (newId) => {
  if (newId) {
    await fetchStudents(newId);
  } else {
    students.value = []; // Clear the list if no class is selected
  }
});

async function fetchStudents(classId) {
  isLoading.value = true;
  error.value = null;
  students.value = [];
  try {
    // We use the new '?search=' parameter to filter by class ID
    const response = await axios.get(`http://127.0.0.1:8000/api/students/?search=${classId}`);
    students.value = response.data;
  } catch (err) {
    error.value = "Failed to load students for this class.";
    console.error(err);
  } finally {
    isLoading.value = false;
  }
}

// Function to handle adding a new student
async function handleAddStudent() {
  if (!form.value.first_name.trim() || !form.value.last_name.trim()) {
    alert('Both first and last name are required.');
    return;
  }
  if (!selectedClassId.value) {
    alert('Please select a class first.');
    return;
  }

  try {
    // POST the new student data, including the ID of the class they belong to.
    await axios.post('http://127.0.0.1:8000/api/students/', {
      ...form.value,
      biology_class: selectedClassId.value,
    });
    // Reset the form and refresh the student list
    form.value = { first_name: '', last_name: '' };
    await fetchStudents(selectedClassId.value);
  } catch (err) {
    alert('An error occurred while adding the student.');
    console.error(err);
  }
}
</script>

<template>
  <div class="manager-container">
    <!-- Class Selector Dropdown -->
    <div class="class-selector">
      <label for="class-select">Select a Class to Manage Students:</label>
      <select id="class-select" v-model="selectedClassId">
        <option :value="null" disabled>-- Please choose a class --</option>
        <option v-for="bioClass in classes" :key="bioClass.id" :value="bioClass.id">
          {{ bioClass.name }}
        </option>
      </select>
    </div>

    <!-- This content only shows after a class has been selected -->
    <div v-if="selectedClassId" class="student-content">
      <div v-if="isLoading">Loading students...</div>
      <div v-else-if="error" class="error-message">{{ error }}</div>
      
      <!-- List of students in the selected class -->
      <div v-else class="student-list">
        <h4>Student Roster ({{ students.length }})</h4>
        <ul v-if="students.length > 0">
          <li v-for="student in students" :key="student.id">
            {{ student.first_name }} {{ student.last_name }}
          </li>
        </ul>
        <p v-else>No students have been added to this class yet.</p>
      </div>

      <!-- Form to add a new student -->
      <div class="form-container">
        <h4>Add New Student to {{ classes.find(c => c.id === selectedClassId)?.name }}</h4>
        <form @submit.prevent="handleAddStudent">
          <div class="form-group">
            <label for="first_name">First Name</label>
            <input type="text" id="first_name" v-model="form.first_name" required />
          </div>
          <div class="form-group">
            <label for="last_name">Last Name</label>
            <input type="text" id="last_name" v-model="form.last_name" required />
          </div>
          <button type="submit" class="btn-primary">Add Student</button>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.class-selector {
  margin-bottom: 2rem;
}
.class-selector label {
  display: block;
  margin-bottom: 0.5rem;
}
.class-selector select {
  width: 100%;
  padding: 10px;
  background-color: #2c3e50;
  border: 1px solid #4a627f;
  color: #ecf0f1;
  border-radius: 4px;
}

.student-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.student-list ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
  background-color: #2c3e50;
  border-radius: 4px;
}
.student-list li {
  padding: 12px;
  border-bottom: 1px solid #34495e;
}
.student-list li:last-child {
  border-bottom: none;
}
.student-list h4, .form-container h4 {
  margin-top: 0;
}

.form-group {
  margin-bottom: 1rem;
}
label {
  display: block;
  margin-bottom: 5px;
  color: #bdc3c7;
}
input[type="text"] {
  width: 100%;
  padding: 10px;
  background-color: #34495e;
  border: 1px solid #4a627f;
  border-radius: 4px;
  color: #ecf0f1;
  box-sizing: border-box;
}
.btn-primary {
  background-color: #16a085;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
}
</style>