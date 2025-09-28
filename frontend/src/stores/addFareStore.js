import { ref } from 'vue'

const selectedAmount = ref(0.00)
const scannedCard = ref(null)

export const addFareStore = {
  selectedAmount,
  scannedCard,

  setAmount(amount) {
    selectedAmount.value = amount
  },

  incrementAmount(delta) {
    selectedAmount.value += delta
  },

  setScannedCard(card) {
    scannedCard.value = card
  },

  reset() {
    selectedAmount.value = 0.00
    scannedCard.value = null
  }
}