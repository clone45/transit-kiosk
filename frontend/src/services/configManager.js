import { transitConfig } from '../config/transitConfig'
import { api } from '../api/client'

class ConfigManager {
  constructor() {
    this.config = null
    this.startedOffline = false
  }

  async initialize() {
    try {
      // Try to fetch fresh config from backend
      console.log('[ConfigManager] Attempting to fetch config from backend...')

      const [stations, pricing, minFare] = await Promise.all([
        api.getStations(),
        api.getAllPricing(),
        api.getMinimumFare()
      ])

      this.config = {
        stations,
        pricing: pricing.map(p => ({
          stationA: p.station_a_id,
          stationB: p.station_b_id,
          fare: p.price
        })),
        minimumFare: minFare.minimum_fare
      }

      this.startedOffline = false
      console.log('[ConfigManager] Using fresh config from backend:', {
        stations: this.config.stations.length,
        pricing: this.config.pricing.length,
        minimumFare: this.config.minimumFare
      })
    } catch (error) {
      // Fall back to static config
      this.loadStaticConfig()
      this.startedOffline = true
      console.warn('[ConfigManager] Backend unavailable at startup, using static config:', error.message)
    }
  }

  loadStaticConfig() {
    // Load the static config as fallback
    this.config = {
      stations: transitConfig.stations,
      pricing: transitConfig.pricing,
      minimumFare: transitConfig.minimumFare
    }
    console.log('[ConfigManager] Loaded static config:', {
      stations: this.config.stations.length,
      pricing: this.config.pricing.length,
      minimumFare: this.config.minimumFare
    })
  }

  ensureConfig() {
    // Make sure we have config, even if network died after startup
    if (!this.config) {
      console.warn('[ConfigManager] No config available, loading static config')
      this.loadStaticConfig()
    }
  }

  getStations() {
    this.ensureConfig()
    return this.config?.stations || transitConfig.stations
  }

  getPricing(stationA, stationB) {
    this.ensureConfig()
    const pricing = this.config?.pricing || transitConfig.pricing

    const found = pricing.find(p =>
      (p.stationA === stationA && p.stationB === stationB) ||
      (p.stationA === stationB && p.stationB === stationA)
    )

    const fare = found?.fare || this.getMinimumFare()
    console.log(`[ConfigManager] Pricing for stations ${stationA} → ${stationB}: $${fare}`)
    return fare
  }

  getMinimumFare() {
    this.ensureConfig()
    return this.config?.minimumFare || transitConfig.minimumFare || 2.25
  }

  startedInOfflineMode() {
    return this.startedOffline
  }

  // Helper method to get station name by ID
  getStationName(stationId) {
    const stations = this.getStations()
    const station = stations.find(s => s.id === stationId)
    return station?.name || `Station ${stationId}`
  }
}

export const configManager = new ConfigManager()