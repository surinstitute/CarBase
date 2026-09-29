import type { CatalogModel, CatalogVehicleRecord } from '#shared/types/catalog'

export const CAR_COMPARISON_LIMIT = 4

export interface ComparisonVehicle {
  id: string
  modelId: string
  makeId: string
  makeName: string
  modelName: string
  variantName: string | null
  year: number
  image?: CatalogModel['image']
  vehicle: CatalogVehicleRecord
}

type ComparisonModel = Pick<CatalogModel, 'id' | 'makeId' | 'makeName' | 'modelName' | 'image'>

function isComparisonVehicle(value: unknown): value is ComparisonVehicle {
  if (!value || typeof value !== 'object') return false
  const selected = value as Partial<ComparisonVehicle>
  return typeof selected.id === 'string'
    && typeof selected.modelId === 'string'
    && typeof selected.makeName === 'string'
    && typeof selected.modelName === 'string'
    && typeof selected.year === 'number'
    && typeof selected.vehicle === 'object'
}

export function useCarComparison() {
  const selectedVehicles = useState<ComparisonVehicle[]>('car-comparison-vehicles', () => [])
  const isLoaded = useState('car-comparison-loaded', () => false)

  if (import.meta.client) {
    if (!isLoaded.value) {
      onMounted(() => {
        try {
          const stored = JSON.parse(localStorage.getItem('car-comparison-vehicles') ?? '[]')
          if (Array.isArray(stored)) {
            selectedVehicles.value = stored.filter(isComparisonVehicle).slice(0, CAR_COMPARISON_LIMIT)
          }
        } catch {
          selectedVehicles.value = []
        }
        isLoaded.value = true
      })
    }

    watch(selectedVehicles, (vehicles) => {
      if (isLoaded.value) {
        localStorage.setItem('car-comparison-vehicles', JSON.stringify(vehicles))
      }
    }, { deep: true })
  }

  function toggle(model: ComparisonModel, vehicle: CatalogVehicleRecord) {
    const vehicleId = String(vehicle.id)
    const existingIndex = selectedVehicles.value.findIndex((selected) => selected.id === vehicleId)
    if (existingIndex !== -1) {
      selectedVehicles.value = selectedVehicles.value.filter((selected) => selected.id !== vehicleId)
      return
    }
    if (selectedVehicles.value.length >= CAR_COMPARISON_LIMIT) return

    const variantImage = vehicle.images?.leftSide ?? vehicle.images?.silhouette ?? vehicle.images?.front
    selectedVehicles.value = [...selectedVehicles.value, {
      id: vehicleId,
      modelId: model.id,
      makeId: model.makeId,
      makeName: model.makeName,
      modelName: model.modelName,
      variantName: vehicle.variantName ?? null,
      year: vehicle.lineage.modelYear,
      image: variantImage ?? model.image,
      vehicle: { ...vehicle, id: vehicleId }
    }]
  }

  function remove(vehicleId: string) {
    selectedVehicles.value = selectedVehicles.value.filter((vehicle) => vehicle.id !== vehicleId)
  }

  function clear() {
    selectedVehicles.value = []
  }

  return {
    selectedVehicles,
    count: computed(() => selectedVehicles.value.length),
    canCompare: computed(() => selectedVehicles.value.length >= 2),
    isAtLimit: computed(() => selectedVehicles.value.length >= CAR_COMPARISON_LIMIT),
    toggle,
    remove,
    clear
  }
}