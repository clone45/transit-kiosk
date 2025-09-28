<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { navigationStore } from '../stores/navigationStore'
import { api } from '../api/client'
import { historyStore } from '../stores/historyStore'
import KioskButton from '../components/KioskButton.vue'

const router = useRouter()

const trips = ref([])
const loading = ref(true)
const error = ref(null)
const stations = ref({})

const scrollContainer = ref(null)
const isDragging = ref(false)
const startY = ref(0)
const scrollTop = ref(0)

async function fetchTrips() {
  try {
    loading.value = true
    error.value = null

    console.log('[HistoryView] Starting to fetch trip history...')

    const cardData = historyStore.scannedCard.value
    console.log('[HistoryView] Card data from scanned store:', cardData)

    if (!cardData) {
      console.error('[HistoryView] No card scanned for history access')
      error.value = 'No card scanned'
      return
    }

    console.log('[HistoryView] Fetching card from DB with UUID:', cardData.uuid)
    const card = await api.getCardByUuid(cardData.uuid)
    console.log('[HistoryView] Card from DB:', card)

    if (!card) {
      console.error('[HistoryView] Card not found in database')
      error.value = 'Card not found'
      return
    }

    console.log('[HistoryView] Fetching trips for card ID:', card.id)
    const tripData = await api.getCardTrips(card.id)
    console.log('[HistoryView] Raw trip data from API:', tripData)
    console.log('[HistoryView] Total trips received:', tripData.length)

    console.log('[HistoryView] Fetching station names...')
    const stationsData = await api.getStations()
    console.log('[HistoryView] Stations data:', stationsData)

    for (const station of stationsData) {
      stations.value[station.id] = station.name
    }
    console.log('[HistoryView] Station ID to name map:', stations.value)

    // Filter only completed trips
    const completedTrips = tripData.filter(trip => trip.status === 'completed')
    console.log('[HistoryView] Completed trips:', completedTrips.length, 'out of', tripData.length)

    // Log any non-completed trips
    const nonCompletedTrips = tripData.filter(trip => trip.status !== 'completed')
    if (nonCompletedTrips.length > 0) {
      console.log('[HistoryView] Non-completed trips found:', nonCompletedTrips)
    }

    // Sort and transform
    trips.value = completedTrips
      .sort((a, b) => {
        // Parse datetime - remove microseconds for JavaScript compatibility
        const dateStringA = (a.completion_time || a.start_time).replace(/\.\d{6}$/, '')
        const dateStringB = (b.completion_time || b.start_time).replace(/\.\d{6}$/, '')
        const dateA = new Date(dateStringA)
        const dateB = new Date(dateStringB)
        console.log(`[HistoryView] Sorting: Trip ${b.id} (${dateB.toISOString()}) vs Trip ${a.id} (${dateA.toISOString()})`)
        return dateB - dateA  // Sort newest first
      })
      .slice(0, 50)
      .map(trip => {
        // Parse datetime - remove microseconds for JavaScript compatibility
        const dateString = (trip.completion_time || trip.start_time).replace(/\.\d{6}$/, '')
        const completedAt = new Date(dateString)

        const transformed = {
          id: trip.id,
          date: completedAt.toLocaleDateString(),
          time: completedAt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          from: stations.value[trip.source_station_id] || `Station ${trip.source_station_id}`,
          to: trip.destination_station_id ? (stations.value[trip.destination_station_id] || `Station ${trip.destination_station_id}`) : 'In Progress',
          fare: trip.cost || 0,  // Backend uses 'cost' not 'fare'
          status: trip.status
        }
        console.log(`[HistoryView] Transformed trip ${trip.id}:`, {
          raw: trip,
          transformed: transformed
        })
        return transformed
      })

    console.log('[HistoryView] Final processed trips for display:', trips.value)
    console.log('[HistoryView] Successfully loaded', trips.value.length, 'trips')
  } catch (err) {
    console.error('[HistoryView] Error fetching trips:', err)
    console.error('[HistoryView] Error details:', err.response || err.message)
    error.value = 'Failed to load trip history'
  } finally {
    loading.value = false
    console.log('[HistoryView] Fetch complete. Loading:', loading.value, 'Error:', error.value)
  }
}

const handleMouseDown = (e) => {
  isDragging.value = true
  startY.value = e.pageY - scrollContainer.value.offsetTop
  scrollTop.value = scrollContainer.value.scrollTop
  scrollContainer.value.style.cursor = 'grabbing'
}

const handleMouseMove = (e) => {
  if (!isDragging.value) return
  e.preventDefault()
  const y = e.pageY - scrollContainer.value.offsetTop
  const walk = (y - startY.value) * 2
  scrollContainer.value.scrollTop = scrollTop.value - walk
}

const handleMouseUp = () => {
  isDragging.value = false
  scrollContainer.value.style.cursor = 'grab'
}

const handleMouseLeave = () => {
  isDragging.value = false
  scrollContainer.value.style.cursor = 'grab'
}

const handleBack = () => {
  historyStore.reset()
  router.push(navigationStore.getReturnPath())
}

onMounted(() => {
  fetchTrips()
})
</script>

<template>
  <div id="history-view" class="h-full flex flex-col">
    <div id="history-header" class="text-center pt-8 px-8 pb-4">
      <h1 id="history-title" class="text-6xl font-semibold text-gray-900">Trip History</h1>
    </div>

    <div
      ref="scrollContainer"
      id="history-content"
      class="flex-1 overflow-y-auto px-8 pb-4 select-none"
      style="scrollbar-width: auto; scrollbar-color: #4B5563 #E5E7EB; cursor: grab;"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @mouseleave="handleMouseLeave"
      @touchstart="handleMouseDown"
      @touchmove="handleMouseMove"
      @touchend="handleMouseUp"
    >
      <div v-if="loading" class="h-full flex items-center justify-center">
        <p class="text-3xl text-gray-600">Loading trips...</p>
      </div>

      <div v-else-if="error" class="h-full flex items-center justify-center">
        <p class="text-3xl text-red-600">{{ error }}</p>
      </div>

      <div v-else-if="trips.length === 0" class="h-full flex items-center justify-center">
        <p class="text-3xl text-gray-600">No trip history</p>
      </div>

      <div v-else id="trips-list" class="space-y-3">
        <div
          v-for="trip in trips"
          :key="trip.id"
          class="bg-white rounded-xl p-6 border-2 border-gray-200 shadow-sm"
        >
          <div class="flex justify-between items-start mb-2 gap-4">
            <div class="text-xl font-semibold text-gray-900 flex-1">
              {{ trip.from }} → {{ trip.to }}
            </div>
            <div class="text-2xl font-bold text-green-600 flex-shrink-0">
              ${{ trip.fare.toFixed(2) }}
            </div>
          </div>
          <div class="flex justify-between items-center text-lg text-gray-600">
            <div>{{ trip.date }} at {{ trip.time }}</div>
            <div class="text-sm uppercase font-semibold text-gray-500">{{ trip.status }}</div>
          </div>
        </div>
      </div>
    </div>

    <div id="back-button-wrapper" class="w-full mt-4">
      <KioskButton
        id="back-button"
        variant="secondary"
        size="small"
        full-width
        @click="handleBack"
      >
        Back
      </KioskButton>
    </div>
  </div>
</template>

<style scoped>
#history-content::-webkit-scrollbar {
  width: 20px;
}

#history-content::-webkit-scrollbar-track {
  background: #E5E7EB;
  border-radius: 10px;
}

#history-content::-webkit-scrollbar-thumb {
  background: #4B5563;
  border-radius: 10px;
  border: 3px solid #E5E7EB;
}

#history-content::-webkit-scrollbar-thumb:hover {
  background: #374151;
}
</style>