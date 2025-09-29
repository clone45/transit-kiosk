<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { CreditCardIcon, XMarkIcon, ArrowRightOnRectangleIcon, ArrowLeftOnRectangleIcon } from '@heroicons/vue/24/outline'
import { testConfig } from '../config/testConfig'
import { addFareStore } from '../stores/addFareStore'
import { navigationStore } from '../stores/navigationStore'
import { scannerService } from '../services/scannerService'
import { configManager } from '../services/configManager'

const router = useRouter()
const route = useRoute()
const scannerState = ref('idle')
const errorMessage = ref(null)
const isInsufficientBalanceError = ref(false)
const showDebugPanel = ref(false)
const debugCardData = ref(null)
const debugTripData = ref(null)
const newBalance = ref(0)
const lastScannedCard = ref(null)
const stations = ref([])
const selectedEntryStation = ref(parseInt(import.meta.env.VITE_ENTRY_STATION_ID) || 1)
const selectedExitStation = ref(parseInt(import.meta.env.VITE_EXIT_STATION_ID) || 2)

const borderColors = {
  idle: 'border-kiosk-blue',
  success: 'border-green-500',
  error: 'border-red-500'
}

watch(
  () => route.name,
  (newRoute) => {
    if (newRoute === 'enter' || newRoute === 'exit' || newRoute === 'purchase-card-dispensing' || newRoute === 'add-fare-complete') {
      scannerState.value = 'success'
    } else {
      scannerState.value = 'idle'
      errorMessage.value = null
      isInsufficientBalanceError.value = false
    }
  },
  { immediate: true }
)

let errorTimeout = null

const clearError = () => {
  scannerState.value = 'idle'
  errorMessage.value = null
  isInsufficientBalanceError.value = false
  if (errorTimeout) {
    clearTimeout(errorTimeout)
    errorTimeout = null
  }
}

const handleExitError = () => {
  clearError()
  router.push('/')
}

const handleAddFunds = () => {
  clearError()
  const context = route.name === 'scan-to-exit' ? 'exit' : 'enter'
  navigationStore.setContext(context)

  if (lastScannedCard.value) {
    addFareStore.setScannedCard({
      uuid: lastScannedCard.value.uuid,
      balance: lastScannedCard.value.balance
    })
    router.push('/add-fare/select-amount')
  } else {
    router.push('/add-fare')
  }
}

const toggleDebugPanel = () => {
  showDebugPanel.value = !showDebugPanel.value
  if (showDebugPanel.value) {
    debugCardData.value = testConfig.scanCard()
    if (debugCardData.value) {
      debugTripData.value = testConfig.readCardTrip(debugCardData.value.uuid)
      newBalance.value = debugCardData.value.balance
    } else {
      debugTripData.value = null
      newBalance.value = 0
    }
  }
}

const updateBalance = () => {
  if (debugCardData.value && newBalance.value >= 0) {
    testConfig.writeCardBalance(debugCardData.value.uuid, newBalance.value)
    debugCardData.value.balance = newBalance.value
  }
}

// Load stations when component mounts
onMounted(async () => {
  try {
    stations.value = configManager.getStations()
  } catch (error) {
    console.error('Failed to load stations:', error)
    // Fallback to static config if needed
    stations.value = [
      { id: 1, name: "Central Station" },
      { id: 2, name: "Union Square" },
      { id: 3, name: "Airport Terminal" },
      { id: 4, name: "Downtown" },
      { id: 5, name: "University" },
      { id: 6, name: "Stadium" },
      { id: 7, name: "Harbor Point" },
      { id: 8, name: "Tech Center" }
    ]
  }
})

const handleScannerClick = async () => {
  // Call the scanner service with context including selected stations
  const result = await scannerService.handleScan({
    routeName: route.name,
    router,
    route,
    entryStationId: selectedEntryStation.value,
    exitStationId: selectedExitStation.value
  })

  // Apply the result to the UI state
  if (result.success) {
    scannerState.value = result.scannerState || 'success'
  } else {
    scannerState.value = result.scannerState || 'error'
    errorMessage.value = result.errorMessage || 'An error occurred'
    isInsufficientBalanceError.value = result.isInsufficientBalance || false

    // Store the last scanned card if provided
    if (result.lastScannedCard) {
      lastScannedCard.value = result.lastScannedCard
    }

    // Set error timeout if specified
    if (result.timeout) {
      errorTimeout = setTimeout(() => {
        clearError()
      }, result.timeout)
    }
  }
}
</script>

<template>
  <div id="kiosk-wrapper" class="min-h-screen bg-black flex items-center justify-center p-4 relative">
    <!-- Debug Icons (Top Right of Browser) -->
    <div v-if="!showDebugPanel" id="debug-icons" class="absolute top-4 right-4 z-50 flex flex-col gap-3">
      <div id="card-icon" class="cursor-pointer hover:opacity-80 transition-opacity" @click="toggleDebugPanel">
        <CreditCardIcon class="w-12 h-12 text-white" />
      </div>
      <div id="enter-icon" class="cursor-pointer hover:opacity-80 transition-opacity" @click="router.push('/')">
        <ArrowRightOnRectangleIcon class="w-12 h-12 text-green-400" />
      </div>
      <div id="exit-icon" class="cursor-pointer hover:opacity-80 transition-opacity" @click="router.push('/scan-to-exit')">
        <ArrowLeftOnRectangleIcon class="w-12 h-12 text-red-400" />
      </div>
    </div>

    <!-- Debug Panel (Side Panel) -->
    <div
      v-if="showDebugPanel"
      id="debug-panel"
      class="fixed top-0 right-0 h-full w-96 bg-gray-900 text-white shadow-2xl z-40 p-6 overflow-y-auto"
    >
      <div id="debug-header" class="flex justify-between items-center mb-6">
        <h2 id="debug-title" class="text-2xl font-semibold">Transit Card Debug</h2>
        <XMarkIcon class="w-8 h-8 cursor-pointer hover:opacity-80" @click="toggleDebugPanel" />
      </div>

      <div v-if="!debugCardData" id="no-card" class="text-gray-400 text-center py-8">
        No card configured
      </div>

      <div v-else id="card-info" class="space-y-6">
        <div id="card-uuid-section">
          <h3 class="text-sm font-semibold text-gray-400 uppercase mb-2">Card UUID</h3>
          <p class="font-mono text-sm break-all">{{ debugCardData.uuid }}</p>
        </div>

        <div id="card-balance-section">
          <h3 class="text-sm font-semibold text-gray-400 uppercase mb-2">Balance</h3>
          <p class="text-3xl font-bold text-green-400">${{ debugCardData.balance.toFixed(2) }}</p>
        </div>

        <div id="active-trip-section">
          <h3 class="text-sm font-semibold text-gray-400 uppercase mb-2">Active Trip</h3>
          <div v-if="debugTripData" class="space-y-2">
            <div>
              <span class="text-gray-400">Entry Station ID:</span>
              <span class="ml-2 font-semibold">{{ debugTripData.station_id }}</span>
            </div>
            <div>
              <span class="text-gray-400">Entry Time:</span>
              <span class="ml-2 font-semibold">{{ new Date(debugTripData.timestamp).toLocaleString() }}</span>
            </div>
          </div>
          <p v-else class="text-gray-500 italic">No active trip</p>
        </div>

        <div id="update-balance-section" class="pt-4 border-t border-gray-700">
          <h3 class="text-sm font-semibold text-gray-400 uppercase mb-3">Update Balance</h3>
          <div class="flex gap-2">
            <input
              id="balance-input"
              v-model.number="newBalance"
              type="number"
              step="0.01"
              min="0"
              class="flex-1 px-3 py-2 bg-gray-800 text-white rounded border border-gray-600 focus:outline-none focus:border-blue-500"
              placeholder="New balance"
            />
            <button
              id="update-balance-button"
              @click="updateBalance"
              class="px-4 py-2 bg-blue-600 text-white rounded font-semibold hover:bg-blue-700 transition-colors"
            >
              Update
            </button>
          </div>
        </div>

        <div id="station-config-section" class="pt-4 border-t border-gray-700">
          <h3 class="text-sm font-semibold text-gray-400 uppercase mb-3">Station Configuration</h3>

          <div class="space-y-3">
            <div>
              <label class="block text-sm text-gray-400 mb-1">Entry Station</label>
              <select
                id="entry-station-select"
                v-model="selectedEntryStation"
                class="w-full px-3 py-2 bg-gray-800 text-white rounded border border-gray-600 focus:outline-none focus:border-blue-500"
              >
                <option v-for="station in stations" :key="station.id" :value="station.id">
                  {{ station.id }} - {{ station.name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm text-gray-400 mb-1">Exit Station</label>
              <select
                id="exit-station-select"
                v-model="selectedExitStation"
                class="w-full px-3 py-2 bg-gray-800 text-white rounded border border-gray-600 focus:outline-none focus:border-blue-500"
              >
                <option v-for="station in stations" :key="station.id" :value="station.id">
                  {{ station.id }} - {{ station.name }}
                </option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div id="kiosk-container" class="w-full max-w-5xl h-[90vh] max-h-[840px] bg-gray-800 rounded-3xl shadow-2xl p-6 flex gap-6">
      <!-- Scanner Area (Left Side) -->
      <div id="scanner-wrapper" class="w-1/3 flex items-center justify-center">
        <div
          id="scanner-border"
          class="w-full h-full rounded-2xl border-8 cursor-pointer"
          :class="borderColors[scannerState]"
          @click="handleScannerClick"
        >
          <div id="scanner-area" class="w-full h-full bg-black rounded-xl">
          </div>
        </div>
      </div>

      <!-- Touch Screen Area (Right Side) -->
      <div id="touchscreen-container" class="flex-1 bg-gray-100 rounded-2xl shadow-inner overflow-hidden flex flex-col">
        <!-- Content Area -->
        <div id="touchscreen-content" class="flex-1 overflow-auto p-4" style="background-color: rgb(240, 241, 247);">
          <!-- Error Message (Full Screen) -->
          <div v-if="errorMessage" id="error-fullscreen" class="h-full flex flex-col items-center justify-center bg-red-600 text-white text-center px-8 rounded-xl gap-8">
            <div id="error-message-text" class="text-4xl font-semibold whitespace-pre-line">
              {{ errorMessage }}
            </div>

            <!-- Insufficient Balance Error Buttons -->
            <div v-if="isInsufficientBalanceError" id="error-buttons" class="flex gap-6">
              <button id="exit-button" @click="handleExitError" class="bg-white text-red-600 px-12 py-6 rounded-xl text-3xl font-semibold hover:bg-gray-100 transition-colors">
                Exit
              </button>
              <button id="add-funds-button" @click="handleAddFunds" class="bg-white text-red-600 px-12 py-6 rounded-xl text-3xl font-semibold hover:bg-gray-100 transition-colors">
                Add Funds
              </button>
            </div>

            <!-- Other Error Close Button -->
            <button v-else id="close-error-button" @click="clearError" class="bg-white text-red-600 px-12 py-6 rounded-xl text-3xl font-semibold hover:bg-gray-100 transition-colors">
              Close
            </button>
          </div>

          <!-- Normal Content -->
          <slot v-else />
        </div>
      </div>
    </div>
  </div>
</template>