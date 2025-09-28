import { ref } from 'vue'

const selectedAmount = ref(15.00)
const createdCard = ref(null)

export const purchaseCardStore = {
  selectedAmount,
  createdCard,

  setAmount(amount) {
    selectedAmount.value = amount
  },

  incrementAmount(delta) {
    selectedAmount.value += delta
  },

  setCreatedCard(card) {
    createdCard.value = card
  },

  reset() {
    selectedAmount.value = 15.00
    createdCard.value = null
  }
}