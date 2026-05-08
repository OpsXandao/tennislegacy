import type { TierVisual } from './types'

export const TOTAL_WEEKS = 52

export const surfaceColors = {
  hard: '#1e3a8a',
  clay: '#991b1b',
  grass: '#166534',
} as const

export function toTier(tipo: string): TierVisual {
  const normalized = tipo.toLowerCase()
  if (normalized.includes('grand slam')) return 'grandslam'
  if (normalized.includes('1000')) return 'masters'
  if (normalized.includes('500')) return 'atp500'
  return 'atp250'
}

export function normalizeSurface(surface: string): keyof typeof surfaceColors {
  const normalized = surface.toLowerCase()
  if (normalized.includes('saibro')) return 'clay'
  if (normalized.includes('grama')) return 'grass'
  return 'hard'
}

export function tierConfig(tier: TierVisual) {
  if (tier === 'grandslam') {
    return { color: '#ffe600', glow: '0 0 12px rgba(255,230,0,0.45)', label: 'GRAND SLAM', badge: '👑' }
  }
  if (tier === 'masters') {
    return { color: '#00ff88', glow: '0 0 12px rgba(0,255,136,0.35)', label: 'MASTERS 1000', badge: '⭐' }
  }
  if (tier === 'atp500') {
    return { color: '#00e5ff', glow: '0 0 12px rgba(0,229,255,0.35)', label: 'ATP / WTA 500', badge: '⚡' }
  }
  return { color: '#ff7b00', glow: '0 0 12px rgba(255,123,0,0.35)', label: 'ATP / WTA 250', badge: '🎾' }
}

export function surfaceTexture(surface: keyof typeof surfaceColors) {
  if (surface === 'clay') {
    return 'repeating-linear-gradient(45deg, #7f1d1d 0px, #7f1d1d 2px, #991b1b 2px, #991b1b 4px)'
  }
  if (surface === 'grass') {
    return 'repeating-linear-gradient(0deg, #14532d 0px, #14532d 1px, #166534 1px, #166534 2px)'
  }
  return 'repeating-conic-gradient(#1e3a8a 0% 25%, #172554 0% 50%)'
}
