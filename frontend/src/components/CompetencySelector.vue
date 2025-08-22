<script setup>
import { ref, computed, watch } from 'vue';

// --- PROPS & EMITS ---
const props = defineProps({
  // The list of all possible standards/competencies
  standards: { type: Array, required: true },
  // The currently selected standard IDs (v-model)
  modelValue: { type: Array, required: true },
});

const emit = defineEmits(['update:modelValue']);

// --- COMPONENT STATE ---
const isDialogOpen = ref(false);
// A temporary list to hold selections inside the dialog without affecting the parent form
const tempSelection = ref([...props.modelValue]);
const activeUnit = ref(null);

// --- COMPUTED PROPERTIES ---
// This groups the standards by unit, which is the core logic
const groupedStandards = computed(() => {
  if (!props.standards.length) return {};
  const groups = props.standards.reduce((acc, standard) => {
    const unit = standard.unit || 'Uncategorized';
    if (!acc[unit]) acc[unit] = [];
    acc[unit].push(standard);
    return acc;
  }, {});
  // Set the first unit as the active one by default
  if (!activeUnit.value && Object.keys(groups).length > 0) {
    activeUnit.value = Object.keys(groups)[0];
  }
  return groups;
});

// A list of just the unit names for the buttons
const units = computed(() => Object.keys(groupedStandards.value));

// A map for quick lookup of standard details by ID
const standardsMap = computed(() => {
  return props.standards.reduce((map, standard) => {
    map[standard.id] = standard;
    return map;
  }, {});
});

// The full standard objects for the selected IDs, to display as chips
const selectedStandards = computed(() => {
  return props.modelValue.map(id => standardsMap.value[id]).filter(Boolean);
});

// --- METHODS ---
function openDialog() {
  // When opening, copy the current selection to the temporary state
  tempSelection.value = [...props.modelValue];
  isDialogOpen.value = true;
}

function confirmSelection() {
  // When confirming, emit the update to the parent (v-model)
  emit('update:modelValue', tempSelection.value);
  isDialogOpen.value = false;
}

function cancelSelection() {
  // When cancelling, do nothing and just close the dialog
  isDialogOpen.value = false;
}

// Watch for external changes to the modelValue and update the temp selection
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
          @click:close="emit('update:modelValue', modelValue.filter(id => id !== standard.id))"
        >
          {{ standard.code }}
        </v-chip>
        <span v-if="!selectedStandards.length" class="placeholder">Click to select competencies</span>
      </v-card-text>
    </v-card>

    <v-dialog v-model="isDialogOpen" max-width="900px" scrollable>
      <v-card>
        <v-card-title>Select Competencies</v-card-title>
        <v-divider></v-divider>

        <v-card-text style="height: 400px;">
          <v-row no-gutters>
            <!-- Left Column: Unit Selection -->
            <v-col cols="4">
              <v-list dense>
                <v-list-item
                  v-for="unit in units"
                  :key="unit"
                  @click="activeUnit = unit"
                  :active="activeUnit === unit"
                  color="primary"
                >
                  <v-list-item-title>{{ unit }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-col>

            <!-- Right Column: Competency Selection -->
            <v-divider vertical></v-divider>
            <v-col cols="8">
              <v-list dense>
                <v-list-item v-for="standard in groupedStandards[activeUnit]" :key="standard.id">
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
          <v-btn color="primary" @click="confirmSelection">Confirm</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
.competency-input {
  cursor: pointer;
  min-height: 56px; /* Match v-text-field height */
}
.competency-input:hover {
  border-color: #fff;
}
.placeholder {
  color: grey;
}
</style>