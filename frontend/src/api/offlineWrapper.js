import { api } from './client'
import { configManager } from '../services/configManager'
import { failedOpsWriter } from '../services/failedOpsWriter'

export const offlineApi = {
  // Write operations - always try API first, write to file if failed
  async createTrip(cardUuid, stationId) {
    try {
      // Always try the real API first
      const result = await api.createTrip(cardUuid, stationId)
      console.log('[OfflineAPI] createTrip succeeded:', result.id)
      return result
    } catch (error) {
      // Network failed - write to file and continue
      console.warn('[OfflineAPI] createTrip failed, writing to file:', error.message)

      await failedOpsWriter.writeFailedOperation({
        type: 'CREATE_TRIP',
        data: { cardUuid, stationId },
        timestamp: new Date().toISOString()
      })

      // Return a fake response so the app continues
      return {
        id: `temp_trip_${Date.now()}`,
        card_uuid: cardUuid,
        source_station_id: stationId,
        status: 'offline_pending'
      }
    }
  },

  async completeTrip(tripId, destinationStationId, finalCost) {
    try {
      // Always try the real API first
      const result = await api.completeTrip(tripId, destinationStationId, finalCost)
      console.log('[OfflineAPI] completeTrip succeeded:', tripId)
      return result
    } catch (error) {
      console.warn('[OfflineAPI] completeTrip failed, writing to file:', error.message)

      await failedOpsWriter.writeFailedOperation({
        type: 'COMPLETE_TRIP',
        data: { tripId, destinationStationId, finalCost },
        timestamp: new Date().toISOString()
      })

      return {
        status: 'offline_pending',
        trip_id: tripId
      }
    }
  },

  async createCard(initialBalance, uuid) {
    try {
      const result = await api.createCard(initialBalance, uuid)
      console.log('[OfflineAPI] createCard succeeded:', result.uuid)
      return result
    } catch (error) {
      console.warn('[OfflineAPI] createCard failed, writing to file:', error.message)

      await failedOpsWriter.writeFailedOperation({
        type: 'CREATE_CARD',
        data: { initialBalance, uuid },
        timestamp: new Date().toISOString()
      })

      return {
        id: `temp_card_${Date.now()}`,
        uuid: uuid || `temp_${Date.now()}`,
        balance: initialBalance,
        status: 'offline_pending'
      }
    }
  },

  async addFunds(cardId, amount) {
    try {
      const result = await api.addFunds(cardId, amount)
      console.log('[OfflineAPI] addFunds succeeded:', cardId, amount)
      return result
    } catch (error) {
      console.warn('[OfflineAPI] addFunds failed, writing to file:', error.message)

      await failedOpsWriter.writeFailedOperation({
        type: 'ADD_FUNDS',
        data: { cardId, amount },
        timestamp: new Date().toISOString()
      })

      return {
        status: 'offline_pending',
        card_id: cardId,
        amount: amount
      }
    }
  },

  // Read operations - try API first, fall back to config
  async getStations() {
    try {
      // Try to get fresh data
      const result = await api.getStations()
      console.log('[OfflineAPI] getStations succeeded from API')
      return result
    } catch (error) {
      // Network failed - use config
      console.warn('[OfflineAPI] getStations failed, using config:', error.message)
      return configManager.getStations()
    }
  },

  async getFareBetweenStations(stationAId, stationBId) {
    try {
      // Try to get fresh fare
      const result = await api.getFareBetweenStations(stationAId, stationBId)
      console.log('[OfflineAPI] getFareBetweenStations succeeded from API')
      return result
    } catch (error) {
      // Network failed - use config
      console.warn('[OfflineAPI] getFareBetweenStations failed, using config:', error.message)
      return {
        price: configManager.getPricing(stationAId, stationBId)
      }
    }
  },

  async getMinimumFare() {
    try {
      // Try to get fresh minimum fare
      const result = await api.getMinimumFare()
      console.log('[OfflineAPI] getMinimumFare succeeded from API')
      return result
    } catch (error) {
      // Network failed - use config
      console.warn('[OfflineAPI] getMinimumFare failed, using config:', error.message)
      return {
        minimum_fare: configManager.getMinimumFare()
      }
    }
  },

  async getAllPricing() {
    try {
      // Try to get fresh pricing
      const result = await api.getAllPricing()
      console.log('[OfflineAPI] getAllPricing succeeded from API')
      return result
    } catch (error) {
      // Network failed - use config
      console.warn('[OfflineAPI] getAllPricing failed, using config:', error.message)
      const pricing = configManager.config?.pricing || []
      return pricing.map(p => ({
        station_a_id: p.stationA,
        station_b_id: p.stationB,
        price: p.fare
      }))
    }
  },

  // Operations that should fail gracefully when offline
  async getCardByUuid(uuid) {
    try {
      const result = await api.getCardByUuid(uuid)
      console.log('[OfflineAPI] getCardByUuid succeeded:', uuid)
      return result
    } catch (error) {
      console.warn('[OfflineAPI] getCardByUuid failed, returning null:', error.message)
      // Return null to indicate card not found/not accessible
      return null
    }
  },

  async getActiveTrip(cardId) {
    try {
      const result = await api.getActiveTrip(cardId)
      console.log('[OfflineAPI] getActiveTrip succeeded:', cardId)
      return result
    } catch (error) {
      console.warn('[OfflineAPI] getActiveTrip failed, returning null:', error.message)
      return null
    }
  },

  async getCardTrips(cardId) {
    try {
      const result = await api.getCardTrips(cardId)
      console.log('[OfflineAPI] getCardTrips succeeded:', cardId)
      return result
    } catch (error) {
      console.warn('[OfflineAPI] getCardTrips failed, returning empty array:', error.message)
      // Return empty array when offline - history won't work but app won't crash
      return []
    }
  },

  // Health check method
  async isOnline() {
    try {
      await api.getHealth()
      return true
    } catch (error) {
      return false
    }
  }
}