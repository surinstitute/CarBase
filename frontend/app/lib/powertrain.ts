export const POWERTRAIN_FILTERS = [
  { label: 'Combustión', value: 'combustion' },
  { label: 'Híbrido', value: 'hybrid' },
  { label: 'Híbrido enchufable', value: 'plug_in_hybrid' },
  { label: 'Eléctrico', value: 'electric' }
] as const

const architectureDetails = {
  ice: { label: 'Combustión interna', filter: 'combustion' },
  mild_hybrid: { label: 'Mild hybrid', filter: 'hybrid' },
  series_hybrid: { label: 'Híbrido serie', filter: 'hybrid' },
  parallel_hybrid: { label: 'Híbrido paralelo', filter: 'hybrid' },
  power_split_hybrid: { label: 'Híbrido combinado', filter: 'hybrid' },
  phev: { label: 'Híbrido enchufable', filter: 'plug_in_hybrid' },
  plug_in_hybrid: { label: 'Híbrido enchufable', filter: 'plug_in_hybrid' },
  battery_electric: { label: 'Eléctrico de batería', filter: 'electric' },
  fuel_cell_electric: { label: 'Pila de combustible', filter: 'electric' }
} as const

export type PowertrainFilter = typeof POWERTRAIN_FILTERS[number]['value']

export function powertrainArchitectureLabel(architecture: string) {
  return architectureDetails[architecture as keyof typeof architectureDetails]?.label
}

export function powertrainFilterForArchitecture(architecture: string) {
  const filter = architectureDetails[architecture as keyof typeof architectureDetails]?.filter
  return POWERTRAIN_FILTERS.find((item) => item.value === filter)
}

export function powertrainFilterLabel(filter: string) {
  return POWERTRAIN_FILTERS.find((item) => item.value === filter)?.label
}
