export const testConfig = {
  getTestCardUuid: () => {
    return import.meta.env.VITE_TEST_CARD_UUID || null
  },

  scanCard: () => {
    const uuid = import.meta.env.VITE_TEST_CARD_UUID
    if (!uuid) return null

    const storedBalance = localStorage.getItem(`card_balance_${uuid}`)
    let balance

    if (storedBalance) {
      balance = parseFloat(storedBalance)
    } else {
      balance = 25.00
      localStorage.setItem(`card_balance_${uuid}`, balance.toString())
    }

    return {
      uuid: uuid,
      balance: balance
    }
  },

  writeCardBalance: (uuid, newBalance) => {
    localStorage.setItem(`card_balance_${uuid}`, newBalance.toString())
  },

  writeCardTrip: (uuid, stationId, timestamp) => {
    const tripData = {
      station_id: stationId,
      timestamp: timestamp
    }
    localStorage.setItem(`card_trip_${uuid}`, JSON.stringify(tripData))
  },

  readCardTrip: (uuid) => {
    const tripData = localStorage.getItem(`card_trip_${uuid}`)
    if (!tripData) return null
    return JSON.parse(tripData)
  },

  clearCardTrip: (uuid) => {
    localStorage.removeItem(`card_trip_${uuid}`)
  }
}