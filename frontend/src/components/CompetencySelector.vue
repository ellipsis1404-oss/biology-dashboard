<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  standards: { type: Array, required: true },
  modelValue: { type: Array, required: true },
});
const emit = defineEmits(['update:modelValue']);

const isDialogOpen = ref(false);
const tempSelection = ref([]);
const activeLevel = ref(null);
const activeChapter = ref(null);
const activeUnit = ref(null);

// --- NEW: A 4-level nested data structure: Level -> Chapter -> Unit -> [Standards] ---
const structuredStandards = computed(() => {
  if (!props.standards.length) return {};
  // First, sort the standards correctly
  const sortedStandards = [...props.standards].sort((a, b) => {
    if (a.chapter_order !== b.chapter_order) return a.chapter_order - b.chapter_order;
    if (a.unit_order !== b.unit_order) return a.unit_order - b.unit_order;
    return a.code.localeCompare(b.code);
  });

  return sortedStandards.reduce((acc, standard) => {
    const level = standard.level || 'Uncategorized';
    const chapter = standard.chapter || 'Uncategorized';
    const unit = standard.unit || 'Uncategorized';
    if (!acc[level]) acc[level] = {};
    if (!acc[level][chapter]) acc[level][chapter] = {};
    if (!acc[level][chapter][unit]) acc[level][chapter][unit] = [];
    acc[level][chapter][unit].push(standard);
    return acc;
  }, {});
});

const levels = computed(() => Object.keys(structuredStandards.value));
const chapters = computed(() => {
  if (!activeLevel.value || !structuredStandards.value[activeLevel.value]) return [];
  return Object.keys(structuredStandards.value[activeLevel.value]);
});
const units = computed(() => {
  if (!activeLevel.value || !activeChapter.value || !structuredStandards.value[activeLevel.value][activeChapter.value]) return [];
  return Object.keys(structuredStandards.value[activeLevel.value][activeChapter.value]);
});
const competencies = computed(() => {
  if (!activeLevel.value || !activeChapter.value || !activeUnit.value || !structuredStandards.value[activeLevel.value][activeChapter.value][activeUnit.value]) return [];
  return structuredStandards.value[activeLevel.value][activeChapter.value][activeUnit.value];
});

// ... (standardsMap and selectedStandards are unchanged) ...
const standardsMap = computed(() => props.standards.reduce((map, s) => { map[s.id] = s; return map; }, {}));
const selectedStandards = computed(() => props.modelValue.map(id => standardsMap.value[id]).filter(Boolean));

function openDialog() {
  tempSelection.value = [...props.modelValue];
  if (!activeLevel.value && levels.value.length > 0) {
    activeLevel.value = levels.value[0];
  }
  isDialogOpen.value = true;
}
function confirmSelection() {
  emit('update:modelValue', tempSelection.value);
  isDialogOpen.value = false;
}
function cancelSelection() {
  isDialogOpen.value = false;
}

// --- NEW: More complex watchers for the 4-level cascade ---
watch(activeLevel, (newLevel) => {
    const newChapters = Object.keys(structuredStandards.value[newLevel] || {});
    activeChapter.value = newChapters.length > 0 ? newChapters[0] : null;
});
watch(activeChapter, (newChapter) => {
    if (!activeLevel.value) return;
    const newUnits = Object.keys(structuredStandards.value[activeLevel.value]?.[newChapter] || {});
    activeUnit.value = newUnits.length > 0 ? newUnits[0] : null;
});
watch(() => props.modelValue, (newValue) => {
    tempSelection.value = [...newValue];
});
</script>

<template>
  <div>
    <v-label>Associated Standards</v-label>
    <v-card @click="openDialog" variant="outlined" class="competency-input">
      <v-card-text>
        <v-chip v-for="standard in selectedStandards" :key="standard.id" class="ma-1" closable @click:close.stop="emit('update:modelValue', modelValue.filter(id => id !== standard.id))">
          {{ standard.code }}
        </v-chip>
        <span v-if="!selectedStandards.length" class="placeholder">Click to select competencies</span>
      </v-card-text>
    </v-card>

    <v-dialog v-model="isDialogOpen" max-width="1400px">
      <v-card class="dialog-card">
        <v-card-title>Select Competencies</v-card-title>
        <v-divider></v-divider>
        <v-card-text class="dialog-content-grid">
            <div class="column"><v-list-subheader>LEVEL</v-list-subheader><v-list class="scrollable-list" dense><v-list-item v-for="level in levels" :key="level" @click="activeLevel = level" :active="activeLevel === level" color="primary"><v-list-item-title>{{ level }}</v-list-item-title></v-list-item></v-list></div>
            <!-- NEW: Chapter Column -->
            <div class="column"><v-list-subheader>CHAPTER</v-list-subheader><v-list class="scrollable-list" dense><v-list-item v-for="chapter in chapters" :key="chapter" @click="activeChapter = chapter" :active="activeChapter === chapter" color="blue-lighten-2"><v-list-item-title class="unit-title">{{ chapter }}</v-list-item-title></v-list-item></v-list></div>
            <div class="column"><v-list-subheader>UNIT</v-list-subheader><v-list class="scrollable-list" dense><v-list-item v-for="unit in units" :key="unit" @click="activeUnit = unit" :active="activeUnit === unit" color="secondary"><v-list-item-title class="unit-title">{{ unit }}</v-list-item-title></v-list-item></v-list></div>
            <div class="column flex-grow"><v-list-subheader>COMPETENCIES</v-list-subheader><v-list class="scrollable-list" dense><v-list-item v-for="standard in competencies" :key="standard.id" @click.stop><template v-slot:prepend><v-checkbox-btn v-model="tempSelection" :value="standard.id"></v-checkbox-btn></template><v-tooltip location="end" :text="standard.description" max-width="400px"><template v-slot:activator="{ props }"><v-list-item-title v-bind="props">{{ standard.code }} - {{ standard.description }}</v-list-item-title></template></v-tooltip></v-list-item></v-list></div>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions><v-spacer></v-spacer><v-btn text @click="cancelSelection">Cancel</v-btn><v-btn color="primary" @click="confirmSelection">Confirm Selection</v-btn></v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
.competency-input { cursor: pointer; min-height: 56px; }
.competency-input:hover { border-color: rgba(var(--v-theme-on-surface), var(--v-high-emphasis-opacity)); }
.placeholder { color: grey; }
.unit-title { white-space: normal; }
.dialog-content-grid { display: flex; flex-direction: row; height: 60vh; max-height: 550px; }
.column { display: flex; flex-direction: column; height: 100%; border-right: 1px solid rgba(var(--v-theme-on-surface), 0.12); }
.column:last-child { border-right: none; }
.scrollable-list { flex-grow: 1; overflow-y: auto; }
/* --- NEW: Adjusted column widths for 4 columns --- */
.column:nth-child(1) { flex-basis: 15%; flex-shrink: 0; }
.column:nth-child(2) { flex-basis: 25%; flex-shrink: 0; }
.column:nth-child(3) { flex-basis: 25%; flex-shrink: 0; }
.column:nth-child(4) { flex-basis: 35%; flex-shrink: 0; }
</style>