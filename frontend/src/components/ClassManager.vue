<script setup>
import { ref, onMounted } from 'vue';
// --- CHANGED: Import our custom apiClient instead of the generic axios ---
import apiClient from '@/api/axios';

// Reactive state
const classes = ref([]);
const isLoading = ref(true);
const error = ref(null);

// State for the form (for adding or editing a class)
const isEditing = ref(false);
const form = ref({
  id: null,
  name: '',
  description: ''
});

// Fetch all classes when the component is mounted
async function fetchClasses() {
  isLoading.value = true;
  error.value = null;
  try {
    // --- CHANGED: Use apiClient and a relative URL ---
    const response = await apiClient.get('/api/classes/');
    classes.value = response.data;
  } catch (err) {
    error.value = "Failed to load classes.";
    console.error(err);
  } finally {
    isLoading.value = false;
  }
}

onMounted(fetchClasses);

// Function to reset the form to its default state
function resetForm() {
  isEditing.value = false;
  form.value = { id: null, name: '', description: '' };
}

// Function to set up the form for editing an existing class
function handleEdit(bioClass) {
  isEditing.value = true;
  form.value = { ...bioClass };
}

// Function to handle form submission (for both creating and updating)
async function handleSubmit() {
  const { id, name, description } = form.value;
  if (!name.trim()) {
    alert('Class name is required.');
    return;
  }

  try {
    if (isEditing.value) {
      // --- CHANGED: Use apiClient and a relative URL ---
      await apiClient.put(`/api/classes/${id}/`, { name, description });
    } else {
      // --- CHANGED: Use apiClient and a relative URL ---
      await apiClient.post('/api/classes/', { name, description });
    }
    // After successful submission, reset the form and refresh the class list
    resetForm();
    await fetchClasses();
  } catch (err) {
    alert('An error occurred. Please check the console.');
    console.error(err);
  }
}
</script>

<template>
  <div class="manager-container">
    <div v-if="isLoading">Loading...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    
    <!-- List of existing classes -->
    <div v-else class="class-list">
      <table>
        <thead>
          <tr>
            <th>Class Name</th>
            <th>Description</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="bioClass in classes" :key="bioClass.id">
            <td>{{ bioClass.name }}</td>
            <td>{{ bioClass.description }}</td>
            <td>
              <button @click="handleEdit(bioClass)" class="btn-edit">Edit</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Form for adding/editing a class -->
    <div class="form-container">
      <h3>{{ isEditing ? 'Edit Class' : 'Add New Class' }}</h3>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="name">Class Name</label>
          <input type="text" id="name" v-model="form.name" required />
        </div>
        <div class="form-group">
          <label for="description">Description (Optional)</label>
          <textarea id="description" v-model="form.description"></textarea>
        </div>
        <div class="form-actions">
          <button type="submit" class="btn-primary">{{ isEditing ? 'Update Class' : 'Save Class' }}</button>
          <button v-if="isEditing" @click="resetForm" type="button" class="btn-secondary">Cancel Edit</button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
/* All styles from before remain the same */
.manager-container{display:grid;grid-template-columns:2fr 1fr;gap:2rem}table{width:100%;border-collapse:collapse}th,td{padding:12px;text-align:left;border-bottom:1px solid #2c3e50}th{color:#95a5a6;font-size:.9rem}.btn-edit{background-color:#2980b9;color:white;border:none;padding:6px 10px;border-radius:4px;cursor:pointer}.form-container{background-color:#2c3e50;padding:1.5rem;border-radius:8px}h3{margin-top:0}.form-group{margin-bottom:1rem}label{display:block;margin-bottom:5px;color:#bdc3c7}input[type="text"],textarea{width:100%;padding:10px;background-color:#34495e;border:1px solid #4a627f;border-radius:4px;color:#ecf0f1;box-sizing:border-box}.form-actions{display:flex;gap:10px;margin-top:1.5rem}.btn-primary{background-color:#16a085;color:white;border:none;padding:10px 15px;border-radius:5px;cursor:pointer}.btn-secondary{background-color:#95a5a6;color:#2c3e50;border:none;padding:10px 15px;border-radius:5px;cursor:pointer}
.error-message { color: #e74c3c; }
</style>