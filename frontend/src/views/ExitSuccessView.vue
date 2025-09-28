<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import EnterChevrons from '../components/EnterChevrons.vue'

const router = useRouter()

onMounted(() => {
  setTimeout(() => {
    router.push('/scan-to-exit')
  }, 3000)
})
</script>

<template>
  <div id="exit-success-view" class="h-full flex flex-col justify-center items-center">
    <div id="exit-success-chevrons" class="mb-8">
      <EnterChevrons size="large" stroke-width="1.8" />
    </div>
    <div id="exit-success-text" class="text-8xl font-semibold text-green-600">
      Exit
    </div>
  </div>
</template>