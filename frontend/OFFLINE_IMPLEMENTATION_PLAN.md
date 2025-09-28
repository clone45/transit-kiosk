# Offline-Capable Transit Kiosk Implementation Plan

## Overview
Implement a hybrid offline/online approach using a local `transitConfig.js` file that caches station and pricing data. The system will attempt to fetch fresh data from the backend on startup, but fall back to cached config if the backend is unavailable.

## Architecture Design

### Data Flow
1. **On Application Start:**
   - Attempt to fetch station and pricing data from backend
   - If successful → Update local transitConfig.js and use fresh data
   - If failed → Use existing transitConfig.js as fallback
   - Set global `isOfflineMode` flag

2. **During Operation:**
   - All fare calculations use local config data
   - API operations are wrapped with offline checks
   - Non-critical failures are queued for later sync
   - Critical features (History) are disabled in offline mode

## Implementation Steps

### 1. Create Transit Config Structure

#### File: `frontend/src/config/transitConfig.js`
```javascript
// Auto-generated config file - DO NOT EDIT MANUALLY
// Last updated: [timestamp]
export const transitConfig = {
  metadata: {
    lastUpdated: "2024-01-01T00:00:00Z",
    version: "1.0.0"
  },

  stations: [
    { id: 1, name: "Station Name", zone: 1 }
    // ... more stations
  ],

  pricing: [
    { stationA: 1, stationB: 2, fare: 3.50 }
    // ... more pricing pairs
  ],

  minimumFare: 2.25
}
```

### 2. Create Config Manager Service

#### File: `frontend/src/services/configManager.js`
**Purpose:** Manage config fetching, caching, and fallback logic

**Key Functions:**
- `initializeConfig()` - Try backend, fall back to local
- `updateConfigFromBackend()` - Fetch and save new config
- `loadLocalConfig()` - Load transitConfig.js
- `saveConfigToFile()` - Write updated config (development only)
- `getStations()` - Return stations from config
- `getPricing()` - Return pricing from config
- `getMinimumFare()` - Return minimum fare from config

### 3. Create Offline State Store

#### File: `frontend/src/stores/offlineStore.js`
**Purpose:** Track online/offline status and manage offline operations

**State:**
- `isOffline` - Boolean flag
- `pendingOperations` - Queue of operations to sync
- `disabledFeatures` - List of features unavailable offline

**Methods:**
- `setOfflineMode(status)`
- `queueOperation(operation)`
- `syncPendingOperations()`
- `isFeatureAvailable(featureName)`

### 4. Modify Existing Stores

#### `frontend/src/stores/fareStore.js`
**Changes:**
- Add `initializeFromConfig()` method
- Modify `fetchMinimumFare()` to check offline mode first
- Modify `preloadAllFares()` to load from config when offline
- Cache data structure remains unchanged

### 5. Create API Wrapper

#### File: `frontend/src/api/offlineClient.js`
**Purpose:** Wrap API calls with offline detection and queuing

**Key Functions:**
- `wrapApiCall(apiFunction, fallbackFunction)`
- `isBackendAvailable()` - Health check
- `queueForSync(operationType, data)`

### 6. Modify App.vue Initialization

#### `frontend/src/App.vue`
**Changes in `onMounted()`:**
```javascript
// Pseudo-code
1. Show "Initializing..." loader
2. Call configManager.initializeConfig()
3. Set offline mode based on result
4. Initialize fareStore from config/backend
5. Hide loader
6. If offline, show subtle indicator
```

### 7. Update Components for Offline Awareness

#### `frontend/src/layouts/KioskLayout.vue`
**Add:**
- Offline indicator (subtle icon/badge)
- Connection status monitoring
- Periodic retry logic for reconnection

#### `frontend/src/views/MenuView.vue`
**Changes:**
- Conditionally disable "History" button when offline
- Show offline tooltip on disabled features

#### `frontend/src/views/HistoryScanCardView.vue`
**Changes:**
- Check offline status on mount
- Redirect to menu with message if offline

### 8. Modify API Client

#### `frontend/src/api/client.js`
**Changes:**
- Add connection timeout handling
- Add retry logic with exponential backoff
- Return cached data when appropriate

### 9. Handle Offline Operations

#### Trip Creation/Completion
**When Offline:**
- Store trips in localStorage with `pending_sync` flag
- Generate temporary trip IDs
- Queue for backend sync when online

**Complete Operation Structure:**
```javascript
{
  id: "op_1234567890_trip_start",  // Unique operation ID
  timestamp: "2024-01-15T10:30:00Z",
  type: "TRIP_START",  // TRIP_START, TRIP_COMPLETE, CARD_CREATE, ADD_FUNDS
  priority: 2,  // 0-3, higher syncs first
  retryCount: 0,
  maxRetries: 3,
  nextRetryAt: null,  // For exponential backoff
  data: {
    cardUuid: "card-12345",
    stationId: 1,
    entryTime: "2024-01-15T10:30:00Z"
  },
  localState: {
    tempTripId: "temp_trip_001",  // Local reference
    completed: false,
    originalBalance: 20.00,
    newBalance: 17.50
  },
  dependencies: ["op_1234567889_card_create"],  // Must sync first
  idempotencyKey: "trip_start_card12345_1234567890"  // Prevent duplicates
}
```

### 10. Sync Strategy Options

#### Option A: Retry-Based Sync (Active Push)
**When to use:** Real-time sync requirements, reliable network

#### Option B: File-Based Sync (Passive Storage)
**When to use:** Intermittent connectivity, batch processing preferred

### 10A. File-Based Sync Implementation

#### File: `frontend/src/services/fileSyncManager.js`
**Purpose:** Write operations to files for later collection/processing by backend

**File Storage Strategy:**

##### A. Operation File Writer
```javascript
class OperationFileWriter {
  constructor() {
    this.pendingOps = this.loadPendingOps()
  }

  async writeOperation(operation) {
    // Add metadata
    const fileOp = {
      ...operation,
      id: `op_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      kioskId: this.getKioskId(),
      timestamp: new Date().toISOString(),
      syncStatus: 'pending'
    }

    // Store in IndexedDB for persistence
    await this.storeToDB(fileOp)

    // Add to pending operations list
    this.pendingOps.push(fileOp)

    return fileOp.id
  }

  async exportPendingOperations() {
    // Get all pending operations
    const operations = await this.getPendingFromDB()

    // Create file with timestamp
    const filename = `kiosk_${this.getKioskId()}_ops_${Date.now()}.json`
    const fileContent = {
      kioskId: this.getKioskId(),
      exportTime: new Date().toISOString(),
      operationCount: operations.length,
      operations: operations
    }

    return {
      filename,
      content: JSON.stringify(fileContent, null, 2)
    }
  }

  async markAsProcessed(operationIds) {
    // Backend confirms which operations were processed
    for (const id of operationIds) {
      await this.updateStatus(id, 'processed')
    }

    // Clean up old processed operations
    await this.pruneProcessedOps()
  }
}
```

##### B. File Generation Methods
```javascript
// Option 1: Using File System Access API (Chrome/Edge)
async function saveToFileSystem(content, filename) {
  if ('showSaveFilePicker' in window) {
    try {
      const handle = await window.showSaveFilePicker({
        suggestedName: filename,
        types: [{
          description: 'JSON Files',
          accept: { 'application/json': ['.json'] }
        }]
      })

      const writable = await handle.createWritable()
      await writable.write(content)
      await writable.close()

      return true
    } catch (err) {
      console.error('File save cancelled or failed', err)
      return false
    }
  }

  // Fallback to download
  return downloadFile(content, filename)
}

// Option 2: Auto-download to Downloads folder
function downloadFile(content, filename) {
  const blob = new Blob([content], { type: 'application/json' })
  const url = URL.createObjectURL(blob)

  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()

  URL.revokeObjectURL(url)
  return true
}

// Option 3: Store in IndexedDB with export endpoint
async function storeForBackendFetch(operations) {
  const db = await openDB('syncQueue', 1)
  const tx = db.transaction('pending', 'readwrite')

  for (const op of operations) {
    await tx.store.put(op)
  }

  await tx.done
}
```

##### C. Backend Fetch Endpoint
```javascript
// Frontend endpoint for backend to fetch pending operations
router.get('/api/sync/pending-operations', async (req, res) => {
  try {
    // Verify backend authentication
    const authToken = req.headers['x-backend-auth']
    if (!verifyBackendToken(authToken)) {
      return res.status(401).json({ error: 'Unauthorized' })
    }

    // Get all pending operations
    const operations = await fileSyncManager.exportPendingOperations()

    // Return as JSON
    res.json({
      kioskId: getKioskId(),
      timestamp: new Date().toISOString(),
      operations: operations.content
    })
  } catch (error) {
    res.status(500).json({ error: 'Failed to export operations' })
  }
})

// Endpoint to confirm processed operations
router.post('/api/sync/confirm-processed', async (req, res) => {
  const { operationIds } = req.body

  await fileSyncManager.markAsProcessed(operationIds)

  res.json({
    processed: operationIds.length,
    remaining: await fileSyncManager.getPendingCount()
  })
})
```

##### D. Backend Collection Service
```python
# Backend service to collect from kiosks
class KioskSyncCollector:
    def __init__(self):
        self.kiosk_registry = self.load_kiosk_registry()

    async def collect_all_kiosks(self):
        """Periodically called to sync all kiosks"""
        results = []

        for kiosk in self.kiosk_registry:
            try:
                result = await self.sync_kiosk(kiosk)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to sync kiosk {kiosk['id']}: {e}")

        return results

    async def sync_kiosk(self, kiosk):
        """Fetch and process operations from a single kiosk"""
        # Fetch pending operations
        response = await self.fetch_operations(kiosk['url'])

        if not response:
            return {'kioskId': kiosk['id'], 'status': 'unreachable'}

        operations = response['operations']
        processed = []
        failed = []

        # Process each operation
        for op in operations:
            try:
                await self.process_operation(op)
                processed.append(op['id'])
            except Exception as e:
                logger.error(f"Failed to process operation {op['id']}: {e}")
                failed.append(op['id'])

        # Confirm processed operations
        if processed:
            await self.confirm_processed(kiosk['url'], processed)

        return {
            'kioskId': kiosk['id'],
            'status': 'success',
            'processed': len(processed),
            'failed': len(failed)
        }

    async def fetch_operations(self, kiosk_url):
        """Fetch pending operations from kiosk"""
        try:
            response = requests.get(
                f"{kiosk_url}/api/sync/pending-operations",
                headers={'x-backend-auth': self.get_auth_token()},
                timeout=30
            )
            return response.json() if response.status_code == 200 else None
        except:
            return None

    async def process_operation(self, operation):
        """Process a single operation"""
        if operation['type'] == 'TRIP_START':
            return await self.process_trip_start(operation)
        elif operation['type'] == 'TRIP_COMPLETE':
            return await self.process_trip_complete(operation)
        elif operation['type'] == 'CARD_CREATE':
            return await self.process_card_create(operation)
        # ... etc
```

##### E. Manual File Collection Option
```javascript
// For completely offline scenarios - manual file collection
class ManualSyncExporter {
  async exportForUSB() {
    const operations = await this.getAllPendingOps()

    // Group by day for easier management
    const groupedOps = this.groupByDay(operations)

    // Create a zip file with all pending operations
    const zip = new JSZip()

    for (const [day, ops] of Object.entries(groupedOps)) {
      const filename = `ops_${day}.json`
      zip.file(filename, JSON.stringify(ops, null, 2))
    }

    // Add manifest
    zip.file('manifest.json', JSON.stringify({
      kioskId: this.getKioskId(),
      exportDate: new Date().toISOString(),
      fileCount: Object.keys(groupedOps).length,
      totalOperations: operations.length
    }))

    // Generate and download zip
    const blob = await zip.generateAsync({ type: 'blob' })
    downloadFile(blob, `kiosk_${this.getKioskId()}_export_${Date.now()}.zip`)
  }

  async importProcessedResults(file) {
    // Import file with list of processed operation IDs
    const content = await file.text()
    const result = JSON.parse(content)

    // Mark operations as processed
    for (const id of result.processedIds) {
      await this.markAsProcessed(id)
    }

    // Handle any errors reported
    for (const error of result.errors || []) {
      await this.handleSyncError(error)
    }
  }
}
```

##### F. Comparison with Retry-Based Sync

| Aspect | File-Based Sync | Retry-Based Sync |
|--------|----------------|------------------|
| **Network Usage** | Batch transfers | Continuous attempts |
| **Battery Usage** | Lower (no retry loops) | Higher (constant retries) |
| **Complexity** | Simpler frontend | Complex retry logic |
| **Real-time** | Delayed (batch) | Near real-time |
| **Reliability** | Very high | Depends on network |
| **Manual Fallback** | Easy (USB export) | Not available |
| **Backend Control** | Backend pulls when ready | Frontend pushes constantly |
| **Storage** | Files accumulate | Memory/localStorage only |

##### G. Hybrid Approach (Recommended)
```javascript
class HybridSyncManager {
  constructor() {
    this.mode = this.determineMode()
  }

  async syncOperation(operation) {
    if (this.isOnline() && this.mode === 'active') {
      // Try immediate sync
      try {
        return await this.immediateSy nc(operation)
      } catch (error) {
        // Fall back to file
        return await this.writeToFile(operation)
      }
    } else {
      // Offline or passive mode - straight to file
      return await this.writeToFile(operation)
    }
  }

  async performBatchSync() {
    // Called periodically or on-demand
    if (this.isOnline()) {
      const pending = await this.getPendingOperations()

      // Try to sync in batches
      const results = await this.batchSync(pending)

      // Write failures to file
      for (const failure of results.failed) {
        await this.writeToFile(failure)
      }
    }
  }
}
```

### 10B. Original Retry-Based Sync Implementation

**Note:** The original retry-based implementation (previously section 10) remains available as Option A for scenarios requiring real-time synchronization.

##### A. Queue Management (Retry-Based)
```javascript
class SyncQueue {
  constructor() {
    this.queue = this.loadQueue()
    this.deadLetterQueue = this.loadDeadLetterQueue()
  }

  add(operation) {
    operation.id = this.generateOperationId(operation.type)
    operation.timestamp = new Date().toISOString()
    operation.retryCount = 0
    this.queue.push(operation)
    this.saveQueue()
  }

  getNextBatch() {
    // Sort by priority, then timestamp
    return this.queue
      .filter(op => this.canSync(op))
      .sort((a, b) => {
        if (a.priority !== b.priority) return b.priority - a.priority
        return new Date(a.timestamp) - new Date(b.timestamp)
      })
      .slice(0, 10)  // Process in batches
  }

  canSync(operation) {
    // Check dependencies are resolved
    if (operation.dependencies?.length) {
      const unresolvedDeps = operation.dependencies.filter(
        depId => this.queue.find(op => op.id === depId)
      )
      if (unresolvedDeps.length > 0) return false
    }

    // Check retry timing
    if (operation.nextRetryAt && Date.now() < operation.nextRetryAt) {
      return false
    }

    return true
  }
}
```

##### B. Sync Process with Retry Logic
```javascript
class SyncManager {
  async startSync() {
    if (this.isSyncing) return
    this.isSyncing = true

    try {
      const batch = this.queue.getNextBatch()

      for (const operation of batch) {
        try {
          // Check for conflicts before syncing
          const conflict = await this.detectConflicts(operation)
          if (conflict.hasConflict) {
            await this.resolveConflict(operation, conflict)
            continue
          }

          // Attempt sync
          const result = await this.syncOperation(operation)

          // Success - update local state
          await this.reconcileLocalState(operation, result)
          this.queue.remove(operation.id)

        } catch (error) {
          await this.handleSyncError(operation, error)
        }
      }
    } finally {
      this.isSyncing = false

      // Schedule next sync if items remain
      if (this.queue.hasItems()) {
        setTimeout(() => this.startSync(), 30000)
      }
    }
  }

  async handleSyncError(operation, error) {
    operation.retryCount++

    if (operation.retryCount >= operation.maxRetries) {
      // Move to dead letter queue
      this.deadLetterQueue.add(operation, error.message)
      this.queue.remove(operation.id)
      console.error(`Operation ${operation.id} moved to DLQ`, error)
    } else {
      // Exponential backoff: 2s, 4s, 8s...
      const delay = Math.pow(2, operation.retryCount) * 1000
      operation.nextRetryAt = Date.now() + delay
      this.queue.update(operation)
    }
  }
}
```

##### C. Operation Type Handlers
```javascript
const operationHandlers = {
  async TRIP_START(operation, api) {
    // Check if card exists in DB first
    let card = await api.getCardByUuid(operation.data.cardUuid)
    if (!card) {
      // Card doesn't exist yet, create it
      const createOp = this.queue.find(
        op => op.type === 'CARD_CREATE' &&
              op.data.uuid === operation.data.cardUuid
      )
      if (createOp) {
        throw new DependencyError('Card not created yet')
      }
    }

    // Create trip
    const trip = await api.createTrip(
      operation.data.cardUuid,
      operation.data.stationId
    )

    return {
      success: true,
      tripId: trip.id,
      mapping: {
        tempId: operation.localState.tempTripId,
        realId: trip.id
      }
    }
  },

  async TRIP_COMPLETE(operation, api) {
    // Find the real trip ID
    const tripId = this.resolveTripId(operation.localState.tempTripId)

    if (!tripId) {
      throw new DependencyError('Trip start not synced yet')
    }

    const result = await api.completeTrip(
      tripId,
      operation.data.destinationStationId,
      operation.data.fare
    )

    return {
      success: true,
      transaction: result.transaction
    }
  },

  async CARD_CREATE(operation, api) {
    // Use idempotency key to prevent duplicates
    const existingCard = await api.getCardByUuid(operation.data.uuid)
    if (existingCard) {
      return {
        success: true,
        card: existingCard,
        wasAlreadyCreated: true
      }
    }

    const card = await api.createCard(
      operation.data.initialBalance,
      operation.data.uuid
    )

    return {
      success: true,
      card: card
    }
  }
}
```

##### D. Conflict Detection and Resolution
```javascript
class ConflictResolver {
  async detectConflicts(operation) {
    const conflicts = []

    if (operation.type === 'TRIP_START') {
      // Check if card already has an active trip
      const activeTrip = await api.getActiveTrip(operation.data.cardUuid)
      if (activeTrip && activeTrip.id !== operation.localState.tempTripId) {
        conflicts.push({
          type: 'DUPLICATE_ACTIVE_TRIP',
          serverData: activeTrip,
          localData: operation
        })
      }
    }

    if (operation.type === 'ADD_FUNDS') {
      // Check if balance has diverged
      const card = await api.getCardByUuid(operation.data.cardUuid)
      const expectedBalance = operation.localState.originalBalance
      if (Math.abs(card.balance - expectedBalance) > 0.01) {
        conflicts.push({
          type: 'BALANCE_MISMATCH',
          serverBalance: card.balance,
          localBalance: expectedBalance
        })
      }
    }

    return conflicts
  }

  async resolveConflict(operation, conflicts) {
    for (const conflict of conflicts) {
      switch (conflict.type) {
        case 'DUPLICATE_ACTIVE_TRIP':
          // Use timestamp to determine which is newer
          const serverTime = new Date(conflict.serverData.startTime)
          const localTime = new Date(operation.data.entryTime)

          if (localTime > serverTime) {
            // Local is newer, cancel server trip
            await api.cancelTrip(conflict.serverData.id)
            return true  // Retry operation
          } else {
            // Server is newer, abandon local
            this.queue.remove(operation.id)
            return false
          }

        case 'BALANCE_MISMATCH':
          // Calculate adjustment needed
          const adjustment = operation.data.amount
          const newBalance = conflict.serverBalance + adjustment
          await api.setCardBalance(operation.data.cardUuid, newBalance)
          return false  // Operation complete
      }
    }
  }
}
```

##### E. Connection Monitoring
```javascript
class ConnectionMonitor {
  constructor(syncManager) {
    this.syncManager = syncManager
    this.isOnline = navigator.onLine
    this.checkInterval = 30000  // 30 seconds
    this.retryBackoff = 1000  // Start with 1 second

    this.init()
  }

  init() {
    // Browser events
    window.addEventListener('online', () => this.handleOnline())
    window.addEventListener('offline', () => this.handleOffline())

    // Periodic health checks
    this.startHealthCheck()
  }

  async startHealthCheck() {
    if (!this.isOnline) {
      // Don't check if we know we're offline
      setTimeout(() => this.startHealthCheck(), this.checkInterval)
      return
    }

    try {
      await api.getHealth()
      this.retryBackoff = 1000  // Reset backoff on success

      if (!this.wasOnline) {
        this.handleOnline()
      }
    } catch (error) {
      if (this.wasOnline) {
        this.handleOffline()
      }
      // Exponential backoff for health checks
      this.retryBackoff = Math.min(this.retryBackoff * 2, 60000)
    }

    setTimeout(
      () => this.startHealthCheck(),
      this.isOnline ? this.checkInterval : this.retryBackoff
    )
  }

  handleOnline() {
    this.isOnline = true
    this.wasOnline = true
    offlineStore.setOfflineMode(false)
    showToast('Connection restored - syncing data...')
    this.syncManager.startSync()
  }

  handleOffline() {
    this.isOnline = false
    this.wasOnline = false
    offlineStore.setOfflineMode(true)
    showToast('Working offline - data will sync when connection returns')
  }
}
```

##### F. Local State Reconciliation
```javascript
class StateReconciler {
  async reconcileAfterSync(operation, serverResponse) {
    switch(operation.type) {
      case 'TRIP_START':
        // Update all references from temp ID to real ID
        const tempId = operation.localState.tempTripId
        const realId = serverResponse.tripId

        // Update in localStorage
        const trips = JSON.parse(localStorage.getItem('active_trips') || '{}')
        if (trips[tempId]) {
          trips[realId] = trips[tempId]
          delete trips[tempId]
          localStorage.setItem('active_trips', JSON.stringify(trips))
        }

        // Update in testConfig if needed
        testConfig.updateTripId(tempId, realId)
        break

      case 'CARD_CREATE':
        // Update UUID if server assigned different one
        if (serverResponse.card.uuid !== operation.data.uuid) {
          const oldUuid = operation.data.uuid
          const newUuid = serverResponse.card.uuid

          // Migrate all local references
          testConfig.migrateCardUuid(oldUuid, newUuid)

          // Update any pending operations
          this.queue.updateCardReferences(oldUuid, newUuid)
        }
        break

      case 'ADD_FUNDS':
        // Verify final balance matches expectations
        const expectedBalance = operation.localState.newBalance
        const actualBalance = serverResponse.balance

        if (Math.abs(expectedBalance - actualBalance) > 0.01) {
          console.warn('Balance mismatch after sync:', {
            expected: expectedBalance,
            actual: actualBalance
          })
          // Update local balance to match server
          testConfig.writeCardBalance(
            operation.data.cardUuid,
            actualBalance
          )
        }
        break
    }
  }

  async cleanupAfterFullSync() {
    // Remove completed operations from queue
    const completed = this.queue.filter(op => op.synced)
    completed.forEach(op => this.queue.remove(op.id))

    // Clear temporary IDs
    localStorage.removeItem('temp_id_mappings')

    // Compact localStorage if needed
    this.compactLocalStorage()
  }
}
```

**Priority System:**
```javascript
const SYNC_PRIORITIES = {
  CARD_CREATE: 3,      // Highest - cards must exist first
  TRIP_START: 2,       // High - must record entry
  TRIP_COMPLETE: 2,    // High - must record fare collection
  ADD_FUNDS: 1,        // Medium - balance updates
  TRANSACTION_LOG: 0   // Low - audit trail
}
```

**Dead Letter Queue Management:**
```javascript
class DeadLetterQueue {
  constructor() {
    this.items = JSON.parse(localStorage.getItem('dlq') || '[]')
  }

  add(operation, reason) {
    this.items.push({
      ...operation,
      movedToDLQ: new Date().toISOString(),
      failureReason: reason,
      originalId: operation.id
    })
    this.save()

    // Alert if DLQ is growing
    if (this.items.length > 10) {
      console.error('Dead letter queue has', this.items.length, 'items')
      this.notifySupport()
    }
  }

  retryAll() {
    const items = [...this.items]
    this.items = []
    this.save()

    items.forEach(item => {
      delete item.movedToDLQ
      delete item.failureReason
      item.retryCount = 0
      syncQueue.add(item)
    })
  }

  save() {
    localStorage.setItem('dlq', JSON.stringify(this.items))
  }
}
```

### 11. Development Tools

#### File: `frontend/scripts/generateConfig.js`
**Purpose:** Node script to generate transitConfig.js from backend
**Usage:** `npm run generate-config`

### 12. Error Handling

#### Graceful Degradation Strategy:
- **Entry/Exit:** ✅ Full functionality with local config
- **Add Fare:** ✅ Full functionality, sync later
- **Purchase Card:** ✅ Full functionality, sync later
- **History:** ⚠️ Disabled (shows message)
- **Fare Calculation:** ✅ Uses local config

#### User Notifications:
- Subtle offline indicator in corner
- Toast notifications for mode changes
- Clear messaging on disabled features

## Choosing a Sync Strategy

### Decision Matrix

| Scenario | Recommended Approach | Rationale |
|----------|---------------------|-----------|
| **Subway stations with intermittent connectivity** | File-Based | Backend can batch collect during off-peak |
| **Bus terminals with reliable WiFi** | Retry-Based | Real-time updates for operations center |
| **Remote stations with daily dial-up** | File-Based | Accumulate day's operations, sync overnight |
| **High-traffic urban stations** | Hybrid | Immediate sync when possible, file fallback |
| **Ferries with offline periods** | File-Based | Sync when docked at terminal |

### Implementation Recommendation

**Start with File-Based Approach because:**
1. Simpler to implement and test
2. More resilient to network issues
3. Provides manual fallback option
4. Lower battery/CPU usage on kiosks
5. Backend controls sync timing and load

**Add Retry-Based Later if Needed for:**
1. Real-time fraud detection
2. Immediate balance updates across network
3. Live operations monitoring
4. Customer service requirements

## Real-World Scenarios

### Scenario 1: Complete Offline Journey
```
Timeline:
09:00 - Internet outage begins at station
09:15 - User A purchases new card ($30)
09:20 - User A enters Station 1
09:45 - User A exits Station 2 (fare: $2.50, balance: $27.50)
10:00 - User A adds $10 to card (balance: $37.50)
10:15 - Internet restored
10:15 - Sync process:
  1. Create card in DB with initial $30
  2. Record trip start at Station 1
  3. Record trip completion with $2.50 fare
  4. Record $10 balance addition
  5. Final DB balance: $37.50 ✓
```

### Scenario 2: Multi-Kiosk Conflict
```
Timeline:
09:00 - Kiosk A goes offline
09:10 - User enters at Kiosk A (offline) - Station 1
09:11 - Kiosk A records entry locally
09:30 - User exits at Kiosk B (online) - Station 3
09:31 - Kiosk B can't find active trip (Kiosk A offline)
09:31 - Kiosk B creates "exit-only" transaction
10:00 - Kiosk A comes online
10:01 - Sync detects orphaned entry
10:01 - Creates retroactive trip with estimated fare
```

### Scenario 3: Partial Sync Failure
```
Operations Queue:
1. [CARD_CREATE] - Success ✓
2. [TRIP_START] - Success ✓
3. [TRIP_COMPLETE] - Network timeout ✗
4. [ADD_FUNDS] - Not attempted

Recovery:
- Operation 3 retry count incremented
- Operation 3 scheduled for retry in 2 seconds
- Operation 4 waits (depends on trip completion)
- Next sync attempt processes 3 & 4
```

## Edge Cases and Solutions

### 1. Storage Quota Exceeded
```javascript
function handleStorageQuota() {
  const usage = await navigator.storage.estimate()
  if (usage.usage / usage.quota > 0.9) {
    // Prune old completed operations
    pruneOldOperations(30) // Keep 30 days

    // Compress operation data
    compressOperationQueue()

    // Alert user if still critical
    if (usage.usage / usage.quota > 0.95) {
      showWarning("Storage nearly full - some features limited")
    }
  }
}
```

### 2. Clock Skew Handling
```javascript
class TimeSync {
  async getServerTime() {
    const response = await api.getServerTime()
    this.serverOffset = response.timestamp - Date.now()
    return this.serverOffset
  }

  getAdjustedTime() {
    return new Date(Date.now() + (this.serverOffset || 0))
  }
}
```

### 3. Duplicate Prevention
```javascript
function generateIdempotencyKey(operation) {
  const components = [
    operation.type,
    operation.data.cardUuid,
    operation.data.stationId,
    Math.floor(operation.timestamp / 60000) // 1-minute window
  ]
  return components.join('_')
}
```

### 4. Browser/Tab Closing
```javascript
window.addEventListener('beforeunload', (e) => {
  if (syncQueue.hasPendingCriticalOps()) {
    e.preventDefault()
    e.returnValue = 'You have pending transit operations. Are you sure?'

    // Attempt quick sync
    syncManager.quickSync()
  }
})
```

## Testing Plan

### Manual Testing Scenarios:
1. **Normal Flow**
   - Start app with backend running
   - Verify config updates from backend
   - Complete full trip cycle

2. **Offline Start**
   - Kill backend before starting app
   - Verify app loads with cached config
   - Test all offline operations

3. **Connection Loss**
   - Start normal, then kill backend mid-operation
   - Verify graceful degradation
   - Complete operations offline

4. **Connection Recovery**
   - Work offline, accumulate operations
   - Restore backend
   - Verify all operations sync correctly
   - Check for duplicates

5. **Conflict Resolution**
   - Create conflicting operations on two devices
   - Verify resolution strategy works
   - No data loss or corruption

6. **Edge Cases**
   - Fill localStorage to quota
   - Test with system clock changes
   - Close browser during sync
   - Rapid online/offline toggling

### Automated Tests:
```javascript
describe('Sync Manager', () => {
  test('handles dependency resolution', async () => {
    const queue = new SyncQueue()
    queue.add({
      type: 'TRIP_COMPLETE',
      dependencies: ['op_123_trip_start']
    })
    queue.add({
      id: 'op_123_trip_start',
      type: 'TRIP_START'
    })

    const batch = queue.getNextBatch()
    expect(batch[0].type).toBe('TRIP_START')
  })

  test('implements exponential backoff', async () => {
    const op = { retryCount: 2, maxRetries: 3 }
    syncManager.handleSyncError(op, new Error())

    expect(op.nextRetryAt).toBeGreaterThan(Date.now() + 3000)
    expect(op.nextRetryAt).toBeLessThan(Date.now() + 5000)
  })

  test('detects balance conflicts', async () => {
    const conflicts = await conflictResolver.detectConflicts({
      type: 'ADD_FUNDS',
      localState: { originalBalance: 10 },
      data: { cardUuid: 'test' }
    })

    expect(conflicts).toContainEqual(
      expect.objectContaining({ type: 'BALANCE_MISMATCH' })
    )
  })
})

## Rollback Plan

If offline mode causes issues:
1. Remove offline checks from App.vue
2. Revert to direct API calls
3. Remove transitConfig.js
4. System continues working as before

## Migration Notes

### Backward Compatibility:
- Existing localStorage data remains compatible
- No changes to backend API required
- Can be deployed incrementally

### Performance Considerations:
- Config file should be <50KB
- Load time impact: ~10ms
- Memory usage: Negligible

## Future Enhancements

### Phase 2 Possibilities:
- Service Worker for true offline PWA
- IndexedDB for larger data storage
- Background sync API for automatic retries
- Offline trip history using localStorage
- Config versioning and migrations

## Development Order

1. **Week 1:** Config structure and manager
2. **Week 1:** Offline store and API wrapper
3. **Week 2:** Modify initialization flow
4. **Week 2:** Update components for offline
5. **Week 3:** Implement sync manager
6. **Week 3:** Testing and refinement

## Success Metrics

- App starts within 2 seconds regardless of backend status
- All core transit functions work offline
- Zero data loss when syncing
- Clear user feedback about system status