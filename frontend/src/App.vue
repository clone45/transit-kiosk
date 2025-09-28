<script setup>
import { onMounted } from 'vue'
import KioskLayout from './layouts/KioskLayout.vue'
import { fareStore } from './stores/fareStore'

onMounted(async () => {
  try {
    await fareStore.fetchMinimumFare()
  } catch (error) {
    console.error('Failed to fetch minimum fare on app mount:', error)
  }
})
</script>

<template>
  <KioskLayout>
    <router-view />
  </KioskLayout>
</template>