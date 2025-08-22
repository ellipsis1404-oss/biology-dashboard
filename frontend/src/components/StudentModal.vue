<script setup>
import { ref, watch } from 'vue';
import axios from 'axios';

const props = defineProps({
  studentId: { type: [Number, null], required: true },
});
const emit = defineEmits(['close']);

const studentData = ref(null);
const isLoading = ref(false);
const error = ref(null);
const newCommentText = ref('');
const isSubmitting = ref(false);

// --- State for AI Summary ---
const aiSummary = ref('');
const isGeneratingSummary = ref(false);

async function fetchStudentPerformance(id) {
  if (!id) return;
  isLoading.value = true;
  error.value = null;
  aiSummary.value = ''; // Clear old summary when opening a new modal
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/students/${id}/performance/`);
    studentData.value = response.data;
  } catch (err) {
    error.value = "Failed to load student performance data.";
    console.error(err);
  } finally {
    isLoading.value = false;
  }
}

async function handleAddComment() {
  if (!newCommentText.value.trim() || !props.studentId) return;
  isSubmitting.value = true;
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/comments/', {
      student: props.studentId, text: newCommentText.value
    });
    studentData.value.comments.unshift(response.data);
    newCommentText.value = '';
  } catch (err) { console.error("Failed to add comment:", err); }
  finally { isSubmitting.value = false; }
}

// --- Function to call the AI backend endpoint ---
async function generateAiSummary() {
  if (!studentData.value) return;
  isGeneratingSummary.value = true;
  aiSummary.value = '';
  try {
    // We send the data we already have to our backend.
    const response = await axios.post('http://127.0.0.1:8000/api/students/generate_summary/', {
        student_info: studentData.value.student_info,
        standards_performance: studentData.value.standards_performance,
        comments: studentData.value.comments
    });
    aiSummary.value = response.data.summary;
  } catch (err) {
    aiSummary.value = "Sorry, an error occurred while generating the summary. Please check the Django server console for more details.";
    console.error("Failed to generate AI summary:", err);
  } finally {
    isGeneratingSummary.value = false;
  }
}

watch(() => props.studentId, (newId) => {
  if (newId) { fetchStudentPerformance(newId); }
  else { studentData.value = null; newCommentText.value = ''; }
}, { immediate: true });
</script>

<template>
  <div v-if="studentId" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content">
      <button class="close-btn" @click="emit('close')">&times;</button>
      
      <div v-if="isLoading">Loading student details...</div>
      <div v-else-if="error">{{ error }}</div>
      <div v-else-if="studentData">
        <header class="modal-header">
          <h2>{{ studentData.student_info.first_name }} {{ studentData.student_info.last_name }}</h2>
          <p>Performance Overview</p>
        </header>

        <div class="modal-body">
          <!-- === AI SUMMARY SECTION === -->
          <div class="section ai-section">
            <div class="ai-header">
                <h3>AI Generated Summary</h3>
                <button @click="generateAiSummary" :disabled="isGeneratingSummary">
                    {{ isGeneratingSummary ? 'Generating...' : '✨ Generate Summary' }}
                </button>
            </div>
            <div v-if="isGeneratingSummary" class="summary-box">Thinking...</div>
            <!-- The 'white-space: pre-wrap' style is important to respect line breaks from the AI -->
            <div v-if="aiSummary" class="summary-box">
                <p style="white-space: pre-wrap;">{{ aiSummary }}</p>
            </div>
          </div>

          <div class="section">
            <h3>Standards Mastery</h3>
            <ul class="standards-list">
              <li v-for="standard in studentData.standards_performance" :key="standard.id">
                <div class="standard-info">
                  <strong>{{ standard.code }}</strong> - {{ standard.description }}
                  <em>Unit: {{ standard.unit }}</em>
                </div>
                <div class="standard-score">
                  {{ Math.round(standard.percentage) }}%
                </div>
              </li>
            </ul>
          </div>

          <div class="section">
            <h3>Comments</h3>
            <form @submit.prevent="handleAddComment" class="comment-form">
              <textarea v-model="newCommentText" placeholder="Add a new comment..." required></textarea>
              <button type="submit" :disabled="isSubmitting">{{ isSubmitting ? 'Saving...' : 'Add Comment' }}</button>
            </form>
            <div v-if="studentData.comments.length > 0">
              <ul class="comments-list">
                <li v-for="comment in studentData.comments" :key="comment.id">
                  <p>{{ comment.text }}</p>
                  <span>{{ new Date(comment.created_at).toLocaleDateString() }}</span>
                </li>
              </ul>
            </div>
            <div v-else><p>No comments have been added for this student.</p></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay{position:fixed;top:0;left:0;width:100%;height:100%;background-color:rgba(0,0,0,.7);display:flex;justify-content:center;align-items:center;z-index:1000}.modal-content{background-color:#34495e;padding:2rem;border-radius:8px;width:80%;max-width:800px;max-height:90vh;overflow-y:auto;position:relative}.close-btn{position:absolute;top:10px;right:15px;background:none;border:none;font-size:2rem;color:#bdc3c7;cursor:pointer}.modal-header h2{margin-top:0}.section{margin-top:2rem}.section h3{border-bottom:1px solid #2c3e50;padding-bottom:8px;color:#95a5a6}.standards-list,.comments-list{list-style:none;padding:0}.standards-list li{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #2c3e50}.standard-info strong{color:#76D7C4}.standard-info em{display:block;font-size:.8em;color:#95a5a6;font-style:normal}.standard-score{font-size:1.5rem;font-weight:bold}.comments-list li{background-color:#2c3e50;padding:1rem;border-radius:5px;margin-bottom:10px}.comments-list li p{margin:0 0 8px 0}.comments-list li span{font-size:.8em;color:#95a5a6}.comment-form{display:flex;flex-direction:column;gap:10px;margin-bottom:1.5rem}.comment-form textarea{background-color:#2c3e50;border:1px solid #4a627f;border-radius:5px;color:#ecf0f1;padding:10px;font-family:inherit;min-height:80px}.comment-form button{align-self:flex-end;background-color:#16a085;color:white;border:none;padding:10px 15px;border-radius:5px;cursor:pointer;transition:background-color .2s ease}.comment-form button:hover{background-color:#1abc9c}.comment-form button:disabled{background-color:#95a5a6;cursor:not-allowed}

/* === STYLES FOR AI SECTION === */
.ai-section {
    background-color: rgba(0,0,0,0.2);
    padding: 1rem 1.5rem;
    border-radius: 8px;
    margin-top: 0;
}
.ai-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.ai-header button {
    background-color: #8e44ad;
    border: none;
    padding: 8px 15px;
    border-radius: 5px;
    cursor: pointer;
    color: white;
    font-weight: bold;
}
.ai-header button:disabled {
    background-color: #9b59b6;
    cursor: not-allowed;
}
.summary-box {
    background-color: #2c3e50;
    margin-top: 1rem;
    padding: 1rem;
    border-radius: 5px;
    color: #bdc3c7;
}
</style>