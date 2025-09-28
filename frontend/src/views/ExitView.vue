<script setup>
import { useRouter } from 'vue-router'
import { navigationStore } from '../stores/navigationStore'
import ScanChevrons from '../components/ScanChevrons.vue'
import KioskButton from '../components/KioskButton.vue'

const router = useRouter()

const handleMenuClick = () => {
  navigationStore.setContext('exit')
  router.push('/menu')
}
</script>

<template>
  <div id="exit-view" class="h-full flex flex-col">
    <div id="exit-header" class="w-full text-center mt-8">
      <h1 id="exit-title" class="text-6xl font-semibold text-gray-900">Scan to Exit</h1>
    </div>

    <div id="exit-arrow-container" class="flex-1 flex justify-center items-center">
      <ScanChevrons size="large" stroke-width="1.8" />
    </div>

    <div id="exit-menu-button-wrapper" class="w-full mt-8">
      <KioskButton id="exit-menu-button" variant="primary" size="large" full-width @click="handleMenuClick">
        Menu
      </KioskButton>
    </div>
  </div>
</template>