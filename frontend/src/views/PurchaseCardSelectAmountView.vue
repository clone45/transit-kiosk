<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { purchaseCardStore } from '../stores/purchaseCardStore'
import { navigationStore } from '../stores/navigationStore'
import KioskButton from '../components/KioskButton.vue'

const router = useRouter()

const MIN_AMOUNT = 0
const MAX_AMOUNT = 200

const isDecrementDisabled = computed(() => {
  return purchaseCardStore.selectedAmount.value - 5 < MIN_AMOUNT
})

const isIncrementDisabled = computed(() => {
  return purchaseCardStore.selectedAmount.value + 5 > MAX_AMOUNT
})

const isDecrement20Disabled = computed(() => {
  return purchaseCardStore.selectedAmount.value - 20 < MIN_AMOUNT
})

const isIncrement20Disabled = computed(() => {
  return purchaseCardStore.selectedAmount.value + 20 > MAX_AMOUNT
})

const handleDecrement = () => {
  const newAmount = purchaseCardStore.selectedAmount.value - 5
  if (newAmount >= MIN_AMOUNT) {
    purchaseCardStore.incrementAmount(-5)
  }
}

const handleIncrement = () => {
  const newAmount = purchaseCardStore.selectedAmount.value + 5
  if (newAmount <= MAX_AMOUNT) {
    purchaseCardStore.incrementAmount(5)
  }
}

const handleDecrement20 = () => {
  const newAmount = purchaseCardStore.selectedAmount.value - 20
  if (newAmount >= MIN_AMOUNT) {
    purchaseCardStore.incrementAmount(-20)
  }
}

const handleIncrement20 = () => {
  const newAmount = purchaseCardStore.selectedAmount.value + 20
  if (newAmount <= MAX_AMOUNT) {
    purchaseCardStore.incrementAmount(20)
  }
}

const handleContinue = () => {
  router.push('/purchase-card/payment')
}

const handleCancel = () => {
  purchaseCardStore.reset()
  router.push(navigationStore.getReturnPath())
}
</script>

<template>
  <div id="purchase-card-select-amount" class="h-full flex flex-col">
    <div id="pc-content" class="flex-1 flex flex-col justify-center items-center gap-8 px-8">
      <h1 id="pc-title" class="text-6xl font-semibold text-gray-900">Purchase Card</h1>

      <div id="amount-display" class="text-8xl font-semibold text-gray-900 bg-white rounded-2xl px-16 py-8 border-4 border-gray-300">
        ${{ purchaseCardStore.selectedAmount.value.toFixed(2) }}
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

      <div id="continue-button-wrapper" class="w-full mt-8">
        <KioskButton
          id="continue-button"
          variant="primary"
          size="small"
          full-width
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