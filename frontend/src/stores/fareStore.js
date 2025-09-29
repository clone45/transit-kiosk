import { ref } from 'vue'
import { offlineApi as api } from '../api/offlineWrapper'

const minimumFare = ref(null)
const fareCache = ref({})
const loading = ref(false)
const error = ref(null)

export const fareStore = {
  minimumFare,
  fareCache,
  loading,
  error,

  // Initialize from config manager (for offline support)
  initializeFromConfig(configManager) {
    console.log('[FareStore] Initializing from config manager...')

    // Set minimum fare
    this.minimumFare.value = configManager.getMinimumFare()

    // Cache all pricing from config
    const pricing = configManager.config?.pricing || []
    for (const p of pricing) {
      const key = p.stationA < p.stationB
        ? `${p.stationA}-${p.stationB}`
        : `${p.stationB}-${p.stationA}`
      this.fareCache.value[key] = p.fare
    }

    console.log('[FareStore] Initialized with config data:', {
      minimumFare: this.minimumFare.value,
      cachedRoutes: Object.keys(this.fareCache.value).length
    })
  },

  async fetchMinimumFare() {
    if (minimumFare.value !== null) {
      return minimumFare.value
    }

    loading.value = true
    error.value = null

    try {
      const data = await api.getMinimumFare()
      minimumFare.value = data.minimum_fare
      return minimumFare.value
    } catch (err) {
      error.value = 'Failed to fetch minimum fare'
      console.error('Error fetching minimum fare:', err)
      return null
    } finally {
      loading.value = false
    }
  },

  getMinimumFare() {
    return minimumFare.value
  },

  async fetchFareBetweenStations(stationAId, stationBId) {
    const cacheKey = stationAId < stationBId ? `${stationAId}-${stationBId}` : `${stationBId}-${stationAId}`

    if (fareCache.value[cacheKey] !== undefined) {
      return fareCache.value[cacheKey]
    }

    loading.value = true
    error.value = null

    try {
      const data = await api.getFareBetweenStations(stationAId, stationBId)
      fareCache.value[cacheKey] = data.price
      return data.price
    } catch (err) {
      error.value = 'Failed to fetch fare between stations'
      console.error('Error fetching fare between stations:', err)
      return null
    } finally {
      loading.value = false
    }
  },

  getFareBetweenStations(stationAId, stationBId) {
    const cacheKey = stationAId < stationBId ? `${stationAId}-${stationBId}` : `${stationBId}-${stationAId}`
    return fareCache.value[cacheKey]
  },

  async preloadAllFares() {
    loading.value = true
    error.value = null

    try {
      const pricingData = await api.getAllPricing()

      for (const pricing of pricingData) {
        const cacheKey = pricing.station_a_id < pricing.station_b_id
          ? `${pricing.station_a_id}-${pricing.station_b_id}`
          : `${pricing.station_b_id}-${pricing.station_a_id}`
        fareCache.value[cacheKey] = pricing.price
      }

      return fareCache.value
    } catch (err) {
      error.value = 'Failed to preload fares'
      console.error('Error preloading fares:', err)
      return null
    } finally {
      loading.value = false
    }
  }
}