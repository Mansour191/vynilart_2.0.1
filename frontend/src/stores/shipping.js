/**
 * Shipping Store (Pinia)
 * This store manages shipping data and calculations
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useShippingStore = defineStore('shipping', () => {
  // State
  const wilayas = ref([])
  const isLoading = ref(false)
  const lastFetched = ref(null)
  const baseCity = ref(null)
  
  // Computed properties
  const activeWilayas = computed(() => {
    return wilayas.value.filter(wilaya => wilaya.isActive)
  })

  const wilayasByCode = computed(() => {
    const result = {}
    wilayas.value.forEach(wilaya => {
      result[wilaya.wilayaCode] = wilaya
    })
    return result
  })

  const wilayasById = computed(() => {
    const result = {}
    wilayas.value.forEach(wilaya => {
      result[wilaya.wilayaId] = wilaya
    })
    return result
  })

  const northernWilayas = computed(() => {
    // Northern Algeria (codes 1-18)
    return wilayas.value.filter(wilaya => wilaya.wilayaCode >= 1 && wilaya.wilayaCode <= 18)
  })

  const southernWilayas = computed(() => {
    // Southern Algeria (codes 19-58)
    return wilayas.value.filter(wilaya => wilaya.wilayaCode >= 19 && wilaya.wilayaCode <= 58)
  })

  const averageHomeDeliveryPrice = computed(() => {
    const active = activeWilayas.value
    if (active.length === 0) return 0
    const total = active.reduce((sum, wilaya) => sum + parseFloat(wilaya.homeDeliveryPrice), 0)
    return total / active.length
  })

  const averageStopDeskPrice = computed(() => {
    const active = activeWilayas.value
    if (active.length === 0) return 0
    const total = active.reduce((sum, wilaya) => sum + parseFloat(wilaya.stopDeskPrice), 0)
    return total / active.length
  })

  // Actions
  async function fetchWilayas() {
    if (isLoading.value) return

    isLoading.value = true

    try {
      const response = await fetch('/api/shipping/wilayas/', {
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        wilayas.value = data.results || data
        lastFetched.value = Date.now()
        saveToStorage()
      }
    } catch (error) {
      console.error('Error fetching wilayas:', error)
      // Fallback to localStorage
      loadFromStorage()
    } finally {
      isLoading.value = false
    }
  }

  async function fetchWilaya(wilayaId) {
    try {
      const response = await fetch(`/api/shipping/wilayas/${wilayaId}/`, {
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const wilaya = await response.json()
        
        // Update in local array
        const index = wilayas.value.findIndex(w => w.wilayaId === wilayaId)
        if (index !== -1) {
          wilayas.value[index] = wilaya
          saveToStorage()
        }
        
        return wilaya
      }
    } catch (error) {
      console.error('Error fetching wilaya:', error)
      return null
    }
  }

  async function fetchShippingMethods() {
    if (isLoading.value) return

    isLoading.value = true

    try {
      const response = await fetch('/api/shipping/methods/', {
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        shippingMethods.value = data.results || data
        lastFetched.value = Date.now()
        saveToStorage()
      }
    } catch (error) {
      console.error('Error fetching shipping methods:', error)
      // Fallback to localStorage
      loadFromStorage()
    } finally {
      isLoading.value = false
    }
  }

  async function fetchShippingPrices(wilayaId) {
    try {
      const response = await fetch(`/api/shipping/prices/?wilaya_id=${wilayaId}`, {
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        return data.results || data
      }
    } catch (error) {
      console.error('Error fetching shipping prices:', error)
      return []
    }
  }

  async function updateShippingPrices(wilayaId, updates) {
    try {
      const response = await fetch(`/api/shipping/prices/${wilayaId}/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates)
      })

      if (response.ok) {
        const updatedPrice = await response.json()
        
        // Update in local array
        const index = shippingPrices.value.findIndex(p => p.wilaya_id === wilayaId)
        if (index !== -1) {
          shippingPrices.value[index] = updatedPrice
          saveToStorage()
        }
        
        return updatedPrice
      }
    } catch (error) {
      console.error('Error updating shipping prices:', error)
      return null
    }
  }

  async function bulkUpdatePrices(wilayaIds, updates) {
    try {
      const response = await fetch('/api/shipping/prices/bulk-update/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          wilaya_ids: wilayaIds,
          updates: updates
        })
      })

      if (response.ok) {
        const result = await response.json()
        
        // Update local array
        result.updated_prices.forEach(updatedPrice => {
          const index = shippingPrices.value.findIndex(p => p.wilaya_id === updatedPrice.wilaya_id)
          if (index !== -1) {
            shippingPrices.value[index] = updatedPrice
          }
        })
        
        saveToStorage()
        return result
      }
    } catch (error) {
      console.error('Error bulk updating shipping prices:', error)
      return null
    }
  }

  function getWilayaByCode(code) {
    return wilayasByCode.value[code] || null
  }

  function getWilayaById(id) {
    return wilayasById.value[id] || null
  }

  function calculateShippingCost(wilayaId, serviceType = 'home', methodId = null, orderWeight = null, orderVolume = null) {
    const wilaya = getWilayaById(wilayaId)
    if (!wilaya || !wilaya.is_active) return 0

    // Get available shipping prices for this wilaya
    const availablePrices = shippingPrices.value.filter(price => 
      price.wilaya_id === wilayaId && 
      price.is_active && 
      price.shipping_method.is_active
    )

    if (methodId) {
      // Use specific method
      const methodPrice = availablePrices.find(p => p.shipping_method_id === methodId)
      if (!methodPrice) return 0

      let basePrice = 0
      if (serviceType === 'home') {
        basePrice = parseFloat(methodPrice.home_delivery_price)
      } else if (serviceType === 'desk') {
        basePrice = parseFloat(methodPrice.stop_desk_price)
      } else if (serviceType === 'express' && methodPrice.express_price) {
        basePrice = parseFloat(methodPrice.express_price)
      }

      // Add surcharges
      let additionalCost = 0
      if (orderWeight && orderWeight > 10) {
        additionalCost += (orderWeight - 10) * parseFloat(methodPrice.weight_surcharge || 0)
      }
      
      if (orderVolume && orderVolume > 0.1) {
        additionalCost += (orderVolume - 0.1) * parseFloat(methodPrice.volume_surcharge || 0)
      }

      return basePrice + additionalCost
    }

    // Find best price for service type
    let bestPrice = 0
    let bestMethod = null

    for (const methodPrice of availablePrices) {
      let currentPrice = 0
      
      if (serviceType === 'home') {
        currentPrice = parseFloat(methodPrice.home_delivery_price)
      } else if (serviceType === 'desk') {
        currentPrice = parseFloat(methodPrice.stop_desk_price)
      } else if (serviceType === 'express' && methodPrice.express_price) {
        currentPrice = parseFloat(methodPrice.express_price)
      }

      // Add surcharges
      let additionalCost = 0
      if (orderWeight && orderWeight > 10) {
        additionalCost += (orderWeight - 10) * parseFloat(methodPrice.weight_surcharge || 0)
      }
      
      if (orderVolume && orderVolume > 0.1) {
        additionalCost += (orderVolume - 0.1) * parseFloat(methodPrice.volume_surcharge || 0)
      }

      currentPrice += additionalCost

      if (bestPrice === 0 || currentPrice < bestPrice) {
        bestPrice = currentPrice
        bestMethod = methodPrice.shipping_method
      }
    }

    return bestPrice
  }

  function calculateDeliveryTime(wilayaId, serviceType = 'home', methodId = null) {
    const wilaya = getWilayaById(wilayaId)
    if (!wilaya || !wilaya.is_active) return null

    // Get available shipping prices for this wilaya
    const availablePrices = shippingPrices.value.filter(price => 
      price.wilaya_id === wilayaId && 
      price.is_active && 
      price.shipping_method.is_active
    )

    if (methodId) {
      // Use specific method
      const methodPrice = availablePrices.find(p => p.shipping_method_id === methodId)
      if (methodPrice) {
        return methodPrice.shipping_method.expected_delivery_time
      }
      return null
    }

    // Find fastest delivery for service type
    let fastestTime = null
    for (const methodPrice of availablePrices) {
      const currentTime = methodPrice.shipping_method.expected_delivery_time
      
      if (serviceType === 'express' && methodPrice.shipping_method.service_type === 'express') {
        fastestTime = Math.min(fastestTime || currentTime, currentTime)
      } else if (serviceType === 'desk' && methodPrice.shipping_method.service_type === 'desk') {
        fastestTime = Math.min(fastestTime || currentTime, currentTime)
      } else if (serviceType === 'home') {
        fastestTime = Math.min(fastestTime || currentTime, currentTime)
      }
    }

    return fastestTime
  }

  function isFreeShippingEligible(wilayaId, orderTotal, methodId = null) {
    const availablePrices = shippingPrices.value.filter(price => 
      price.wilaya_id === wilayaId && 
      price.is_active && 
      price.shipping_method.is_active &&
      price.free_shipping_minimum
    )

    if (methodId) {
      // Check specific method
      const methodPrice = availablePrices.find(p => p.shipping_method_id === methodId)
      if (methodPrice) {
        return orderTotal >= parseFloat(methodPrice.free_shipping_minimum)
      }
      return false
    }

    // Check any method
    return availablePrices.some(price => 
      orderTotal >= parseFloat(price.free_shipping_minimum)
    )
  }

  function getAvailableShippingMethods(wilayaId) {
    const availablePrices = shippingPrices.value.filter(price => 
      price.wilaya_id === wilayaId && 
      price.is_active && 
      price.shipping_method.is_active
    )

    return availablePrices.map(price => ({
      ...price.shipping_method,
      prices: {
        home: parseFloat(price.home_delivery_price),
        desk: parseFloat(price.stop_desk_price),
        express: price.express_price ? parseFloat(price.express_price) : null
      },
      free_shipping_minimum: price.free_shipping_minimum ? parseFloat(price.free_shipping_minimum) : null,
      cod_available: price.cod_available,
      insurance_available: price.insurance_available,
      tracking_available: price.tracking_available
    }))
  }

  function getWilayasByRegion(region) {
    return wilayas.value.filter(wilaya => 
      wilaya.regions && wilaya.regions.includes(region)
    )
  }

  function searchWilayas(query) {
    if (!query) return wilayas.value

    const searchTerm = query.toLowerCase()
    return wilayas.value.filter(wilaya => 
      wilaya.nameAr.toLowerCase().includes(searchTerm) ||
      wilaya.nameEn.toLowerCase().includes(searchTerm) ||
      wilaya.wilayaId.toString().includes(searchTerm) ||
      wilaya.wilayaCode.toString().includes(searchTerm)
    )
  }

  function setBaseCity(city) {
    baseCity.value = city
    saveToStorage()
  }

  function saveToStorage() {
    try {
      const data = {
        wilayas: wilayas.value,
        shippingPrices: shippingPrices.value,
        shippingMethods: shippingMethods.value,
        lastFetched: lastFetched.value,
        baseCity: baseCity.value
      }
      localStorage.setItem('shipping_store', JSON.stringify(data))
    } catch (error) {
      console.error('Error saving shipping data to storage:', error)
    }
  }

  function loadFromStorage() {
    try {
      const stored = localStorage.getItem('shipping_store')
      if (stored) {
        const data = JSON.parse(stored)
        wilayas.value = data.wilayas || []
        lastFetched.value = data.lastFetched || null
        baseCity.value = data.baseCity || null
      }
    } catch (error) {
      console.error('Error loading shipping data from storage:', error)
    }
  }

  function getAuthToken() {
    return localStorage.getItem('auth_token') || ''
  }

  function initialize() {
    loadFromStorage()
    
    // Fetch fresh data if needed (older than 1 hour)
    if (!lastFetched.value || Date.now() - lastFetched.value > 3600000) {
      fetchWilayas()
    }
  }

  function cleanup() {
    saveToStorage()
  }

  return {
    // State
    wilayas,
    isLoading,
    lastFetched,
    baseCity,
    
    // Computed
    activeWilayas,
    wilayasByCode,
    wilayasById,
    northernWilayas,
    southernWilayas,
    averageHomeDeliveryPrice,
    averageStopDeskPrice,
    
    // Actions
    fetchWilayas,
    fetchWilaya,
    updateShippingPrices,
    bulkUpdatePrices,
    getWilayaByCode,
    getWilayaById,
    calculateShippingCost,
    calculateDeliveryTime,
    isFreeShippingEligible,
    getDistanceFromBase,
    getWilayasByRegion,
    searchWilayas,
    setBaseCity,
    initialize,
    cleanup
  }
})
