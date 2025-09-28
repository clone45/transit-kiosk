import { ref } from 'vue'

const context = ref('enter')

export const navigationStore = {
  context,

  setContext(newContext) {
    if (newContext === 'enter' || newContext === 'exit') {
      context.value = newContext
    }
  },

  getContext() {
    return context.value
  },

  getReturnPath() {
    return context.value === 'exit' ? '/scan-to-exit' : '/'
  }
}