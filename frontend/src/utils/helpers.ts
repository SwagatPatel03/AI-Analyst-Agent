/**
 * Helper utility functions
 */

export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount)
}

export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('en-US').format(num)
}

export const formatPercentage = (value: number): string => {
  return `${value.toFixed(2)}%`
}

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

export const downloadFile = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)
}

export const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    uploaded: 'text-blue-600 bg-blue-100',
    processing: 'text-yellow-600 bg-yellow-100',
    completed: 'text-green-600 bg-green-100',
    failed: 'text-red-600 bg-red-100',
    pending: 'text-gray-600 bg-gray-100',
  }
  return colors[status] || 'text-gray-600 bg-gray-100'
}

/**
 * Extract a human-friendly message from unknown errors (Axios, Fetch, plain Error, string).
 */
export function getErrorMessage(err: unknown): string {
  // String thrown
  if (typeof err === 'string') return err

  // Standard Error
  if (err instanceof Error) return err.message

  // Axios-style error shape without importing axios types
  if (typeof err === 'object' && err !== null) {
    const anyErr = err as {
      response?: { data?: { detail?: string; message?: string }; status?: number }
      message?: string
    }
    const detail = anyErr.response?.data?.detail || anyErr.response?.data?.message
    if (detail) return detail
    if (anyErr.message) return anyErr.message
  }

  return 'Unexpected error occurred.'
}
