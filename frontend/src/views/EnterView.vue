<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import EnterChevrons from '../components/EnterChevrons.vue'

const router = useRouter()

onMounted(() => {
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
  </div>
</template>