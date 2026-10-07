import type { ClassValue } from "clsx"
import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function countryFlag(country: string | null | undefined) {
  const code = country?.trim().toUpperCase()
  if (!code || !/^[A-Z]{2}$/.test(code)) return ''

  return String.fromCodePoint(...[...code].map((letter) => 127397 + letter.charCodeAt(0)))
}

export function countryName(country: string | null | undefined) {
  const code = country?.trim().toUpperCase()
  if (!code || !/^[A-Z]{2}$/.test(code)) return ''

  return new Intl.DisplayNames('es-MX', { type: 'region' }).of(code) ?? code
}

export function formatNumber(value: number | string | null | undefined) {
  const number = typeof value === 'number' ? value : Number(value)
  if (!Number.isFinite(number)) return ''

  return new Intl.NumberFormat('es-MX', { maximumFractionDigits: 2 }).format(number)
}
