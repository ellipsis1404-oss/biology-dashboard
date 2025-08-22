<script setup>
import { ref, watch, computed } from 'vue';
import apiClient from '@/api/axios';

const props = defineProps({
  classes: { type: Array, required: true },
});

const selectedClassId = ref(null);
const tests = ref([]);
const students = ref([]);
const standards = ref([]);
const selectedTest = ref(null);
const scores = ref({});
const isLoading = ref(false);
const newTestForm = ref({ title: '', date_administered: new Date().toISOString().split('T')[0] });
const newQuestionForm = ref({ question_text: '', max_mark: 1, standards: [] });

const selectedClass = computed(() => props.classes.find(c => c.id === selectedClassId.value));
const selectedTestDetails = computed(() => tests.value.find(t => t.id === selectedTest.value?.id));

// --- WATCHER IS NOW ASYNC ---
watch(selectedTest, async (newTest) => {
  if (newTest) {
    // 1. Build the empty grid structure first.
    const newScores = {};
    students.value.forEach(student => {
      newScores[student.id] = {};
      newTest.questions.forEach(question => {
        newScores[student.id][question.id] = ''; // Default to empty string
      });
    });

    // --- NEW: Fetch existing scores and populate the grid ---
    try {
      const response = await apiClient.get(`/api/tests/${newTest.id}/scores/`);
      const existingScores = response.data;
      
      // 2. Loop through the fetched scores and fill in the grid.
      existingScores.forEach(score => {
        // Safety check to make sure the student and question still exist
        if (newScores[score.student] && newScores[score.student][score.question] !== undefined) {
          newScores[score.student][score.question] = score.mark_awarded;
        }
      });
    } catch (err) {
      console.error("Could not fetch existing scores:", err);
    }
    
    // 3. Set the final, populated scores object.
    scores.value = newScores;
  }
});

watch(selectedClassId, async (newId) => {
  selectedTest.value = null; tests.value = []; students.value = []; scores.value = {};
  if (newId) {
    await fetchTests(newId);
    await fetchStudents(newId);
    await fetchStandards();
  }
});


// ... The rest of the script (all the async functions) remains exactly the same ...
async function fetchTests(classId) {
  isLoading.value = true;
  try {
    const response = await apiClient.get(`/api/tests/?search=${classId}`);
    tests.value = response.data;
  } catch (err) { console.error("Failed to fetch tests:", err); } 
  finally { isLoading.value = false; }
}
async function fetchStudents(classId) {
  try {
    const response = await apiClient.get(`/api/students/?search=${classId}`);
    students.value = response.data;
  } catch (err) { console.error("Failed to fetch students:", err); }
}
async function fetchStandards() {
  if (standards.value.length > 0) return;
  try {
    const response = await apiClient.get('/api/standards/');
    standards.value = response.data;
  } catch (err) { console.error("Failed to fetch standards:", err); }
}
async function handleCreateTest() {
  if (!newTestForm.value.title.trim()) return;
  try {
    await apiClient.post('/api/tests/', {
      ...newTestForm.value,
      assigned_class: selectedClassId.value,
    });
    newTestForm.value.title = '';
    await fetchTests(selectedClassId.value);
  } catch (err) { console.error("Failed to create test:", err); }
}
async function handleAddQuestion() {
  if (!newQuestionForm.value.question_text.trim() || !selectedTest.value) return;
  try {
    await apiClient.post('/api/questions/', {
      ...newQuestionForm.value,
      test: selectedTest.value.id,
    });
    newQuestionForm.value = { question_text: '', max_mark: 1, standards: [] };
    const currentlySelectedTestId = selectedTest.value.id;
    await fetchTests(selectedClassId.value);
    selectedTest.value = tests.value.find(t => t.id === currentlySelectedTestId);
  } catch (err) { console.error("Failed to add question:", err); }
}
async function handleSaveScores() {
  if (!selectedTest.value) return;
  try {
    await apiClient.post(`/api/tests/${selectedTest.value.id}/bulk_score_entry/`, {
      scores: scores.value
    });
    alert('Scores saved successfully!');
  } catch (err) {
    alert('Failed to save scores. Check console for details.');
    console.error("Failed to save scores:", err);
  }
}
</script>

<template>
    <!-- The template for this component remains exactly the same -->
    <div>
        <div class="step-container">
            <h3>Step 1: Select a Class</h3>
            <select v-model="selectedClassId">
                <option :value="null" disabled>-- Choose a class --</option>
                <option v-for="bioClass in classes" :key="bioClass.id" :value="bioClass.id">{{ bioClass.name }}</option>
            </select>
        </div>
        <div v-if="selectedClassId">
            <div class="step-container">
                <h3>Step 2: Create or Select a Test for {{ selectedClass.name }}</h3>
                <div class="form-grid">
                    <form @submit.prevent="handleCreateTest" class="form-card">
                        <h4>Create New Test</h4>
                        <input type="text" v-model="newTestForm.title" placeholder="Test Title (e.g., Unit 1 Exam)" required /><input type="date" v-model="newTestForm.date_administered" required /><button type="submit">Create Test</button>
                    </form>
                    <div class="test-selection-card">
                        <h4>Select Existing Test</h4>
                        <div v-if="isLoading">Loading tests...</div>
                        <select v-model="selectedTest" v-else>
                            <option :value="null" disabled>-- Choose a test --</option>
                            <option v-for="test in tests" :key="test.id" :value="test">{{ test.title }} ({{ test.date_administered }})</option>
                        </select>
                    </div>
                </div>
            </div>
            <div v-if="selectedTest">
                <div class="step-container">
                    <h3>Step 3: Add Questions to "{{ selectedTest.title }}"</h3>
                    <div class="questions-section">
                        <ul class="question-list">
                            <li v-for="q in selectedTestDetails?.questions" :key="q.id">{{ q.question_text }} ({{ q.max_mark }} marks)</li>
                            <li v-if="!selectedTestDetails?.questions.length">No questions added yet.</li>
                        </ul>
                        <form @submit.prevent="handleAddQuestion" class="form-card">
                            <h4>Add New Question</h4>
                            <input type="text" v-model="newQuestionForm.question_text" placeholder="Question Text" required /><input type="number" v-model="newQuestionForm.max_mark" placeholder="Max Mark" min="1" required /><label>Associated Standards (Hold Ctrl/Cmd to select multiple)</label>
                            <select multiple v-model="newQuestionForm.standards">
                                <option v-for="s in standards" :key="s.id" :value="s.id">{{ s.code }} - {{ s.description.substring(0, 50) }}...</option>
                            </select><button type="submit">Add Question</button>
                        </form>
                    </div>
                </div>
                <div class="step-container">
                    <h3>Step 4: Enter Scores</h3>
                    <div v-if="students.length && selectedTestDetails?.questions.length" class="score-grid-container">
                        <table class="score-table">
                            <thead>
                                <tr>
                                    <th>Student Name</th>
                                    <th v-for="q in selectedTestDetails.questions" :key="q.id">{{ q.question_text }} (Max: {{ q.max_mark }})</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="student in students" :key="student.id">
                                    <td>{{ student.first_name }} {{ student.last_name }}</td>
                                    <td v-for="q in selectedTestDetails.questions" :key="q.id"><input type="number" v-model="scores[student.id][q.id]" :max="q.max_mark" min="0" /></td>
                                </tr>
                            </tbody>
                        </table><button @click="handleSaveScores" class="save-scores-btn">Save All Scores</button>
                    </div>
                    <p v-else>Please add students to this class and questions to this test to enter scores.</p>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* All styles from before remain the same */
.step-container{background-color:#2c3e50;padding:1.5rem;border-radius:8px;margin-bottom:2rem}select,input[type="text"],input[type="date"],input[type="number"],button{padding:10px;border-radius:4px;border:1px solid #4a627f;background-color:#34495e;color:#ecf0f1;width:100%;box-sizing:border-box}select[multiple]{height:100px}button{background-color:#16a085;cursor:pointer;border-color:#16a085}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem}.form-card{display:flex;flex-direction:column;gap:1rem}.questions-section{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem}.question-list{list-style-type:none;padding:0;margin:0}.question-list li{padding:8px;background-color:#34495e;border-radius:4px;margin-bottom:5px}.score-grid-container{overflow-x:auto}.score-table{width:100%;border-collapse:collapse;margin-top:1rem}.score-table th,.score-table td{padding:8px;border:1px solid #4a627f;text-align:center}.score-table th{white-space:nowrap}.score-table td:first-child{text-align:left;white-space:nowrap}.score-table input{width:60px;text-align:center}.save-scores-btn{margin-top:1.5rem;width:auto;padding:12px 20px}
label { font-size: 0.9em; color: #bdc3c7; margin-bottom: -5px; }
</style>