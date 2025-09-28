<script setup>
import { useRouter } from 'vue-router'
import { purchaseCardStore } from '../stores/purchaseCardStore'
import EnterChevrons from '../components/EnterChevrons.vue'

const router = useRouter()
</script>

<template>
  <div id="purchase-card-dispensing" class="h-full flex flex-col justify-center items-center gap-12 px-8">
    <div id="dispensing-title" class="text-5xl font-semibold text-gray-900 text-center">
      Dispensing transit card.
    </div>

    <div id="dispensing-instructions" class="text-4xl text-gray-700 text-center">
      Please remove your card<br>from the slot below
    </div>

    <div id="dispensing-chevrons" class="rotate-180">
      <EnterChevrons size="large" stroke-width="1.8" />
    </div>
  </div>
</template>