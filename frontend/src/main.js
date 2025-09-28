import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { fareStore } from './stores/fareStore'

fareStore.fetchMinimumFare()
fareStore.preloadAllFares()

createApp(App).use(router).mount('#app')
