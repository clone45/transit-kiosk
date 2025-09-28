# Offline MVP Implementation Plan

## Goal
Create a minimal viable offline-capable transit kiosk that:
1. Caches station and pricing data locally for offline fare calculations
2. Writes failed operations to files for manual recovery (no auto-sync)
3. Continues to function during network outages

## Core Principle
**Write and forget** - When offline, save operations to files. Don't implement automatic recovery. Focus on not losing data.

## Implementation Steps

### 1. Create Transit Config File

#### File: `frontend/src/config/transitConfig.js`
```javascript
// Static config file with station and pricing data
export const transitConfig = {
  lastUpdated: "2024-01-01T00:00:00Z",

  stations: [
    { id: 1, name: "Downtown", zone: 1 },
    { id: 2, name: "Airport", zone: 3 },
    { id: 3, name: "University", zone: 2 }
    // ... all stations
  ],

  pricing: [
    { stationA: 1, stationB: 2, fare: 3.50 },
    { stationA: 1, stationB: 3, fare: 2.25 },
    { stationA: 2, stationB: 3, fare: 2.75 }
    // ... all pricing pairs
  ],

  minimumFare: 2.25
}
```

### 2. Create Config Manager

#### File: `frontend/src/services/configManager.js`
```javascript
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
      const [stations, pricing, minFare] = await Promise.all([
        api.getStations(),
        api.getAllPricing(),
        api.getMinimumFare()
      ])

      this.config = {
        stations,
        pricing,
        minimumFare: minFare.minimum_fare
      }

      this.startedOffline = false
      console.log('Using fresh config from backend')
    } catch (error) {
      // Fall back to static config
      this.loadStaticConfig()
      this.startedOffline = true
      console.warn('Backend unavailable at startup, using static config')
    }
  }

  loadStaticConfig() {
    // Load the static config as fallback
    this.config = {
      stations: transitConfig.stations,
      pricing: transitConfig.pricing,
      minimumFare: transitConfig.minimumFare
    }
    console.log('Loaded static config')
  }

  ensureConfig() {
    // Make sure we have config, even if network died after startup
    if (!this.config) {
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
    return found?.fare || this.getMinimumFare()
  }

  getMinimumFare() {
    this.ensureConfig()
    return this.config?.minimumFare || transitConfig.minimumFare || 2.25
  }

  startedInOfflineMode() {
    return this.startedOffline
  }
}

export const configManager = new ConfigManager()
```

### 3. Create Failed Operations Writer

#### File: `frontend/src/services/failedOpsWriter.js`
```javascript
class FailedOpsWriter {
  constructor() {
    this.failedOps = []
  }

  async writeFailedOperation(operation) {
    const failedOp = {
      id: `failed_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
      operation: operation,
      error: 'Network unavailable'
    }

    // Add to memory
    this.failedOps.push(failedOp)

    // Store in localStorage as backup
    this.saveToLocalStorage()

    // Export to file
    this.exportToFile()

    return failedOp.id
  }

  saveToLocalStorage() {
    try {
      const existing = JSON.parse(localStorage.getItem('failed_operations') || '[]')
      existing.push(...this.failedOps)

      // Keep only last 100 operations to prevent storage overflow
      const trimmed = existing.slice(-100)
      localStorage.setItem('failed_operations', JSON.stringify(trimmed))
    } catch (error) {
      console.error('Failed to save to localStorage:', error)
    }
  }

  exportToFile() {
    if (this.failedOps.length === 0) return

    const content = JSON.stringify({
      exportTime: new Date().toISOString(),
      kioskId: this.getKioskId(),
      operations: this.failedOps
    }, null, 2)

    const blob = new Blob([content], { type: 'application/json' })
    const url = URL.createObjectURL(blob)

    // Auto-download to Downloads folder
    const a = document.createElement('a')
    a.href = url
    a.download = `failed_ops_${Date.now()}.json`
    a.click()

    URL.revokeObjectURL(url)

    // Clear after export
    this.failedOps = []
  }

  getKioskId() {
    // Get or generate a unique kiosk ID
    let kioskId = localStorage.getItem('kiosk_id')
    if (!kioskId) {
      kioskId = `kiosk_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      localStorage.setItem('kiosk_id', kioskId)
    }
    return kioskId
  }
}

export const failedOpsWriter = new FailedOpsWriter()
```

### 4. Modify API Client to Handle Offline

#### File: `frontend/src/api/offlineWrapper.js`
```javascript
import { api } from './client'
import { configManager } from '../services/configManager'
import { failedOpsWriter } from '../services/failedOpsWriter'

export const offlineApi = {
  // Write operations - always try API first, write to file if failed
  async createTrip(cardUuid, stationId) {
    try {
      // Always try the real API first
      return await api.createTrip(cardUuid, stationId)
    } catch (error) {
      // Network failed - write to file and continue
      console.warn('createTrip failed, writing to file:', error.message)

      await failedOpsWriter.writeFailedOperation({
        type: 'CREATE_TRIP',
        data: { cardUuid, stationId },
        timestamp: new Date().toISOString()
      })

      // Return a fake response so the app continues
      return {
        id: `temp_trip_${Date.now()}`,
        status: 'offline_pending'
      }
    }
  },

  async completeTrip(tripId, destinationStationId, fare) {
    try {
      // Always try the real API first
      return await api.completeTrip(tripId, destinationStationId, fare)
    } catch (error) {
      console.warn('completeTrip failed, writing to file:', error.message)

      await failedOpsWriter.writeFailedOperation({
        type: 'COMPLETE_TRIP',
        data: { tripId, destinationStationId, fare },
        timestamp: new Date().toISOString()
      })

      return { status: 'offline_pending' }
    }
  },

  async createCard(initialBalance, uuid) {
    try {
      return await api.createCard(initialBalance, uuid)
    } catch (error) {
      console.warn('createCard failed, writing to file:', error.message)

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
      return await api.addFunds(cardId, amount)
    } catch (error) {
      console.warn('addFunds failed, writing to file:', error.message)

      await failedOpsWriter.writeFailedOperation({
        type: 'ADD_FUNDS',
        data: { cardId, amount },
        timestamp: new Date().toISOString()
      })

      return { status: 'offline_pending' }
    }
  },

  // Read operations - try API first, fall back to config
  async getStations() {
    try {
      // Try to get fresh data
      return await api.getStations()
    } catch (error) {
      // Network failed - use config
      console.warn('getStations failed, using config:', error.message)
      return configManager.getStations()
    }
  },

  async getFareBetweenStations(stationA, stationB) {
    try {
      // Try to get fresh fare
      return await api.getFareBetweenStations(stationA, stationB)
    } catch (error) {
      // Network failed - use config
      console.warn('getFareBetweenStations failed, using config:', error.message)
      return {
        price: configManager.getPricing(stationA, stationB)
      }
    }
  },

  async getMinimumFare() {
    try {
      // Try to get fresh minimum fare
      return await api.getMinimumFare()
    } catch (error) {
      // Network failed - use config
      console.warn('getMinimumFare failed, using config:', error.message)
      return {
        minimum_fare: configManager.getMinimumFare()
      }
    }
  },

  // Operations that should fail gracefully
  async getCardByUuid(uuid) {
    try {
      return await api.getCardByUuid(uuid)
    } catch (error) {
      console.warn('getCardByUuid failed, returning null:', error.message)
      // Return null to indicate card not found/not accessible
      return null
    }
  },

  async getActiveTrip(cardId) {
    try {
      return await api.getActiveTrip(cardId)
    } catch (error) {
      console.warn('getActiveTrip failed, returning null:', error.message)
      return null
    }
  },

  async getCardTrips(cardId) {
    try {
      return await api.getCardTrips(cardId)
    } catch (error) {
      console.warn('getCardTrips failed, returning empty array:', error.message)
      // Return empty array when offline
      return []
    }
  }
}
```

### 5. Update App.vue Initialization

#### Modify: `frontend/src/App.vue`
```javascript
import { configManager } from './services/configManager'
import { offlineApi } from './api/offlineWrapper'

onMounted(async () => {
  // Initialize config (will use backend or fall back to static)
  await configManager.initialize()

  // Update fareStore to use config instead of API
  fareStore.initializeFromConfig(configManager)

  // Show offline indicator if needed
  if (configManager.isOfflineMode()) {
    console.warn('Running in offline mode')
    // Optionally show a subtle indicator in UI
  }
})
```

### 6. Update Stores to Use Config

#### Modify: `frontend/src/stores/fareStore.js`
```javascript
export const fareStore = {
  // ... existing code ...

  initializeFromConfig(configManager) {
    this.minimumFare.value = configManager.getMinimumFare()

    // Cache all pricing
    const pricing = configManager.config?.pricing || []
    for (const p of pricing) {
      const key = p.stationA < p.stationB
        ? `${p.stationA}-${p.stationB}`
        : `${p.stationB}-${p.stationA}`
      this.fareCache.value[key] = p.fare
    }
  },

  // No longer needs async fetching - just returns cached value
  getMinimumFare() {
    return this.minimumFare.value
  },

  getFareBetweenStations(stationA, stationB) {
    const key = stationA < stationB
      ? `${stationA}-${stationB}`
      : `${stationB}-${stationA}`
    return this.fareCache.value[key] || this.minimumFare.value
  }
}
```

### 7. Update Components to Use Offline API

#### Example: `frontend/src/layouts/KioskLayout.vue`
Replace `api` imports with `offlineApi`:

```javascript
import { offlineApi } from '../api/offlineWrapper'

// Change all api calls to offlineApi
// api.createTrip() → offlineApi.createTrip()
// api.completeTrip() → offlineApi.completeTrip()
```

### 8. Add Manual Export Button (Optional)

#### Add to: `frontend/src/layouts/KioskLayout.vue`
```javascript
// In debug panel, add export button
const exportFailedOps = () => {
  const ops = JSON.parse(localStorage.getItem('failed_operations') || '[]')

  if (ops.length === 0) {
    alert('No failed operations to export')
    return
  }

  const content = JSON.stringify(ops, null, 2)
  const blob = new Blob([content], { type: 'application/json' })
  const url = URL.createObjectURL(blob)

  const a = document.createElement('a')
  a.href = url
  a.download = `all_failed_ops_${Date.now()}.json`
  a.click()

  URL.revokeObjectURL(url)
}
```

## How Offline Behavior Works

### Scenario A: Backend Down at Startup
1. App tries to fetch config from backend → fails
2. Loads static config immediately
3. All operations use static config
4. Failed writes go to files

### Scenario B: Network Dies After Startup
1. App started fine with fresh backend config
2. Network dies during operation
3. Each API call now follows this pattern:
   - **Read operations** (fares, stations): Try API → fail → use cached/static config
   - **Write operations** (trips, payments): Try API → fail → write to file
4. App continues working seamlessly

### Key Design: "Always Try First"
- **No complex state tracking** - each operation independently tries the API
- **No "offline mode" flag** - just try/catch at each call
- **Immediate fallback** - if API fails, instantly use local data

## What This MVP Does

✅ **Works Offline**: Handles both startup and runtime network failures
✅ **Preserves Data**: Writes failed operations to files
✅ **No Data Loss**: Operations saved to localStorage + auto-downloaded
✅ **Simple**: No retry logic, no sync complexity
✅ **Seamless Fallback**: Users won't notice when network dies
✅ **Debuggable**: JSON files can be manually inspected

## What This MVP Doesn't Do

❌ **No Auto-Sync**: Files must be manually processed
❌ **No Conflict Resolution**: That's a future problem
❌ **No Real-Time Updates**: Accepts that data is delayed
❌ **No Retry Logic**: Write once and move on

## Manual Recovery Process

When network is restored:
1. Collect JSON files from kiosk Downloads folder
2. Process files with a backend script
3. Manually handle any conflicts
4. Clear localStorage once processed

## Testing the MVP

### Test Case 1: Backend Down at Startup
1. **Kill backend**: Stop the backend server
2. **Start frontend**: App should load with static config
3. **Verify console**: Should see "Backend unavailable at startup, using static config"
4. **Test operations**: Entry/exit should work using static fares
5. **Check Downloads**: Should see failed_ops_*.json files for write operations

### Test Case 2: Network Dies After Startup
1. **Start normally**: App loads with fresh backend config
2. **Verify console**: Should see "Using fresh config from backend"
3. **Disconnect network**: Unplug ethernet or disable WiFi
4. **Test operations**: Entry/exit should continue working
5. **Check console**: Should see "createTrip failed, writing to file" messages
6. **Check Downloads**: Should see new failed_ops_*.json files

### Test Case 3: Network Recovery
1. **Start offline**: Begin with backend down
2. **Reconnect**: Restore network connection
3. **Test operations**: Should now succeed against real API
4. **Verify**: New operations go to backend, not files

### What to Look For:
- ✅ **No user-visible errors** - app continues working
- ✅ **JSON files created** in Downloads folder
- ✅ **Console warnings** but no exceptions
- ✅ **Fare calculations work** using static config
- ✅ **Operations complete** even when writes fail

## Next Steps (Post-MVP)

Only after MVP is working:
1. Add backend endpoint to receive failed operations
2. Implement basic sync without retry logic
3. Add conflict detection (not resolution)
4. Build admin UI to review conflicts

## Time Estimate

- **Config setup**: 2 hours
- **Offline wrapper**: 2 hours
- **Testing**: 2 hours
- **Total MVP**: ~6 hours

This MVP focuses purely on **not losing data** when offline, which is the most critical requirement. Everything else can be built on top of this foundation.