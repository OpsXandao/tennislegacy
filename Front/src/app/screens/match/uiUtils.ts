import type { Surface } from './types'

export function getMatchThemeClass(surface: Surface): string {
  if (surface === 'hard') return 'match-theme-hard'
  if (surface === 'grass') return 'match-theme-grass'
  if (surface === 'clay') return 'match-theme-clay'
  return 'match-theme-default'
}

export function normSurface(s?: string): Surface {
  const v = String(s ?? '').toLowerCase()
  if (v.includes('saibro') || v.includes('clay')) return 'clay'
  if (v.includes('grama') || v.includes('grass')) return 'grass'
  return 'hard'
}

export function flashColor(desc: string): string {
  const d = desc.toLowerCase()
  if (d.includes('ace')) return 'var(--neon-green)'
  if (d.includes('winner')) return 'var(--neon-yellow)'
  if (d.includes('break')) return '#ff9900'
  if (d.includes('erro') || d.includes('falta dupla')) return 'var(--neon-pink)'
  return 'var(--neon-cyan)'
}

export function accentFromCarta(carta?: { raridade?: string; tipo?: string; cor_primaria?: string | null }, fallback = '#ff4466'): string {
  if (!carta) return fallback
  const raridade = String(carta.raridade ?? '').toLowerCase()
  const tipo = String(carta.tipo ?? '').toLowerCase()
  const cor = String(carta.cor_primaria ?? '').trim()

  if ((raridade === 'special' || raridade === 'iconic' || tipo === 'lenda' || tipo === 'iconic') && cor) return cor
  if (raridade === 'gold') return '#FFD700'
  if (raridade === 'silver') return '#C0C0C0'
  if (raridade === 'bronze') return '#CD7F32'
  return cor || fallback
}

export function alpha(hex: string, opacity: string): string {
  const percent = Math.round((parseInt(opacity, 16) / 255) * 100)
  if (!hex.startsWith('#')) return `color-mix(in srgb, ${hex} ${percent}%, transparent)`
  const normalized = hex.length === 4
    ? `#${hex[1]}${hex[1]}${hex[2]}${hex[2]}${hex[3]}${hex[3]}`
    : hex
  return `${normalized}${opacity}`
}

export function leituraFisica(energia: number, fadiga: number): string {
  if (energia <= 45) return 'Estado físico comprometido.'
  if (fadiga >= 25) return 'Há desgaste acumulado importante.'
  if (energia >= 80 && fadiga <= 10) return 'Chega inteiro para a partida.'
  return 'Condição estável, mas exige gestão.'
}

export function rankingValido(valor: unknown): number | null {
  const numero = Number(valor)
  if (!Number.isFinite(numero) || numero <= 0) return null
  return Math.round(numero)
}

export function formatarNacionalidade(valor?: string | null): string {
  const texto = String(valor ?? '').trim()
  if (!texto) return 'Nacionalidade não informada'
  return texto
}

export function getContextoArena(tipoTorneio?: string): { estadio: string; energia: string; icon: string } {
  const t = String(tipoTorneio ?? '').toLowerCase()
  if (t.includes('grand slam')) return { estadio: 'QUADRA CENTRAL (LOTADA)', energia: 'ELETRIZANTE', icon: '🏟️' }
  if (t.includes('1000')) return { estadio: 'STADIUM 1 (LOTADO)', energia: 'ALTA', icon: '🏟️' }
  if (t.includes('500') || t.includes('250')) return { estadio: 'QUADRA PRINCIPAL', energia: 'ANIMADA', icon: '🏛️' }
  if (t.includes('challenger')) return { estadio: 'QUADRA 2', energia: 'MODERADA', icon: '🏢' }
  return { estadio: 'QUADRA SECUNDÁRIA', energia: 'LOCAL', icon: '📍' }
}
