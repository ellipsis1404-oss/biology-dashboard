<script setup>
import { ref, watch, computed } from 'vue';
import apiClient from '@/api/axios';

// --- PROPS ---
const props = defineProps({
  classes: { type: Array, required: true },
});

// --- STATE MANAGEMENT ---
const selectedClassId = ref(null);
const tests = ref([]);
const students = ref([]);
const standards = ref([]);
const selectedTest = ref(null);
const scores = ref({});
const isLoading = ref(false);

// --- FORM STATE ---
const newTestForm = ref({ title: '', date_administered: new Date().toISOString().split('T')[0] });
const newQuestionForm = ref({ question_number: 1, question_text: '', max_mark: 1, standards: [] });

// --- NEW: State for the Question Edit Dialog ---
const isQuestionEditDialogOpen = ref(false);
const questionToEdit = ref(null);

// --- COMPUTED PROPERTIES ---
const selectedClass = computed(() => props.classes.find(c => c.id === selectedClassId.value));
const selectedTestDetails = computed(() => tests.value.find(t => t.id === selectedTest.value?.id));

// --- WATCHERS ---
watch(selectedTest, async (newTest) => {
  if (newTest) {
    const newScores = {};
    students.value.forEach(student => {
      newScores[student.id] = {};
      newTest.questions.forEach(question => { newScores[student.id][question.id] = ''; });
    });

    try {
      const response = await apiClient.get(`/api/tests/${newTest.id}/scores/`);
      const existingScores = response.data;
      existingScores.forEach(score => {
        if (newScores[score.student] && newScores[score.student][score.question] !== undefined) {
          newScores[score.student][score.question] = score.mark_awarded;
        }
      });
    } catch (err) { console.error("Could not fetch existing scores:", err); }
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

// --- API METHODS ---
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
    // Set the next question number automatically
    const nextQuestionNumber = (selectedTestDetails.value?.questions.length || 0) + 2;
    newQuestionForm.value = { question_number: nextQuestionNumber, question_text: '', max_mark: 1, standards: [] };
    await refreshCurrentTest();
  } catch (err) { console.error("Failed to add question:", err); }
}

// --- NEW: Methods for Handling Question Edit Dialog ---
function openQuestionEditDialog(question) {
  // We need to pass just the IDs for the standards to the v-select
  questionToEdit.value = { ...question, standards: question.standards.map(s => s.id || s) };
  isQuestionEditDialogOpen.value = true;
}

async function handleUpdateQuestion() {
  if (!questionToEdit.value) return;
  try {
    // The question API endpoint expects a list of standard IDs.
    await apiClient.put(`/api/questions/${questionToEdit.value.id}/`, questionToEdit.value);
    isQuestionEditDialogOpen.value = false;
    await refreshCurrentTest();
  } catch (err) {
    alert('Failed to update question.');
    console.error(err);
  }
}

// --- NEW: Helper function to refresh the current test details ---
async function refreshCurrentTest() {
    const currentlySelectedTestId = selectedTest.value.id;
    await fetchTests(selectedClassId.value);
    selectedTest.value = tests.value.find(t => t.id === currentlySelectedTestId);
}

</script>

<template>
  <div>
    <!-- Step 1: Select a Class (No changes) -->
    <v-container>
      <h3>Step 1: Select a Class</h3>
      <v-select
        v-model="selectedClassId"
        :items="classes"
        item-title="name"
        item-value="id"
        label="-- Choose a class --"
        dense
      ></v-select>
    </v-container>

    <div v-if="selectedClassId">
      <!-- Step 2: Create or Select a Test (No changes) -->
      <v-container>
        <h3>Step 2: Create or Select a Test for {{ selectedClass.name }}</h3>
        <v-row>
          <v-col cols="12" md="6">
            <v-card>
              <v-card-title>Create New Test</v-card-title>
              <v-card-text>
                <v-form @submit.prevent="handleCreateTest">
                  <v-text-field v-model="newTestForm.title" label="Test Title (e.g., Unit 1 Exam)" required></v-text-field>
                  <v-text-field v-model="newTestForm.date_administered" label="Date Administered" type="date" required></v-text-field>
                  <v-btn type="submit" color="primary">Create Test</v-btn>
                </v-form>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="6">
             <v-card>
                <v-card-title>Select Existing Test</v-card-title>
                <v-card-text>
                    <v-select v-model="selectedTest" :items="tests" item-title="title" return-object label="-- Choose a test --" dense></v-select>
                </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>

      <div v-if="selectedTest">
        <!-- Step 3: Add/Edit Questions -->
        <v-container>
          <h3>Step 3: Add & Edit Questions for "{{ selectedTest.title }}"</h3>
          <v-row>
            <v-col cols="12" md="7">
                <v-card>
                    <v-card-title>Question List</v-card-title>
                    <v-list lines="two">
                        <v-list-item v-for="q in selectedTestDetails?.questions" :key="q.id">
                           <v-list-item-title>Q{{ q.question_number }}: {{ q.question_text }}</v-list-item-title>
                           <v-list-item-subtitle>Max Mark: {{ q.max_mark }}</v-list-item-subtitle>
                           <template v-slot:append>
                                <v-btn icon="mdi-pencil" variant="text" size="small" @click="openQuestionEditDialog(q)"></v-btn>
                           </template>
                        </v-list-item>
                         <v-list-item v-if="!selectedTestDetails?.questions.length">
                            <v-list-item-title>No questions added yet.</v-list-item-title>
                        </v-list-item>
                    </v-list>
                </v-card>
            </v-col>
            <v-col cols="12" md="5">
              <v-card>
                <v-card-title>Add New Question</v-card-title>
                <v-card-text>
                    <v-form @submit.prevent="handleAddQuestion">
                      <v-text-field label="Question Number" v-model.number="newQuestionForm.question_number" type="number" min="1" required></v-text-field>
                      <v-text-field label="Question Text" v-model="newQuestionForm.question_text" required></v-text-field>
                      <v-text-field label="Max Mark" v-model.number="newQuestionForm.max_mark" type="number" min="1" required></v-text-field>
                      <v-select label="Associated Standards" v-model="newQuestionForm.standards" :items="standards" item-title="code" item-value="id" multiple chips></v-select>
                      <v-btn type="submit" color="primary">Add Question</v-btn>
                    </v-form>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
        
        <!-- Step 4: Bulk Score Entry (No changes) -->
        <v-container>
          <h3>Step 4: Enter Scores</h3>
          <v-card>
            <v-card-text>
              <div v-if="students.length && selectedTestDetails?.questions.length" class="score-grid-container">
                <v-table density="compact">
                  <thead>
                    <tr>
                      <th class="text-left">Student Name</th>
                      <th v-for="q in selectedTestDetails.questions" :key="q.id" class="text-center">Q{{ q.question_number }} ({{ q.max_mark }})</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="student in students" :key="student.id">
                      <td>{{ student.first_name }} {{ student.last_name }}</td>
                      <td v-for="q in selectedTestDetails.questions" :key="q.id">
                        <v-text-field v-model.number="scores[student.id][q.id]" :max="q.max_mark" min="0" type="number" density="compact" hide-details></v-text-field>
                      </td>
                    </tr>
                  </tbody>
                </v-table>
                <v-btn @click="handleSaveScores" color="primary" class="mt-4">Save All Scores</v-btn>
              </div>
              <p v-else>Please add students to this class and questions to this test to enter scores.</p>
            </v-card-text>
          </v-card>
        </v-container>
      </div>
    </div>

    <!-- NEW: Edit Question Dialog -->
    <v-dialog v-model="isQuestionEditDialogOpen" max-width="600px">
      <v-card v-if="questionToEdit">
        <v-card-title>Edit Question</v-card-title>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12" sm="3">
                <v-text-field label="Q Number" v-model.number="questionToEdit.question_number" type="number" min="1" required></v-text-field>
              </v-col>
              <v-col cols="12" sm="9">
                <v-text-field label="Question Text" v-model="questionToEdit.question_text" required></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-text-field label="Max Mark" v-model.number="questionToEdit.max_mark" type="number" min="1" required></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-select label="Associated Standards" v-model="questionToEdit.standards" :items="standards" item-title="code" item-value="id" multiple chips></v-select>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="isQuestionEditDialogOpen = false">Cancel</v-btn>
          <v-btn color="primary" @click="handleUpdateQuestion">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
.score-grid-container {
  overflow-x: auto;
}
.score-table input {
  width: 60px;
  text-align: center;
}
.v-table th {
    white-space: nowrap;
}
</style>