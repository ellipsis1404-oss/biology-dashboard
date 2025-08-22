<script setup>
import { ref, watch } from 'vue';
import apiClient from '@/api/axios';

// --- PROPS & EMITS ---
const props = defineProps({
  studentId: { type: [Number, null], required: true },
});
const emit = defineEmits(['close']);

// --- COMPONENT STATE ---
const studentData = ref(null);
const isLoading = ref(false);
const error = ref(null);
const newCommentText = ref('');
const isSubmitting = ref(false);
const aiSummary = ref('');
const isGeneratingSummary = ref(false);

// State for the AI Comment Generator
const isGeneratingComment = ref(false);


// --- API & LOGIC METHODS ---
async function fetchStudentPerformance(id) {
  if (!id) return;
  isLoading.value = true;
  error.value = null;
  aiSummary.value = ''; // Clear old summary when opening
  try {
    const response = await apiClient.get(`/api/students/${id}/performance/`);
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
    const response = await apiClient.post('/api/comments/', {
      student: props.studentId, text: newCommentText.value
    });
    studentData.value.comments.unshift(response.data);
    newCommentText.value = '';
  } catch (err) { console.error("Failed to add comment:", err); } 
  finally { isSubmitting.value = false; }
}

async function generateAiSummary() {
  if (!studentData.value) return;
  isGeneratingSummary.value = true;
  aiSummary.value = '';
  try {
    const response = await apiClient.post('/api/students/generate_summary/', {
        student_info: studentData.value.student_info,
        standards_performance: studentData.value.standards_performance,
        comments: studentData.value.comments
    });
    aiSummary.value = response.data.summary;
  } catch (err) {
    aiSummary.value = "Sorry, an error occurred while generating the summary.";
    console.error("Failed to generate AI summary:", err);
  } finally {
    isGeneratingSummary.value = false;
  }
}

async function generateReportComment() {
  if (!studentData.value) return;
  isGeneratingComment.value = true;
  try {
    const response = await apiClient.post('/api/students/generate_comment/', {
        student_info: studentData.value.student_info,
        standards_performance: studentData.value.standards_performance,
    });
    newCommentText.value = response.data.comment;
  } catch (err) {
    console.error("Failed to generate AI comment:", err);
  } finally {
    isGeneratingComment.value = false;
  }
}

function printReport() {
    if (!studentData.value) return;

    let reportHTML = `
        <html>
        <head>
            <title>Student Report: ${studentData.value.student_info.first_name} ${studentData.value.student_info.last_name}</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 2rem; color: #333; }
                h1, h2 { border-bottom: 2px solid #eee; padding-bottom: 8px; }
                h3 { margin-top: 2rem; }
                table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
                th, td { border: 1px solid #ccc; padding: 10px; text-align: left; }
                th { background-color: #f2f2f2; }
                .summary { background-color: #f9f9f9; border: 1px solid #eee; border-radius: 5px; padding: 1rem; margin-top: 1rem; white-space: pre-wrap; }
                p { margin-top: 0; }
            </style>
        </head>
        <body>
            <h1>Student Progress Report</h1>
            <h2>${studentData.value.student_info.first_name} ${studentData.value.student_info.last_name}</h2>
    `;

    if (aiSummary.value) {
        reportHTML += `
            <h3>AI Generated Summary</h3>
            <div class="summary">${aiSummary.value.replace(/\*\*/g, '')}</div>
        `;
    }

    if (studentData.value.standards_performance.length) {
        reportHTML += '<h3>Standards Mastery</h3><table><thead><tr><th style="width: 15%;">Code</th><th>Description</th><th style="width: 15%;">Mastery</th></tr></thead><tbody>';
        studentData.value.standards_performance.forEach(s => {
            reportHTML += `<tr><td>${s.code}</td><td>${s.description}</td><td>${Math.round(s.percentage)}%</td></tr>`;
        });
        reportHTML += '</tbody></table>';
    }

    if (studentData.value.comments.length) {
        reportHTML += '<h3>Teacher Comments</h3>';
        // Show newest comments first
        [...studentData.value.comments].reverse().forEach(c => {
            reportHTML += `<p><strong>${new Date(c.created_at).toLocaleDateString()}:</strong> ${c.text}</p>`;
        });
    }

    reportHTML += '</body></html>';

    const printWindow = window.open('', '_blank');
    printWindow.document.write(reportHTML);
    printWindow.document.close();
    printWindow.print();
}

watch(() => props.studentId, (newId) => {
  if (newId) { fetchStudentPerformance(newId); } 
  else { studentData.value = null; newCommentText.value = ''; }
}, { immediate: true });
</script>

<template>
  <v-dialog :model-value="!!studentId" @update:model-value="!$event && emit('close')" fullscreen transition="dialog-bottom-transition">
    <v-card>
      <v-toolbar dark color="primary">
        <v-btn icon dark @click="emit('close')"><v-icon>mdi-close</v-icon></v-btn>
        <v-toolbar-title v-if="studentData">{{ studentData.student_info.first_name }} {{ studentData.student_info.last_name }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-items>
          <v-btn v-if="studentData" prepend-icon="mdi-printer" @click="printReport">Print Report</v-btn>
        </v-toolbar-items>
      </v-toolbar>

      <v-card-text>
        <div v-if="isLoading" class="text-center pa-10"><v-progress-circular indeterminate size="64"></v-progress-circular></div>
        <div v-else-if="error"><v-alert type="error">{{ error }}</v-alert></div>
        <v-container v-else-if="studentData">
          <v-row>
            <v-col cols="12" md="8">
              <!-- AI Summary Section -->
              <div class="section ai-section">
                <div class="ai-header">
                  <h3>AI Generated Summary</h3>
                  <v-btn @click="generateAiSummary" :loading="isGeneratingSummary" prepend-icon="mdi-sparkles">Generate Summary</v-btn>
                </div>
                <div v-if="isGeneratingSummary" class="summary-box"><p>Thinking...</p></div>
                <div v-if="aiSummary" class="summary-box" v-html="aiSummary.replace(/\*\*/g, (match, p1, offset) => (offset > 0 && aiSummary[offset - 1] === '*' ? '' : '<strong>')).replace(/\*\*/g, '</strong>').replace(/\n/g, '<br />')"></div>
              </div>

              <!-- Standards Mastery Section -->
              <div class="section">
                <h3>Standards Mastery</h3>
                <v-list lines="two" border>
                  <v-list-item v-for="standard in studentData.standards_performance" :key="standard.id">
                    <v-list-item-title>{{ standard.code }} - {{ standard.description }}</v-list-item-title>
                    <v-list-item-subtitle>{{ standard.unit }}</v-list-item-subtitle>
                    <template v-slot:append>
                      <v-progress-circular :model-value="standard.percentage" :color="standard.percentage > 70 ? 'success' : 'warning'">{{ Math.round(standard.percentage) }}</v-progress-circular>
                    </template>
                  </v-list-item>
                </v-list>
              </div>
            </v-col>
            <v-col cols="12" md="4">
              <!-- Comments Section -->
              <div class="section">
                <h3>Comments</h3>
                <v-form @submit.prevent="handleAddComment" class="comment-form">
                  <v-textarea v-model="newCommentText" label="Add or generate a comment..." rows="4" variant="outlined" required></v-textarea>
                  <div class="form-actions">
                    <v-btn @click="generateReportComment" :loading="isGeneratingComment" prepend-icon="mdi-auto-fix" variant="tonal">Generate</v-btn>
                    <v-spacer></v-spacer>
                    <v-btn type="submit" :loading="isSubmitting" color="primary">Save</v-btn>
                  </div>
                </v-form>

                <v-list lines="one">
                  <v-list-item v-for="comment in studentData.comments" :key="comment.id">
                    <v-list-item-title class="comment-text">{{ comment.text }}</v-list-item-title>
                    <v-list-item-subtitle>{{ new Date(comment.created_at).toLocaleDateString() }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item v-if="!studentData.comments.length">
                      <v-list-item-title>No comments recorded.</v-list-item-title>
                  </v-list-item>
                </v-list>
              </div>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.section { margin-bottom: 2rem; }
.section h3 { margin-bottom: 1rem; }
.ai-section { background-color: rgba(var(--v-theme-on-surface), 0.05); padding: 1.5rem; border-radius: 8px; }
.ai-header { display: flex; justify-content: space-between; align-items: center; }
.summary-box { margin-top: 1rem; }
.form-actions { display: flex; gap: 0.5rem; align-items: center; margin-top: -10px; margin-bottom: 10px; }
.comment-text { white-space: pre-wrap; }
</style>