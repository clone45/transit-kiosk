import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import EnterView from '../views/EnterView.vue'
import ExitView from '../views/ExitView.vue'
import ExitSuccessView from '../views/ExitSuccessView.vue'
import MenuView from '../views/MenuView.vue'
import PurchaseCardSelectAmountView from '../views/PurchaseCardSelectAmountView.vue'
import PurchaseCardPaymentView from '../views/PurchaseCardPaymentView.vue'
import PurchaseCardDispensingView from '../views/PurchaseCardDispensingView.vue'
import AddFareScanCardView from '../views/AddFareScanCardView.vue'
import AddFareSelectAmountView from '../views/AddFareSelectAmountView.vue'
import AddFarePaymentView from '../views/AddFarePaymentView.vue'
import AddFareCompleteView from '../views/AddFareCompleteView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/enter',
    name: 'enter',
    component: EnterView
  },
  {
    path: '/scan-to-exit',
    name: 'scan-to-exit',
    component: ExitView
  },
  {
    path: '/exit',
    name: 'exit',
    component: ExitSuccessView
  },
  {
    path: '/menu',
    name: 'menu',
    component: MenuView
  },
  {
    path: '/purchase-card',
    name: 'purchase-card',
    component: PurchaseCardSelectAmountView
  },
  {
    path: '/purchase-card/payment',
    name: 'purchase-card-payment',
    component: PurchaseCardPaymentView
  },
  {
    path: '/purchase-card/dispensing',
    name: 'purchase-card-dispensing',
    component: PurchaseCardDispensingView
  },
  {
    path: '/add-fare',
    name: 'add-fare',
    component: AddFareScanCardView
  },
  {
    path: '/add-fare/select-amount',
    name: 'add-fare-select-amount',
    component: AddFareSelectAmountView
  },
  {
    path: '/add-fare/payment',
    name: 'add-fare-payment',
    component: AddFarePaymentView
  },
  {
    path: '/add-fare/complete',
    name: 'add-fare-complete',
    component: AddFareCompleteView
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router