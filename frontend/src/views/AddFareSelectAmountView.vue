<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { addFareStore } from '../stores/addFareStore'
import { navigationStore } from '../stores/navigationStore'
import KioskButton from '../components/KioskButton.vue'

const router = useRouter()

const MIN_AMOUNT = 0
const MAX_AMOUNT = 200

const isDecrementDisabled = computed(() => {
  return addFareStore.selectedAmount.value - 5 < MIN_AMOUNT
})

const isIncrementDisabled = computed(() => {
  return addFareStore.selectedAmount.value + 5 > MAX_AMOUNT
})

const isDecrement20Disabled = computed(() => {
  return addFareStore.selectedAmount.value - 20 < MIN_AMOUNT
})

const isIncrement20Disabled = computed(() => {
  return addFareStore.selectedAmount.value + 20 > MAX_AMOUNT
})

const isContinueDisabled = computed(() => {
  return addFareStore.selectedAmount.value <= 0
})

const handleDecrement = () => {
  const newAmount = addFareStore.selectedAmount.value - 5
  if (newAmount >= MIN_AMOUNT) {
    addFareStore.incrementAmount(-5)
  }
}

const handleIncrement = () => {
  const newAmount = addFareStore.selectedAmount.value + 5
  if (newAmount <= MAX_AMOUNT) {
    addFareStore.incrementAmount(5)
  }
}

const handleDecrement20 = () => {
  const newAmount = addFareStore.selectedAmount.value - 20
  if (newAmount >= MIN_AMOUNT) {
    addFareStore.incrementAmount(-20)
  }
}

const handleIncrement20 = () => {
  const newAmount = addFareStore.selectedAmount.value + 20
  if (newAmount <= MAX_AMOUNT) {
    addFareStore.incrementAmount(20)
  }
}

const handleContinue = () => {
  router.push('/add-fare/payment')
}

const handleCancel = () => {
  addFareStore.reset()
  router.push(navigationStore.getReturnPath())
}
</script>

<template>
  <div id="add-fare-select-amount" class="h-full flex flex-col">
    <div id="add-fare-header" class="text-center pt-8 px-8">
      <h1 id="add-fare-title" class="text-6xl font-semibold text-gray-900">Add Fare</h1>
      <div v-if="addFareStore.scannedCard.value !== null" id="current-balance" class="text-3xl text-gray-700 mt-2">
        Current Balance: ${{ addFareStore.scannedCard.value.balance.toFixed(2) }}
      </div>
    </div>

    <div id="add-fare-content" class="flex-1 flex flex-col justify-center items-center gap-6 px-8">
      <div id="amount-display" class="bg-white rounded-2xl px-16 py-8 border-4 border-gray-300 flex flex-col items-center gap-2">
        <div id="amount-to-add" class="text-6xl font-semibold text-gray-900">
          +${{ addFareStore.selectedAmount.value.toFixed(2) }}
        </div>
        <div v-if="addFareStore.scannedCard.value !== null" id="new-total" class="text-3xl text-gray-600">
          New Total: ${{ (addFareStore.scannedCard.value.balance + addFareStore.selectedAmount.value).toFixed(2) }}
        </div>
      </div>

      <div id="amount-controls" class="flex flex-col gap-4 w-full">
        <div class="flex gap-6 justify-center">
          <KioskButton
            id="decrement-button"
            variant="secondary"
            size="small"
            :disabled="isDecrementDisabled"
            @click="handleDecrement"
          >
            -$5
          </KioskButton>

          <KioskButton
            id="increment-button"
            variant="secondary"
            size="small"
            :disabled="isIncrementDisabled"
            @click="handleIncrement"
          >
            +$5
          </KioskButton>

          <KioskButton
            id="decrement-20-button"
            variant="secondary"
            size="small"
            :disabled="isDecrement20Disabled"
            @click="handleDecrement20"
          >
            -$20
          </KioskButton>

          <KioskButton
            id="increment-20-button"
            variant="secondary"
            size="small"
            :disabled="isIncrement20Disabled"
            @click="handleIncrement20"
          >
            +$20
          </KioskButton>
        </div>
      </div>

      <div id="continue-button-wrapper" class="w-full mt-6">
        <KioskButton
          id="continue-button"
          variant="primary"
          size="small"
          full-width
          :disabled="isContinueDisabled"
          @click="handleContinue"
        >
          Continue to Payment
        </KioskButton>
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