<script setup>
import { useRouter } from 'vue-router'
import { navigationStore } from '../stores/navigationStore'
import KioskButton from '../components/KioskButton.vue'

const router = useRouter()

const handleHistory = () => {
  console.log('History clicked')
}

const handlePurchaseCard = () => {
  router.push('/purchase-card')
}

const handleAddFare = () => {
  router.push('/add-fare')
}

const handleCancel = () => {
  router.push(navigationStore.getReturnPath())
}
</script>

<template>
  <div id="menu-view" class="h-full flex flex-col">
    <div id="menu-buttons" class="flex-1 flex flex-col justify-center gap-6 px-8">
      <KioskButton
        id="history-button"
        variant="secondary"
        size="large"
        full-width
        @click="handleHistory"
      >
        History
      </KioskButton>

      <KioskButton
        id="purchase-card-button"
        variant="secondary"
        size="large"
        full-width
        @click="handlePurchaseCard"
      >
        Purchase Card
      </KioskButton>

      <KioskButton
        id="add-fare-button"
        variant="secondary"
        size="large"
        full-width
        @click="handleAddFare"
      >
        Add Fare
      </KioskButton>
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