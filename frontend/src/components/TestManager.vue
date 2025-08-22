<script setup>
import { ref, watch } from 'vue';
import apiClient from '@/api/axios';
import CompetencySelector from './CompetencySelector.vue';

const props = defineProps({
  classes: { type: Array, required: true },
});

const selectedClassId = ref(null);
const tests = ref([]);
const students = ref([]);
const standards = ref([]);
const selectedTestId = ref(null);
const selectedTestDetails = ref(null);
const scores = ref({});
const isLoadingTests = ref(false);
const isLoadingDetails = ref(false);
const showArchived = ref(false);
const isConfirmDialogOpen = ref(false);
const testToAction = ref(null);
const actionType = ref('');

const newTestForm = ref({ title: '', date_administered: new Date().toISOString().split('T')[0], test_file_link: '' });
const newQuestionForm = ref({ question_number: 1, question_text: '', max_mark: 1, standards: [] });
const isQuestionEditDialogOpen = ref(false);
const questionToEdit = ref(null);
const isTestEditDialogOpen = ref(false);
const testToEdit = ref(null);
const isScoringDialogOpen = ref(false);
const questionToScore = ref(null);
const singleQuestionScores = ref({});

watch(selectedClassId, async (newId) => {
  selectedTestId.value = null; selectedTestDetails.value = null; tests.value = []; students.value = []; scores.value = {};
  if (newId) { await fetchTests(newId); await fetchStudents(newId); await fetchStandards(); }
});
watch(selectedTestId, async (newId) => {
    selectedTestDetails.value = null; scores.value = {};
    if (newId) { await fetchTestDetails(newId); }
});
watch(showArchived, () => {
    if (selectedClassId.value) { fetchTests(selectedClassId.value); }
});
watch(selectedTestDetails, async (newTest) => {
  if (newTest && newTest.questions) {
    const newScores = {}; students.value.forEach(student => { newScores[student.id] = {}; newTest.questions.forEach(question => { newScores[student.id][question.id] = ''; }); });
    scores.value = newScores;
    try {
      const response = await apiClient.get(`/api/tests/${newTest.id}/scores/`);
      response.data.forEach(score => { if (scores.value[score.student] && scores.value[score.student][score.question] !== undefined) { scores.value[score.student][score.question] = score.mark_awarded; } });
    } catch (err) { console.error("Could not fetch existing scores:", err); }
  }
});

async function fetchTests(classId) {
  isLoadingTests.value = true;
  try {
    const params = { search: classId };
    if (showArchived.value) { params.include_archived = 'true'; }
    const response = await apiClient.get(`/api/tests/`, { params });
    tests.value = response.data;
  } catch (err) { console.error("Failed to fetch tests:", err); } 
  finally { isLoadingTests.value = false; }
}
async function fetchTestDetails(testId) {
    isLoadingDetails.value = true;
    try { const response = await apiClient.get(`/api/tests/${testId}/`); selectedTestDetails.value = response.data; }
    catch (err) { console.error("Failed to fetch test details:", err); }
    finally { isLoadingDetails.value = false; }
}
async function fetchStudents(classId) {
  try { const response = await apiClient.get(`/api/students/?search=${classId}`); students.value = response.data; }
  catch (err) { console.error("Failed to fetch students:", err); }
}
async function fetchStandards() {
  if (standards.value.length > 0) return;
  try { const response = await apiClient.get('/api/standards/'); standards.value = response.data; }
  catch (err) { console.error("Failed to fetch standards:", err); }
}
async function handleCreateTest() {
  if (!newTestForm.value.title.trim()) return;
  try {
    const response = await apiClient.post('/api/tests/', { ...newTestForm.value, assigned_class: selectedClassId.value });
    newTestForm.value = { title: '', date_administered: new Date().toISOString().split('T')[0], test_file_link: '' };
    await fetchTests(selectedClassId.value);
    selectedTestId.value = response.data.id;
  } catch (err) { console.error("Failed to create test:", err); }
}
async function handleAddQuestion() {
  if (!newQuestionForm.value.question_text.trim() || !selectedTestDetails.value) return;
  try {
    await apiClient.post('/api/questions/', { ...newQuestionForm.value, test: selectedTestDetails.value.id });
    const nextQNum = (selectedTestDetails.value.questions?.length || 0) + 2;
    newQuestionForm.value = { question_number: nextQNum, question_text: '', max_mark: 1, standards: [] };
    await fetchTestDetails(selectedTestDetails.value.id);
  } catch (err) { console.error("Failed to add question:", err); }
}
async function handleUpdateQuestion() {
  if (!questionToEdit.value) return;
  try {
    const payload = { ...questionToEdit.value, standards: questionToEdit.value.standards || [] };
    await apiClient.put(`/api/questions/${questionToEdit.value.id}/`, payload);
    isQuestionEditDialogOpen.value = false;
    await fetchTestDetails(selectedTestDetails.value.id);
  } catch (err) { alert('Failed to update question.'); console.error(err); }
}
function openQuestionEditDialog(question) {
  questionToEdit.value = { ...question, standards: question.standards ? [...question.standards] : [] };
  isQuestionEditDialogOpen.value = true;
}
async function handleUpdateTest() {
    if (!testToEdit.value) return;
    try {
        await apiClient.put(`/api/tests/${testToEdit.value.id}/`, testToEdit.value);
        isTestEditDialogOpen.value = false;
        await fetchTests(selectedClassId.value);
        await fetchTestDetails(testToEdit.value.id);
    } catch (err) { alert('Failed to update test.'); console.error(err); }
}
function openTestEditDialog() {
    if (!selectedTestDetails.value) return;
    testToEdit.value = { ...selectedTestDetails.value };
    isTestEditDialogOpen.value = true;
}
function openScoringDialog(question) {
  questionToScore.value = question;
  const newSingleScores = {};
  students.value.forEach(student => {
    newSingleScores[student.id] = scores.value[student.id]?.[question.id] || '';
  });
  singleQuestionScores.value = newSingleScores;
  isScoringDialogOpen.value = true;
}
async function handleSaveSingleQuestionScores() {
  if (!questionToScore.value || !selectedTestDetails.value) return;
  const payload = {};
  Object.keys(singleQuestionScores.value).forEach(studentId => {
    payload[studentId] = {
      [questionToScore.value.id]: singleQuestionScores.value[studentId]
    };
  });
  try {
    await apiClient.post(`/api/tests/${selectedTestDetails.value.id}/bulk_score_entry/`, {
      scores: payload
    });
    Object.keys(singleQuestionScores.value).forEach(studentId => {
        scores.value[studentId][questionToScore.value.id] = singleQuestionScores.value[studentId];
    });
    isScoringDialogOpen.value = false;
  } catch (err) {
    alert('Failed to save scores.');
    console.error(err);
  }
}
async function handleSaveScores() {
  if (!selectedTestDetails.value) return;
  try {
    await apiClient.post(`/api/tests/${selectedTestDetails.value.id}/bulk_score_entry/`, { scores: scores.value });
    alert('Scores saved successfully!');
  } catch (err) { alert('Failed to save scores. Check console for details.'); console.error("Failed to save scores:", err); }
}
function openConfirmDialog(test, type) {
    testToAction.value = test;
    actionType.value = type;
    isConfirmDialogOpen.value = true;
}
async function confirmAction() {
    if (!testToAction.value) return;
    try {
        if (actionType.value === 'archive') {
            await apiClient.delete(`/api/tests/${testToAction.value.id}/`);
        } else if (actionType.value === 'restore') {
            await apiClient.post(`/api/tests/${testToAction.value.id}/restore/`);
        }
        if (selectedTestId.value === testToAction.value.id) {
            selectedTestId.value = null;
        }
        await fetchTests(selectedClassId.value);
    } catch (err) {
        alert(`Failed to ${actionType.value} test.`);
        console.error(err);
    } finally {
        isConfirmDialogOpen.value = false;
        testToAction.value = null;
    }
}
</script>

<template>
  <div class="main-layout">
    <v-card class="mb-6">
      <v-card-title>Step 1: Select a Class</v-card-title>
      <v-card-text><v-select v-model="selectedClassId" :items="classes" item-title="name" item-value="id" label="-- Choose a class --" dense variant="outlined" hide-details></v-select></v-card-text>
    </v-card>

    <v-card v-if="selectedClassId" class="mb-6">
      <v-card-title>Step 2: Manage Tests for {{ classes.find(c => c.id === selectedClassId)?.name }}</v-card-title>
      <v-row class="pa-4">
        <v-col cols="12" md="5">
            <v-form @submit.prevent="handleCreateTest">
              <v-text-field v-model="newTestForm.title" label="New Test Title" variant="outlined" class="mb-2"></v-text-field>
              <v-text-field v-model="newTestForm.date_administered" label="Date Administered" type="date" variant="outlined" class="mb-2"></v-text-field>
              <v-text-field v-model="newTestForm.test_file_link" label="Google Drive Link (Optional)" variant="outlined" class="mb-2"></v-text-field>
              <v-btn type="submit" color="primary">Create Test</v-btn>
            </v-form>
        </v-col>
        <v-col cols="12" md="7">
            <v-list border>
                <v-list-subheader class="d-flex justify-space-between">
                    <span>Existing Tests</span>
                    <v-switch v-model="showArchived" label="Show Archived" color="secondary" dense hide-details class="flex-grow-0"></v-switch>
                </v-list-subheader>
                <div v-if="isLoadingTests" class="text-center pa-4"><v-progress-circular indeterminate size="24"></v-progress-circular></div>
                <v-list-item
                    v-for="test in tests"
                    :key="test.id"
                    @click="selectedTestId = test.id"
                    :active="selectedTestId === test.id"
                    :disabled="test.is_archived"
                    color="primary"
                >
                    <v-list-item-title>{{ test.title }}</v-list-item-title>
                    <v-list-item-subtitle>{{ test.date_administered }} <v-chip v-if="test.is_archived" size="x-small" color="grey">Archived</v-chip></v-list-item-subtitle>
                    <template v-slot:append>
                        <v-btn v-if="!test.is_archived" icon="mdi-archive-arrow-down-outline" variant="text" size="small" @click.stop="openConfirmDialog(test, 'archive')"></v-btn>
                        <v-btn v-else icon="mdi-archive-arrow-up-outline" variant="text" size="small" @click.stop="openConfirmDialog(test, 'restore')"></v-btn>
                    </template>
                </v-list-item>
                <v-list-item v-if="!tests.length && !isLoadingTests"><v-list-item-title>No tests found for this class.</v-list-item-title></v-list-item>
            </v-list>
            <v-btn v-if="selectedTestId" @click="openTestEditDialog" color="secondary" class="mt-4">Edit Selected Test</v-btn>
        </v-col>
      </v-row>
    </v-card>

    <div v-if="isLoadingDetails" class="text-center pa-4"><v-progress-circular indeterminate></v-progress-circular></div>
    <div v-else-if="selectedTestDetails">
      <v-card class="mb-6">
        <v-card-title>Step 3: Add & Edit Questions for "{{ selectedTestDetails.title }}"</v-card-title>
        <v-row class="pa-4">
          <v-col cols="12" md="7">
            <v-list lines="two" border><v-list-subheader>Question List</v-list-subheader><v-list-item v-for="q in selectedTestDetails.questions" :key="q.id"><v-list-item-title>Q{{ q.question_number }}: {{ q.question_text }}</v-list-item-title><v-list-item-subtitle>Max Mark: {{ q.max_mark }}</v-list-item-subtitle><template v-slot:append><v-btn icon="mdi-clipboard-edit-outline" variant="text" size="small" @click.stop="openScoringDialog(q)"></v-btn><v-btn icon="mdi-pencil" variant="text" size="small" @click.stop="openQuestionEditDialog(q)"></v-btn></template></v-list-item><v-list-item v-if="!selectedTestDetails.questions.length"><v-list-item-title>No questions added yet.</v-list-item-title></v-list-item></v-list>
          </v-col>
          <v-col cols="12" md="5">
            <v-form @submit.prevent="handleAddQuestion"><v-text-field label="Question Number" v-model.number="newQuestionForm.question_number" type="number" min="1" required variant="outlined" class="mb-4"></v-text-field><v-text-field label="Question Text" v-model="newQuestionForm.question_text" required variant="outlined" class="mb-4"></v-text-field><v-text-field label="Max Mark" v-model.number="newQuestionForm.max_mark" type="number" min="1" required variant="outlined" class="mb-4"></v-text-field><CompetencySelector v-model="newQuestionForm.standards" :standards="standards" class="mb-4" /><v-btn type="submit" color="primary">Add Question</v-btn></v-form>
          </v-col>
        </v-row>
      </v-card>
      <v-card>
        <v-card-title>Step 4: Enter Scores (Bulk)</v-card-title>
        <v-card-text>
          <div v-if="students.length && selectedTestDetails.questions.length" class="score-grid-container">
            <v-table density="compact">
              <thead><tr><th class="text-left">Student Name</th><th v-for="q in selectedTestDetails.questions" :key="q.id" class="text-center">Q{{ q.question_number }} ({{ q.max_mark }})</th></tr></thead>
              <tbody><tr v-for="student in students" :key="student.id"><td>{{ student.first_name }} {{ student.last_name }}</td><td v-for="q in selectedTestDetails.questions" :key="q.id"><v-text-field v-model.number="scores[student.id][q.id]" :max="q.max_mark" min="0" type="number" density="compact" hide-details variant="outlined"></v-text-field></td></tr></tbody>
            </v-table>
            <v-btn @click="handleSaveScores" color="primary" class="mt-4">Save All Scores</v-btn>
          </div>
          <p v-else>Please add students to this class and questions to this test to enter scores.</p>
        </v-card-text>
      </v-card>
    </div>
    
    <v-dialog v-model="isQuestionEditDialogOpen" max-width="600px">
      <v-card v-if="questionToEdit">
        <v-card-title>Edit Question</v-card-title>
        <v-card-text><v-container><v-row><v-col cols="12" sm="3"><v-text-field label="Q Number" v-model.number="questionToEdit.question_number" type="number" min="1" required></v-text-field></v-col><v-col cols="12" sm="9"><v-text-field label="Question Text" v-model="questionToEdit.question_text" required></v-text-field></v-col><v-col cols="12"><v-text-field label="Max Mark" v-model.number="questionToEdit.max_mark" type="number" min="1" required></v-text-field></v-col><v-col cols="12"><CompetencySelector v-model="questionToEdit.standards" :standards="standards" /></v-col></v-row></v-container></v-card-text>
        <v-card-actions><v-spacer></v-spacer><v-btn text @click="isQuestionEditDialogOpen = false">Cancel</v-btn><v-btn color="primary" @click="handleUpdateQuestion">Save</v-btn></v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="isTestEditDialogOpen" max-width="600px">
        <v-card v-if="testToEdit">
            <v-card-title>Edit Test</v-card-title>
            <v-card-text><v-text-field v-model="testToEdit.title" label="Test Title" variant="outlined" class="mb-2"></v-text-field><v-text-field v-model="testToEdit.date_administered" label="Date Administered" type="date" variant="outlined" class="mb-2"></v-text-field><v-text-field v-model="testToEdit.test_file_link" label="Google Drive Link (Optional)" variant="outlined" class="mb-2"></v-text-field></v-card-text>
            <v-card-actions><v-spacer></v-spacer><v-btn text @click="isTestEditDialogOpen = false">Cancel</v-btn><v-btn color="primary" @click="handleUpdateTest">Save</v-btn></v-card-actions>
        </v-card>
    </v-dialog>
    <v-dialog v-model="isScoringDialogOpen" max-width="600px" scrollable>
        <v-card v-if="questionToScore">
            <v-card-title>Enter Scores for: Q{{ questionToScore.question_number }}</v-card-title>
            <v-card-subtitle>{{ questionToScore.question_text }} (Max Mark: {{ questionToScore.max_mark }})</v-card-subtitle>
            <v-divider class="mt-2"></v-divider>
            <v-card-text style="max-height: 400px;">
                <v-list>
                    <v-list-item v-for="student in students" :key="student.id">
                        <v-list-item-title>{{ student.first_name }} {{ student.last_name }}</v-list-item-title>
                        <template v-slot:append>
                            <v-text-field v-model.number="singleQuestionScores[student.id]" type="number" :max="questionToScore.max_mark" min="0" density="compact" hide-details variant="outlined" style="width: 80px"></v-text-field>
                        </template>
                    </v-list-item>
                </v-list>
            </v-card-text>
            <v-divider></v-divider>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn text @click="isScoringDialogOpen = false">Cancel</v-btn>
                <v-btn color="primary" @click="handleSaveSingleQuestionScores">Save Scores</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
    <v-dialog v-model="isConfirmDialogOpen" max-width="500px">
        <v-card v-if="testToAction">
            <v-card-title class="text-h5">Confirm {{ actionType }}</v-card-title>
            <v-card-text>
                Are you sure you want to {{ actionType }} the test "{{ testToAction.title }}"?
                <div v-if="actionType === 'archive'" class="mt-2">Its scores will be hidden but not deleted.</div>
                <div v-if="actionType === 'restore'" class="mt-2">It will become active and visible again.</div>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn text @click="isConfirmDialogOpen = false">Cancel</v-btn>
                <v-btn :color="actionType === 'archive' ? 'error' : 'success'" @click="confirmAction">Confirm</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
.main-layout { display: flex; flex-direction: column; gap: 1.5rem; }
.score-grid-container { overflow-x: auto; }
.v-table th { white-space: nowrap; }
</style>