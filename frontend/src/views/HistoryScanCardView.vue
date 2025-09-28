<script setup>
import { useRouter } from 'vue-router'
import { navigationStore } from '../stores/navigationStore'
import ScanChevrons from '../components/ScanChevrons.vue'
import KioskButton from '../components/KioskButton.vue'

const router = useRouter()

const handleCancel = () => {
  router.push(navigationStore.getReturnPath())
}
</script>

<template>
  <div id="history-scan-card" class="h-full flex flex-col">
    <div id="scan-content" class="flex-1 flex flex-col justify-center items-center gap-12 px-8">
      <h1 id="scan-title" class="text-6xl font-semibold text-gray-900 text-center">Trip History</h1>

      <div id="scan-instructions" class="text-5xl text-gray-700 text-center">
        Please tap your<br>transit card
      </div>

      <div id="scan-chevrons">
        <ScanChevrons size="large" stroke-width="1.8" />
      </div>
    </div>

    <div id="cancel-button-wrapper" class="w-full mt-8">
      <KioskButton
        id="cancel-button"
        variant="secondary"
        size="small"
        full-width
        @click="handleCancel"
      >
        Cancel
      </KioskButton>
    </div>
  </div>
</template>