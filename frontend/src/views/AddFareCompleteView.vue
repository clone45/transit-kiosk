<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { addFareStore } from '../stores/addFareStore'
import { navigationStore } from '../stores/navigationStore'
import KioskButton from '../components/KioskButton.vue'

const router = useRouter()

const newBalance = computed(() => {
  if (addFareStore.scannedCard.value) {
    return addFareStore.scannedCard.value.balance
  }
  return 0
})

const handleDone = () => {
  addFareStore.reset()
  router.push(navigationStore.getReturnPath())
}
</script>

<template>
  <div id="add-fare-complete" class="h-full flex flex-col">
    <div id="complete-content" class="flex-1 flex flex-col justify-center items-center gap-12 px-8">
      <div id="complete-title" class="text-5xl font-semibold text-green-600 text-center">
        Funds Added Successfully
      </div>

      <div id="balance-info" class="text-4xl text-gray-700 text-center">
        New Balance: ${{ newBalance.toFixed(2) }}
      </div>
    </div>

    <div id="done-button-wrapper" class="w-full mt-8">
      <KioskButton
        id="done-button"
        variant="primary"
        size="small"
        full-width
        @click="handleDone"
      >
        Done
      </KioskButton>
    </div>
  </div>
</template>