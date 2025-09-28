<script setup>
defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'danger', 'disabled'].includes(value)
  },
  size: {
    type: String,
    default: 'large',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  fullWidth: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

const handleClick = () => {
  emit('click')
}

const variantClasses = {
  primary: 'bg-kiosk-blue text-white hover:opacity-90',
  secondary: 'bg-gray-300 text-gray-800 hover:bg-gray-400',
  danger: 'bg-red-600 text-white hover:bg-red-700',
  disabled: 'bg-gray-400 text-gray-600 cursor-not-allowed'
}

const sizeClasses = {
  small: 'text-3xl py-4 px-6',
  medium: 'text-4xl py-6 px-8',
  large: 'text-6xl py-9 px-8'
}
</script>

<template>
  <button
    :class="[
      'font-semibold rounded-2xl transition-colors',
      variantClasses[disabled ? 'disabled' : variant],
      sizeClasses[size],
      fullWidth ? 'w-full' : ''
    ]"
    :disabled="disabled"
    @click="handleClick"
  >
    <slot />
  </button>
</template>