<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { CreditCardIcon, XMarkIcon, ArrowRightOnRectangleIcon, ArrowLeftOnRectangleIcon } from '@heroicons/vue/24/outline'
import { api } from '../api/client'
import { testConfig } from '../config/testConfig'
import { purchaseCardStore } from '../stores/purchaseCardStore'
import { addFareStore } from '../stores/addFareStore'
import { fareStore } from '../stores/fareStore'
import { navigationStore } from '../stores/navigationStore'
import { historyStore } from '../stores/historyStore'

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

const handleScannerClick = async () => {
  if (route.name === 'history') {
    const cardData = testConfig.scanCard()
    if (!cardData) {
      scannerState.value = 'error'
      errorMessage.value = 'No test card configured'
      isInsufficientBalanceError.value = false
      errorTimeout = setTimeout(() => {
        clearError()
      }, 5000)
      return
    }

    scannerState.value = 'success'
    historyStore.setScannedCard({
      uuid: cardData.uuid,
      balance: cardData.balance
    })

    setTimeout(() => {
      router.push('/history/view')
    }, 500)
    return
  }

  if (route.name === 'add-fare') {
    const cardData = testConfig.scanCard()
    if (!cardData) {
      scannerState.value = 'error'
      errorMessage.value = 'No test card configured'
      isInsufficientBalanceError.value = false
      errorTimeout = setTimeout(() => {
        clearError()
      }, 5000)
      return
    }

    scannerState.value = 'success'
    addFareStore.setScannedCard({
      uuid: cardData.uuid,
      balance: cardData.balance
    })

    setTimeout(() => {
      router.push('/add-fare/select-amount')
    }, 500)
    return
  }

  if (route.name === 'add-fare-payment') {
    const cardUuid = addFareStore.scannedCard.value?.uuid
    if (!cardUuid) {
      scannerState.value = 'error'
      errorMessage.value = 'No card selected'
      errorTimeout = setTimeout(() => {
        clearError()
      }, 5000)
      return
    }

    scannerState.value = 'success'

    const currentBalance = addFareStore.scannedCard.value.balance
    const amountToAdd = addFareStore.selectedAmount.value
    const newBalance = currentBalance + amountToAdd

    testConfig.writeCardBalance(cardUuid, newBalance)

    addFareStore.setScannedCard({
      uuid: cardUuid,
      balance: newBalance
    })

    api.getCardByUuid(cardUuid).then(card => {
      api.addFunds(card.id, amountToAdd).catch(error => {
        console.error('Failed to add funds to DB:', error)
      })
    }).catch(error => {
      console.error('Card not found in DB:', error)
    })

    setTimeout(() => {
      router.push('/add-fare/complete')
    }, 500)
    return
  }

  if (route.name === 'add-fare-complete') {
    addFareStore.reset()
    router.push('/')
    return
  }

  if (route.name === 'purchase-card-payment') {
    scannerState.value = 'success'

    const initialBalance = purchaseCardStore.selectedAmount.value
    const newCardUuid = `card-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

    testConfig.writeCardBalance(newCardUuid, initialBalance)

    purchaseCardStore.setCreatedCard({
      uuid: newCardUuid,
      balance: initialBalance
    })

    api.createCard(initialBalance, newCardUuid).catch(error => {
      console.error('Failed to create card in DB:', error)
    })

    setTimeout(() => {
      router.push('/purchase-card/dispensing')
    }, 500)
    return
  }

  if (route.name === 'purchase-card-dispensing') {
    purchaseCardStore.reset()
    router.push('/')
    return
  }

  if (route.name === 'scan-to-exit') {
    const cardData = testConfig.scanCard()
    if (!cardData) {
      scannerState.value = 'error'
      errorMessage.value = 'No test card configured'
      isInsufficientBalanceError.value = false
      errorTimeout = setTimeout(() => {
        clearError()
      }, 5000)
      return
    }

    const tripData = testConfig.readCardTrip(cardData.uuid)
    if (!tripData) {
      scannerState.value = 'success'
      router.push('/exit')
      return
    }

    const exitStationId = parseInt(import.meta.env.VITE_EXIT_STATION_ID)
    if (!exitStationId) {
      scannerState.value = 'error'
      errorMessage.value = 'No exit station ID configured'
      isInsufficientBalanceError.value = false
      errorTimeout = setTimeout(() => {
        clearError()
      }, 5000)
      return
    }

    const fare = await fareStore.fetchFareBetweenStations(tripData.station_id, exitStationId)
    if (fare === null) {
      scannerState.value = 'error'
      errorMessage.value = 'Unable to calculate fare'
      isInsufficientBalanceError.value = false
      errorTimeout = setTimeout(() => {
        clearError()
      }, 5000)
      return
    }

    if (cardData.balance < fare) {
      lastScannedCard.value = cardData
      scannerState.value = 'error'
      const shortfall = (fare - cardData.balance).toFixed(2)
      errorMessage.value = `Insufficient balance\n\nFare: $${fare.toFixed(2)}\nBalance: $${cardData.balance.toFixed(2)}\nShort: $${shortfall}`
      isInsufficientBalanceError.value = true
      errorTimeout = setTimeout(() => {
        clearError()
      }, 5000)
      return
    }

    scannerState.value = 'success'

    const newBalance = cardData.balance - fare
    testConfig.writeCardBalance(cardData.uuid, newBalance)
    testConfig.clearCardTrip(cardData.uuid)

    // Complete the trip in the database asynchronously
    api.getCardByUuid(cardData.uuid).then(card => {
      if (card) {
        api.getActiveTrip(card.id).then(activeTrip => {
          if (activeTrip) {
            api.completeTrip(activeTrip.id, exitStationId, fare).catch(error => {
              console.error('Failed to complete trip in DB:', error)
            })
          }
        }).catch(error => {
          console.error('Failed to get active trip:', error)
        })
      }
    }).catch(error => {
      console.error('Failed to get card from DB:', error)
    })

    router.push('/exit')
    return
  }

  const cardData = testConfig.scanCard()
  if (!cardData) {
    scannerState.value = 'error'
    errorMessage.value = 'No test card configured'
    isInsufficientBalanceError.value = false
    errorTimeout = setTimeout(() => {
      clearError()
    }, 5000)
    return
  }

  const entryStationId = parseInt(import.meta.env.VITE_ENTRY_STATION_ID)
  if (!entryStationId) {
    scannerState.value = 'error'
    errorMessage.value = 'No entry station ID configured'
    isInsufficientBalanceError.value = false
    errorTimeout = setTimeout(() => {
      clearError()
    }, 5000)
    return
  }

  const minimumFare = fareStore.getMinimumFare()
  if (cardData.balance < minimumFare) {
    lastScannedCard.value = cardData
    scannerState.value = 'error'
    errorMessage.value = 'Insufficient balance'
    isInsufficientBalanceError.value = true
    errorTimeout = setTimeout(() => {
      clearError()
    }, 5000)
    return
  }

  scannerState.value = 'success'

  const entryTimestamp = new Date().toISOString()
  testConfig.writeCardTrip(cardData.uuid, entryStationId, entryTimestamp)

  api.createTrip(cardData.uuid, entryStationId).catch(error => {
    console.error('Failed to create trip in DB:', error)
  })

  router.push('/enter')
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