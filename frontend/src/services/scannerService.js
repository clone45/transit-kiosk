import { offlineApi as api } from '../api/offlineWrapper'
import { testConfig } from '../config/testConfig'
import { purchaseCardStore } from '../stores/purchaseCardStore'
import { addFareStore } from '../stores/addFareStore'
import { fareStore } from '../stores/fareStore'
import { navigationStore } from '../stores/navigationStore'
import { historyStore } from '../stores/historyStore'

class ScannerService {
  constructor() {
    this.errorTimeout = null
  }

  /**
   * Main entry point for scanner clicks
   * Routes to appropriate handler based on current route
   */
  async handleScan(context) {
    const { routeName, router, route, entryStationId, exitStationId } = context

    // Store station overrides for use in handlers
    this.entryStationId = entryStationId
    this.exitStationId = exitStationId

    // Route to the appropriate handler
    switch (routeName) {
      case 'history':
        return this.handleHistoryScan(router)

      case 'add-fare':
        return this.handleAddFareScan(router)

      case 'add-fare-payment':
        return this.handleAddFarePayment(router)

      case 'add-fare-complete':
        return this.handleAddFareComplete(router)

      case 'purchase-card-payment':
        return this.handlePurchaseCardPayment(router)

      case 'purchase-card-dispensing':
        return this.handlePurchaseCardDispensing(router)

      case 'scan-to-exit':
        return this.handleScanToExit(router, route)

      default:
        return this.handleDefaultScan(router, route)
    }
  }

  /**
   * Handle history view scanning
   */
  async handleHistoryScan(router) {
    const cardData = testConfig.scanCard()

    if (!cardData) {
      return {
        success: false,
        scannerState: 'error',
        errorMessage: 'No test card configured',
        isInsufficientBalance: false,
        timeout: 5000
      }
    }

    historyStore.setScannedCard({
      uuid: cardData.uuid,
      balance: cardData.balance
    })

    setTimeout(() => {
      router.push('/history/view')
    }, 500)

    return {
      success: true,
      scannerState: 'success'
    }
  }

  /**
   * Handle add fare initial scan
   */
  async handleAddFareScan(router) {
    const cardData = testConfig.scanCard()

    if (!cardData) {
      return {
        success: false,
        scannerState: 'error',
        errorMessage: 'No test card configured',
        isInsufficientBalance: false,
        timeout: 5000
      }
    }

    addFareStore.setScannedCard({
      uuid: cardData.uuid,
      balance: cardData.balance
    })

    setTimeout(() => {
      router.push('/add-fare/select-amount')
    }, 500)

    return {
      success: true,
      scannerState: 'success'
    }
  }

  /**
   * Handle add fare payment completion
   */
  async handleAddFarePayment(router) {
    const cardUuid = addFareStore.scannedCard.value?.uuid

    if (!cardUuid) {
      return {
        success: false,
        scannerState: 'error',
        errorMessage: 'No card selected',
        timeout: 5000
      }
    }

    const currentBalance = addFareStore.scannedCard.value.balance
    const amountToAdd = addFareStore.selectedAmount.value
    const newBalance = currentBalance + amountToAdd

    // Update local balance immediately
    testConfig.writeCardBalance(cardUuid, newBalance)
    addFareStore.setScannedCard({
      uuid: cardUuid,
      balance: newBalance
    })

    // Sync with backend asynchronously
    api.getCardByUuid(cardUuid).then(card => {
      api.addFunds(card.id, amountToAdd).catch(error => {
        console.error('Failed to add funds to DB:', error)
      })
    }).catch(error => {
      console.error('Card not found in DB:', error)
    })

    setTimeout(() => {
      router.push('/add-fare/complete')
    }, 500)

    return {
      success: true,
      scannerState: 'success'
    }
  }

  /**
   * Handle add fare completion
   */
  handleAddFareComplete(router) {
    addFareStore.reset()
    router.push('/')
    return {
      success: true,
      scannerState: 'success'
    }
  }

  /**
   * Handle purchase card payment
   */
  async handlePurchaseCardPayment(router) {
    const initialBalance = purchaseCardStore.selectedAmount.value
    const newCardUuid = `card-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

    // Create card locally
    testConfig.writeCardBalance(newCardUuid, initialBalance)
    purchaseCardStore.setCreatedCard({
      uuid: newCardUuid,
      balance: initialBalance
    })

    // Sync with backend asynchronously
    api.createCard(initialBalance, newCardUuid).catch(error => {
      console.error('Failed to create card in DB:', error)
    })

    setTimeout(() => {
      router.push('/purchase-card/dispensing')
    }, 500)

    return {
      success: true,
      scannerState: 'success'
    }
  }

  /**
   * Handle purchase card dispensing completion
   */
  handlePurchaseCardDispensing(router) {
    purchaseCardStore.reset()
    router.push('/')
    return {
      success: true,
      scannerState: 'success'
    }
  }

  /**
   * Handle scan to exit
   */
  async handleScanToExit(router, route) {
    const cardData = testConfig.scanCard()

    if (!cardData) {
      return {
        success: false,
        scannerState: 'error',
        errorMessage: 'No test card configured',
        isInsufficientBalance: false,
        timeout: 5000
      }
    }

    const tripData = testConfig.readCardTrip(cardData.uuid)

    // No active trip - just exit
    if (!tripData) {
      router.push('/exit')
      return {
        success: true,
        scannerState: 'success'
      }
    }

    const exitStationId = this.exitStationId || parseInt(import.meta.env.VITE_EXIT_STATION_ID)

    if (!exitStationId) {
      return {
        success: false,
        scannerState: 'error',
        errorMessage: 'No exit station ID configured',
        isInsufficientBalance: false,
        timeout: 5000
      }
    }

    // Calculate fare
    const fare = await fareStore.fetchFareBetweenStations(tripData.station_id, exitStationId)

    if (fare === null) {
      return {
        success: false,
        scannerState: 'error',
        errorMessage: 'Unable to calculate fare',
        isInsufficientBalance: false,
        timeout: 5000
      }
    }

    // Check balance
    if (cardData.balance < fare) {
      return {
        success: false,
        scannerState: 'error',
        errorMessage: `Insufficient balance\n\nFare: $${fare.toFixed(2)}\nBalance: $${cardData.balance.toFixed(2)}\nShort: $${(fare - cardData.balance).toFixed(2)}`,
        isInsufficientBalance: true,
        lastScannedCard: cardData,
        timeout: 5000
      }
    }

    // Process exit
    const newBalance = cardData.balance - fare
    testConfig.writeCardBalance(cardData.uuid, newBalance)
    testConfig.clearCardTrip(cardData.uuid)

    // Complete trip in backend asynchronously
    api.getCardByUuid(cardData.uuid).then(card => {
      if (card) {
        api.getActiveTrip(card.id).then(activeTrip => {
          if (activeTrip) {
            api.completeTrip(activeTrip.id, exitStationId, fare).catch(error => {
              console.error('Failed to complete trip in DB:', error)
            })
          }
        }).catch(error => {
          console.error('Failed to get active trip:', error)
        })
      }
    }).catch(error => {
      console.error('Failed to get card from DB:', error)
    })

    router.push('/exit')
    return {
      success: true,
      scannerState: 'success'
    }
  }

  /**
   * Handle default scan (entry)
   */
  async handleDefaultScan(router, route) {
    const cardData = testConfig.scanCard()

    if (!cardData) {
      return {
        success: false,
        scannerState: 'error',
        errorMessage: 'No test card configured',
        isInsufficientBalance: false,
        timeout: 5000
      }
    }

    const entryStationId = this.entryStationId || parseInt(import.meta.env.VITE_ENTRY_STATION_ID)

    if (!entryStationId) {
      return {
        success: false,
        scannerState: 'error',
        errorMessage: 'No entry station ID configured',
        isInsufficientBalance: false,
        timeout: 5000
      }
    }

    const minimumFare = fareStore.getMinimumFare()

    // Check minimum balance
    if (cardData.balance < minimumFare) {
      return {
        success: false,
        scannerState: 'error',
        errorMessage: 'Insufficient balance',
        isInsufficientBalance: true,
        lastScannedCard: cardData,
        timeout: 5000
      }
    }

    // Record entry
    const entryTimestamp = new Date().toISOString()
    testConfig.writeCardTrip(cardData.uuid, entryStationId, entryTimestamp)

    // Create trip in backend asynchronously
    api.createTrip(cardData.uuid, entryStationId).catch(error => {
      console.error('Failed to create trip in DB:', error)
    })

    router.push('/enter')
    return {
      success: true,
      scannerState: 'success'
    }
  }
}

export const scannerService = new ScannerService()