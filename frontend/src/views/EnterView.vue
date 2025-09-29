<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import EnterChevrons from '../components/EnterChevrons.vue'
import { testConfig } from '../config/testConfig'

const router = useRouter()
const cardBalance = ref(null)

onMounted(() => {
  // Get the current card balance
  const cardData = testConfig.scanCard()
  console.log('[EnterView] Card data:', cardData)
  if (cardData) {
    cardBalance.value = cardData.balance
    console.log('[EnterView] Set balance to:', cardBalance.value)
  } else {
    console.log('[EnterView] No card data found')
  }

  setTimeout(() => {
    router.push('/')
  }, 3000)
})
</script>

<template>
  <div id="enter-view" class="h-full flex flex-col justify-center items-center">
    <div id="enter-chevrons" class="mb-8">
      <EnterChevrons size="large" stroke-width="1.8" />
    </div>
    <div id="enter-text" class="text-8xl font-semibold text-green-600">
      Enter
    </div>
    <div v-if="cardBalance !== null" id="card-balance" class="text-4xl font-semibold text-green-600 mt-6">
      Balance: ${{ cardBalance.toFixed(2) }}
    </div>
  </div>
</template>