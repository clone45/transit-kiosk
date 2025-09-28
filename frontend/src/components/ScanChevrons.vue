<script setup>
defineProps({
  size: {
    type: String,
    default: 'large'
  },
  strokeWidth: {
    type: String,
    default: '1.8'
  },
  animate: {
    type: Boolean,
    default: true
  }
})

const sizes = {
  small: 'w-24 h-32',
  medium: 'w-32 h-48',
  large: 'w-48 h-64'
}
</script>

<template>
  <div class="flex justify-center items-center -space-x-20">
    <svg :class="[sizes[size], animate ? 'chevron-pulse-1' : '']" viewBox="0 0 12 24" fill="none" stroke="currentColor" :stroke-width="strokeWidth" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="9 18 3 12 9 6" class="text-kiosk-blue" stroke="currentColor"></polyline>
    </svg>
    <svg :class="[sizes[size], animate ? 'chevron-pulse-2' : '']" viewBox="0 0 12 24" fill="none" stroke="currentColor" :stroke-width="strokeWidth" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="9 18 3 12 9 6" class="text-kiosk-blue" stroke="currentColor"></polyline>
    </svg>
    <svg :class="[sizes[size], animate ? 'chevron-pulse-3' : '']" viewBox="0 0 12 24" fill="none" stroke="currentColor" :stroke-width="strokeWidth" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="9 18 3 12 9 6" class="text-kiosk-blue" stroke="currentColor"></polyline>
    </svg>
  </div>
</template>

<style scoped>
@keyframes chevron-pulse-1 {
  0%, 33% {
    opacity: 0.3;
  }
  34%, 66% {
    opacity: 0.3;
  }
  67%, 99% {
    opacity: 1;
  }
  100% {
    opacity: 0.3;
  }
}

@keyframes chevron-pulse-2 {
  0%, 33% {
    opacity: 0.3;
  }
  34%, 66% {
    opacity: 1;
  }
  67%, 100% {
    opacity: 0.3;
  }
}

@keyframes chevron-pulse-3 {
  0%, 33% {
    opacity: 1;
  }
  34%, 100% {
    opacity: 0.3;
  }
}

.chevron-pulse-1 {
  animation: chevron-pulse-1 0.9s steps(1) infinite;
}

.chevron-pulse-2 {
  animation: chevron-pulse-2 0.9s steps(1) infinite;
}

.chevron-pulse-3 {
  animation: chevron-pulse-3 0.9s steps(1) infinite;
}
</style>