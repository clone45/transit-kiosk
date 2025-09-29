// Simple test script to verify offline functionality
import { configManager } from './src/services/configManager.js'
import { offlineApi } from './src/api/offlineWrapper.js'
import { failedOpsWriter } from './src/services/failedOpsWriter.js'

console.log('🧪 Testing offline functionality...\n')

// Test 1: ConfigManager initialization (should fall back to static config)
console.log('1️⃣ Testing configManager initialization with backend down...')
try {
  await configManager.initialize()

  if (configManager.startedInOfflineMode()) {
    console.log('✅ ConfigManager correctly detected offline mode')
  } else {
    console.log('❌ ConfigManager should have detected offline mode')
  }

  // Test config data
  const stations = configManager.getStations()
  const fare = configManager.getPricing(1, 2)
  const minFare = configManager.getMinimumFare()

  console.log(`   📍 Stations loaded: ${stations.length}`)
  console.log(`   💰 Fare 1→2: $${fare}`)
  console.log(`   💰 Min fare: $${minFare}`)
} catch (error) {
  console.log('❌ ConfigManager initialization failed:', error.message)
}

console.log('\n2️⃣ Testing offline API wrapper...')

// Test 2: Read operations (should use static config)
try {
  const stations = await offlineApi.getStations()
  const fareData = await offlineApi.getFareBetweenStations(1, 2)
  const minFareData = await offlineApi.getMinimumFare()

  console.log('✅ Read operations work offline:')
  console.log(`   📍 Stations: ${stations.length} loaded`)
  console.log(`   💰 Fare API: $${fareData.price}`)
  console.log(`   💰 Min fare API: $${minFareData.minimum_fare}`)
} catch (error) {
  console.log('❌ Read operations failed:', error.message)
}

// Test 3: Write operations (should write to files)
console.log('\n3️⃣ Testing write operations (should save to files)...')

try {
  // Test create trip
  const tripResult = await offlineApi.createTrip('test-card-123', 1)
  console.log('✅ createTrip:', tripResult.status)

  // Test complete trip
  const completeResult = await offlineApi.completeTrip(tripResult.id, 2, 3.25)
  console.log('✅ completeTrip:', completeResult.status)

  // Test create card
  const cardResult = await offlineApi.createCard(20.00, 'new-card-456')
  console.log('✅ createCard:', cardResult.status)

  console.log('\n📁 Failed operations written to files. Check Downloads folder!')

} catch (error) {
  console.log('❌ Write operations failed:', error.message)
}

console.log('\n🎉 Offline testing complete!')