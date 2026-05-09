type Modalidade = 'simples' | 'duplas'

export function getDuplasRating(atributos?: Record<string, number> | null) {
  return Number(atributos?.duplas ?? 0)
}

export function isDoublesSpecialist(
  atributos?: Record<string, number> | null,
  modalidade?: Modalidade,
) {
  const duplas = getDuplasRating(atributos)
  return modalidade === 'duplas' || duplas >= 88
}

export function getOverallTierLabel(overall: number, ranking?: number | null, totalPlayers?: number | null) {
  if (ranking && ranking > 0) {
    if (ranking <= 10) return 'GALACTICO'
    if (ranking <= 25) return 'ICONICO'
    if (ranking <= 100) return 'ELITE TOUR'
    if (ranking <= 250) return 'MAIN DRAW'
    if (ranking <= 500) return 'CHALLENGER'
  }

  if (totalPlayers && ranking && ranking > 0) {
    const percentile = ranking / totalPlayers
    if (percentile <= 0.02) return 'ELITE TOUR'
    if (percentile <= 0.08) return 'MAIN DRAW'
    if (percentile <= 0.2) return 'CHALLENGER'
  }

  if (overall >= 90) return 'GALACTICO'
  if (overall >= 84) return 'ELITE TOUR'
  if (overall >= 78) return 'MAIN DRAW'
  if (overall >= 72) return 'CHALLENGER'
  return 'FUTURES'
}

export function getSpecialCardPalette(isSpecialist: boolean, tour: 'atp' | 'wta') {
  if (isSpecialist) {
    return {
      accent: '#f6c453',
      glow: '0 0 18px rgba(246, 196, 83, 0.28)',
      soft: 'rgba(246, 196, 83, 0.16)',
      label: 'DUPLAS PRO',
    }
  }

  if (tour === 'wta') {
    return {
      accent: '#ff4466',
      glow: '0 0 18px rgba(255, 68, 102, 0.24)',
      soft: 'rgba(255, 68, 102, 0.14)',
      label: 'WTA TOUR',
    }
  }

  return {
    accent: 'var(--neon-cyan)',
    glow: '0 0 18px rgba(0, 229, 255, 0.24)',
    soft: 'rgba(0, 229, 255, 0.14)',
    label: 'ATP TOUR',
  }
}
