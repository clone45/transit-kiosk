class FailedOpsWriter {
  constructor() {
    this.failedOps = []
  }

  async writeFailedOperation(operation) {
    const failedOp = {
      id: `failed_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
      kioskId: this.getKioskId(),
      operation: operation,
      error: 'Network unavailable'
    }

    console.warn('[FailedOpsWriter] Writing failed operation:', {
      id: failedOp.id,
      type: operation.type,
      timestamp: failedOp.timestamp
    })

    // Add to memory
    this.failedOps.push(failedOp)

    // Store in localStorage as backup
    this.saveToLocalStorage()

    // Export to file immediately
    this.exportToFile([failedOp])

    return failedOp.id
  }

  saveToLocalStorage() {
    try {
      const existing = JSON.parse(localStorage.getItem('failed_operations') || '[]')
      existing.push(...this.failedOps)

      // Keep only last 100 operations to prevent storage overflow
      const trimmed = existing.slice(-100)
      localStorage.setItem('failed_operations', JSON.stringify(trimmed))

      console.log(`[FailedOpsWriter] Saved ${this.failedOps.length} operations to localStorage (${trimmed.length} total)`)
    } catch (error) {
      console.error('[FailedOpsWriter] Failed to save to localStorage:', error)
    }
  }

  exportToFile(operations = null) {
    const opsToExport = operations || this.failedOps

    if (opsToExport.length === 0) {
      console.log('[FailedOpsWriter] No operations to export')
      return
    }

    const content = JSON.stringify({
      exportTime: new Date().toISOString(),
      kioskId: this.getKioskId(),
      operationCount: opsToExport.length,
      operations: opsToExport
    }, null, 2)

    // Create filename with timestamp
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const filename = `failed_ops_${timestamp}.json`

    try {
      // Auto-download to Downloads folder
      const blob = new Blob([content], { type: 'application/json' })
      const url = URL.createObjectURL(blob)

      const a = document.createElement('a')
      a.href = url
      a.download = filename
      a.style.display = 'none'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)

      URL.revokeObjectURL(url)

      console.log(`[FailedOpsWriter] Exported ${opsToExport.length} operations to ${filename}`)

      // Clear exported operations from memory if we exported everything
      if (!operations) {
        this.failedOps = []
      }
    } catch (error) {
      console.error('[FailedOpsWriter] Failed to export to file:', error)
    }
  }

  getKioskId() {
    // Get or generate a unique kiosk ID
    let kioskId = localStorage.getItem('kiosk_id')
    if (!kioskId) {
      kioskId = `kiosk_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      localStorage.setItem('kiosk_id', kioskId)
      console.log('[FailedOpsWriter] Generated new kiosk ID:', kioskId)
    }
    return kioskId
  }

  // Method to export all operations from localStorage (for manual recovery)
  exportAllFromStorage() {
    try {
      const allOps = JSON.parse(localStorage.getItem('failed_operations') || '[]')

      if (allOps.length === 0) {
        console.log('[FailedOpsWriter] No operations in localStorage to export')
        return false
      }

      this.exportToFile(allOps)
      return true
    } catch (error) {
      console.error('[FailedOpsWriter] Failed to export from localStorage:', error)
      return false
    }
  }

  // Method to clear all operations from localStorage (after manual processing)
  clearStorage() {
    try {
      localStorage.removeItem('failed_operations')
      console.log('[FailedOpsWriter] Cleared all operations from localStorage')
      return true
    } catch (error) {
      console.error('[FailedOpsWriter] Failed to clear localStorage:', error)
      return false
    }
  }

  // Get count of pending operations
  getPendingCount() {
    try {
      const existing = JSON.parse(localStorage.getItem('failed_operations') || '[]')
      return existing.length
    } catch (error) {
      console.error('[FailedOpsWriter] Failed to get pending count:', error)
      return 0
    }
  }
}

export const failedOpsWriter = new FailedOpsWriter()