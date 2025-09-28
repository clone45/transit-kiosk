import { ref } from 'vue'

const scannedCard = ref(null)

export const historyStore = {
  scannedCard,

  setScannedCard(cardData) {
    scannedCard.value = cardData
  },

  reset() {
    scannedCard.value = null
  }
}