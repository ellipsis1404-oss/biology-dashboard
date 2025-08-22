<script setup>
import { ref, computed, watch } from 'vue';

// --- PROPS & EMITS ---
const props = defineProps({
  standards: { type: Array, required: true },
  modelValue: { type: Array, required: true },
});

const emit = defineEmits(['update:modelValue']);

// --- COMPONENT STATE ---
const isDialogOpen = ref(false);
const tempSelection = ref([...props.modelValue]);
const activeLevel = ref(null); // e.g., 'IGCSE'
const activeUnit = ref(null); // e.g., 'Cell Structure'


// --- COMPUTED PROPERTIES ---
// This is the core logic. A nested data structure: Level -> Unit -> [Standards]
const structuredStandards = computed(() => {
  if (!props.standards.length) return {};
  return props.standards.reduce((acc, standard) => {
    const level = standard.level || 'Uncategorized';
    const unit = standard.unit || 'Uncategorized';
    
    if (!acc[level]) acc[level] = {};
    if (!acc[level][unit]) acc[level][unit] = [];
    
    acc[level][unit].push(standard);
    return acc;
  }, {});
});

// A list of the top-level keys (e.g., ['IGCSE', 'AS', 'A2'])
const levels = computed(() => Object.keys(structuredStandards.value));

// A list of units for the currently selected level
const units = computed(() => {
  if (!activeLevel.value || !structuredStandards.value[activeLevel.value]) return [];
  return Object.keys(structuredStandards.value[activeLevel.value]);
});

// The list of competencies for the selected level and unit
const competencies = computed(() => {
  if (!activeLevel.value || !activeUnit.value || !structuredStandards.value[activeLevel.value][activeUnit.value]) return [];
  return structuredStandards.value[activeLevel.value][activeUnit.value];
});

// A map for quick lookup of standard details by ID (for the chips)
const standardsMap = computed(() => {
  return props.standards.reduce((map, standard) => {
    map[standard.id] = standard;
    return map;
  }, {});
});

const selectedStandards = computed(() => {
  return props.modelValue.map(id => standardsMap.value[id]).filter(Boolean);
});


// --- METHODS ---
function openDialog() {
  tempSelection.value = [...props.modelValue];
  // Set default active level and unit if not already set
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

// Watchers to handle selections changing
watch(activeLevel, (newLevel) => {
    // When the level changes, select the first unit of that new level
    const newUnits = Object.keys(structuredStandards.value[newLevel] || {});
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
        <v-chip
          v-for="standard in selectedStandards"
          :key="standard.id"
          class="ma-1"
          closable
          @click:close.stop="emit('update:modelValue', modelValue.filter(id => id !== standard.id))"
        >
          {{ standard.code }}
        </v-chip>
        <span v-if="!selectedStandards.length" class="placeholder">Click to select competencies</span>
      </v-card-text>
    </v-card>

    <!-- The dialog now has a 3-column layout -->
    <v-dialog v-model="isDialogOpen" max-width="1200px" scrollable>
      <v-card>
        <v-card-title>Select Competencies</v-card-title>
        <v-divider></v-divider>

        <v-card-text style="height: 500px;">
          <v-row no-gutters class="fill-height">
            <!-- Column 1: Level Selection -->
            <v-col cols="3">
              <v-list dense>
                <v-list-subheader>LEVEL</v-list-subheader>
                <v-list-item
                  v-for="level in levels"
                  :key="level"
                  @click="activeLevel = level"
                  :active="activeLevel === level"
                  color="primary"
                >
                  <v-list-item-title>{{ level }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-col>
            <v-divider vertical></v-divider>

            <!-- Column 2: Unit Selection -->
            <v-col cols="4">
              <v-list dense>
                <v-list-subheader>UNIT</v-list-subheader>
                <v-list-item
                  v-for="unit in units"
                  :key="unit"
                  @click="activeUnit = unit"
                  :active="activeUnit === unit"
                  color="secondary"
                >
                  <v-list-item-title class="unit-title">{{ unit }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-col>
            <v-divider vertical></v-divider>
            
            <!-- Column 3: Competency Selection -->
            <v-col cols="5">
               <v-list dense>
                <v-list-subheader>COMPETENCIES</v-list-subheader>
                <v-list-item v-for="standard in competencies" :key="standard.id">
                  <template v-slot:prepend>
                    <v-checkbox-btn v-model="tempSelection" :value="standard.id"></v-checkbox-btn>
                  </template>
                  <v-list-item-title>{{ standard.code }} - {{ standard.description }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-col>
          </v-row>
        </v-card-text>

        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="cancelSelection">Cancel</v-btn>
          <v-btn color="primary" @click="confirmSelection">Confirm Selection</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
.competency-input { cursor: pointer; min-height: 56px; }
.competency-input:hover { border-color: rgba(var(--v-theme-on-surface), var(--v-high-emphasis-opacity)); }
.placeholder { color: grey; }
.unit-title { white-space: normal; } /* Allow unit titles to wrap */
.fill-height { height: 100%; }
</style>