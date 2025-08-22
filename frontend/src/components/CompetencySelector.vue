<script setup>
// The <script> section is unchanged and correct.
import { ref, computed, watch } from 'vue';
const props = defineProps({ standards: { type: Array, required: true }, modelValue: { type: Array, required: true } });
const emit = defineEmits(['update:modelValue']);
const isDialogOpen = ref(false);
const tempSelection = ref([...props.modelValue]);
const activeLevel = ref(null);
const activeUnit = ref(null);
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
const levels = computed(() => Object.keys(structuredStandards.value));
const units = computed(() => {
  if (!activeLevel.value || !structuredStandards.value[activeLevel.value]) return [];
  return Object.keys(structuredStandards.value[activeLevel.value]);
});
const competencies = computed(() => {
  if (!activeLevel.value || !activeUnit.value || !structuredStandards.value[activeLevel.value][activeUnit.value]) return [];
  return structuredStandards.value[activeLevel.value][activeUnit.value];
});
const standardsMap = computed(() => {
  return props.standards.reduce((map, standard) => {
    map[standard.id] = standard;
    return map;
  }, {});
});
const selectedStandards = computed(() => {
  return props.modelValue.map(id => standardsMap.value[id]).filter(Boolean);
});
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
watch(activeLevel, (newLevel) => {
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

    <v-dialog v-model="isDialogOpen" max-width="1200px">
      <v-card>
        <v-card-title>Select Competencies</v-card-title>
        <v-divider></v-divider>

        <!-- The main content area is now a flex container -->
        <v-card-text class="dialog-content-grid">
            <!-- Column 1: Level Selection -->
            <div class="column">
              <v-list-subheader>LEVEL</v-list-subheader>
              <v-list class="scrollable-list" dense>
                <v-list-item v-for="level in levels" :key="level" @click="activeLevel = level" :active="activeLevel === level" color="primary">
                  <v-list-item-title>{{ level }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </div>

            <!-- Column 2: Unit Selection -->
            <div class="column">
              <v-list-subheader>UNIT</v-list-subheader>
              <v-list class="scrollable-list" dense>
                <v-list-item v-for="unit in units" :key="unit" @click="activeUnit = unit" :active="activeUnit === unit" color="secondary">
                  <v-list-item-title class="unit-title">{{ unit }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </div>
            
            <!-- Column 3: Competency Selection -->
            <div class="column">
               <v-list-subheader>COMPETENCIES</v-list-subheader>
               <v-list class="scrollable-list" dense>
                <v-list-item v-for="standard in competencies" :key="standard.id" @click.stop>
                  <template v-slot:prepend>
                    <v-checkbox-btn v-model="tempSelection" :value="standard.id"></v-checkbox-btn>
                  </template>
                   <v-tooltip location="end" :text="standard.description">
        <template v-slot:activator="{ props }">
          <v-list-item-title v-bind="props">
            {{ standard.code }} - {{ standard.description }}
          </v-list-item-title>
        </template>
      </v-tooltip>
                  <v-list-item-title>{{ standard.code }} - {{ standard.description }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </div>
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
.unit-title { white-space: normal; }

.dialog-content-grid {
  display: flex;
  flex-direction: row;
  height: 60vh; /* Give the content area a fixed height relative to the viewport */
  max-height: 550px;
}
.column {
  display: flex;
  flex-direction: column;
  height: 100%;
  border-right: 1px solid rgba(var(--v-theme-on-surface), 0.12);
}
.column:last-child {
  border-right: none;
}
.scrollable-list {
  flex-grow: 1; /* This makes the list take up all available vertical space */
  overflow-y: auto; /* This adds the scrollbar ONLY when needed */
}
.column:nth-child(1) { flex-basis: 25%; flex-shrink: 0; }
.column:nth-child(2) { flex-basis: 35%; flex-shrink: 0; }
.column:nth-child(3) { flex-basis: 40%; flex-shrink: 0; }
</style>