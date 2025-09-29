<script setup>
import { onMounted } from 'vue'
import KioskLayout from './layouts/KioskLayout.vue'
import { fareStore } from './stores/fareStore'
import { configManager } from './services/configManager'

onMounted(async () => {
  console.log('[App] Initializing application...')

  try {
    // Initialize config manager (will try backend, fall back to static)
    await configManager.initialize()

    // Update fareStore to use config data instead of API calls
    fareStore.initializeFromConfig(configManager)

    // Show offline indicator if we started offline
    if (configManager.startedInOfflineMode()) {
      console.warn('[App] Started in offline mode - using static configuration')
    } else {
      console.log('[App] Started with fresh backend configuration')
    }

    console.log('[App] Initialization complete')
  } catch (error) {
    console.error('[App] Failed to initialize application:', error)
    // App should still work with static config fallbacks
  }
})
</script>

<template>
  <KioskLayout>
    <router-view />
  </KioskLayout>
</template>