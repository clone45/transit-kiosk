<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'
import { navigationStore } from '../stores/navigationStore'
import ScanChevrons from '../components/ScanChevrons.vue'
import KioskButton from '../components/KioskButton.vue'

const router = useRouter()
const message = ref('Welcome to Transit Kiosk')
const stations = ref([])
const loading = ref(true)
const error = ref(null)

async function fetchStations() {
  try {
    loading.value = true
    error.value = null
    stations.value = await api.getStations()
  } catch (err) {
    error.value = 'Failed to load stations'
    console.error('Error fetching stations:', err)
  } finally {
    loading.value = false
  }
}

const handleMenuClick = () => {
  navigationStore.setContext('enter')
  router.push('/menu')
}

onMounted(() => {
  fetchStations()
})
</script>

<template>
  <div id="home-view" class="h-full flex flex-col">
    <div id="home-header" class="w-full text-center mt-8">
      <h1 id="home-title" class="text-7xl font-semibold text-gray-900">Scan to Enter</h1>
    </div>

    <div id="arrow-container" class="flex-1 flex justify-center items-center">
      <ScanChevrons size="large" stroke-width="1.8" />
    </div>

    <div id="menu-button-wrapper" class="w-full mt-8">
      <KioskButton id="menu-button" variant="primary" size="large" full-width @click="handleMenuClick">
        Menu
      </KioskButton>
    </div>
  </div>
</template>