<script setup>
import { useRouter } from 'vue-router'
import { addFareStore } from '../stores/addFareStore'
import ScanChevrons from '../components/ScanChevrons.vue'
import KioskButton from '../components/KioskButton.vue'

const router = useRouter()

const handleCancel = () => {
  router.push('/add-fare/select-amount')
}
</script>

<template>
  <div id="add-fare-payment" class="h-full flex flex-col">
    <div id="payment-content" class="flex-1 flex flex-col justify-center items-center gap-12 px-8">
      <h1 id="payment-title" class="text-6xl font-semibold text-gray-900">Payment Required</h1>

      <div id="payment-total" class="text-6xl font-semibold text-gray-900">
        Total: ${{ addFareStore.selectedAmount.value.toFixed(2) }}
      </div>

      <div id="payment-instructions" class="text-5xl text-gray-700 text-center">
        Please tap payment<br>card to add funds.
      </div>

      <div id="payment-chevrons">
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