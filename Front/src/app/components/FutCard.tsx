import { motion } from 'motion/react'
import { PixelFlag } from './PixelFlag'
import { useTheme } from '../hooks/useTheme'
import { getDuplasRating, getOverallTierLabel, getSpecialCardPalette, isDoublesSpecialist } from '../utils/playerRatings'

const STAT_KEYS = [
  { key: 'saque',        label: 'SAQ' },
  { key: 'retorno',      label: 'RET' },
  { key: 'forca',        label: 'FOR' },
  { key: 'velocidade',   label: 'VEL' },
  { key: 'mental',       label: 'MEN' },
  { key: 'consistencia', label: 'CON' },
]

function avg(...values: Array<number | undefined>) {
  const valid = values.filter((value): value is number => typeof value === 'number')
  if (valid.length === 0) return undefined
  return Math.round(valid.reduce((acc, value) => acc + value, 0) / valid.length)
}

function calcularOverallCard(
  atributos: Record<string, number>,
  atributosPsicologicos: Record<string, number>,
): number {
  const stats = STAT_KEYS
    .map(({ key }) => resolveStat(key, atributos, atributosPsicologicos))
    .filter((value): value is number => typeof value === 'number')

  if (stats.length === 0) return 60
  return Math.round(stats.reduce((acc, value) => acc + value, 0) / stats.length)
}

function resolveStat(
  key: string,
  atributos: Record<string, number>,
  atributosPsicologicos: Record<string, number>,
) {
  const direct = atributos[key]
  if (typeof direct === 'number') return direct

  switch (key) {
    case 'retorno':
      return avg(atributos.retorno, atributos.backhand, atributos.forehand)
    case 'forca':
      return avg(atributos.forca, atributos.fisico, atributos.winner)
    case 'velocidade':
      return avg(atributos.velocidade, atributos.movimento, atributos.fisico)
    case 'mental':
      return avg(
        atributos.mental,
        atributos.consistencia,
        atributos.winner,
        atributos.backhand,
        atributos.forehand,
        atributosPsicologicos.concentracao,
        atributosPsicologicos.determinacao,
      )
    case 'consistencia':
      return avg(
        atributos.consistencia,
        atributos.backhand,
        atributosPsicologicos.leitura_de_jogo,
      )
    default:
      return undefined
  }
}

function ovrColorVar(ovr: number) {
  if (ovr >= 90) return 'var(--neon-yellow)'
  if (ovr >= 80) return 'var(--neon-green)'
  if (ovr >= 70) return 'var(--neon-cyan)'
  return 'var(--text-secondary)'
}

/** Returns a card background gradient based on raridade/tipo */
function getCardBackground(
  cartaRaridade?: string,
  cartaTipo?: string,
  cartaCor?: string,
  specialDuplas?: boolean,
  specialPalette?: { soft: string },
): string | undefined {
  if (cartaRaridade === 'special' && cartaCor) {
    // special cards (IF, GS, WK, DS): use the card's primary color as gradient base
    return `linear-gradient(135deg, #0a0a0a 0%, ${cartaCor}22 40%, #0a0a0a 100%)`
  }
  if (cartaRaridade === 'iconic' || cartaTipo === 'lenda' || cartaTipo === 'iconic') {
    return 'linear-gradient(135deg, #1a0e00 0%, #4a3200 40%, #1a0e00 100%)'
  }
  if (cartaRaridade === 'gold') {
    return 'linear-gradient(135deg, #2a1f00 0%, #5a4200 40%, #2a1f00 100%)'
  }
  if (cartaRaridade === 'silver') {
    return 'linear-gradient(135deg, #1a1a2e 0%, #4a4a6a 40%, #1a1a2e 100%)'
  }
  if (cartaRaridade === 'bronze') {
    return 'linear-gradient(135deg, #3d1c0a 0%, #7a3e18 40%, #3d1c0a 100%)'
  }
  // fallback: duplas specialist
  if (specialDuplas && specialPalette) {
    return `linear-gradient(180deg, ${specialPalette.soft} 0%, rgba(8,12,18,0.96) 48%, rgba(8,12,18,1) 100%)`
  }
  return undefined
}

/** Returns border color based on carta or fallback accent */
function getBorderColor(
  cartaRaridade?: string,
  cartaCor?: string,
  accentVar?: string,
): string {
  if ((cartaRaridade === 'special' || cartaRaridade === 'iconic') && cartaCor) {
    return cartaCor
  }
  if (cartaRaridade === 'gold') return '#FFD700'
  if (cartaRaridade === 'silver') return '#C0C0C0'
  if (cartaRaridade === 'bronze') return '#CD7F32'
  return accentVar ?? 'var(--neon-cyan)'
}

function getCartaBadgeLabel(cartaTipo?: string, cartaRaridade?: string): string | null {
  const tipo = String(cartaTipo ?? '').trim().toLowerCase()
  const raridade = String(cartaRaridade ?? '').trim().toLowerCase()

  if (tipo && !['gold', 'silver', 'bronze'].includes(tipo)) {
    if (tipo === 'iconic' || tipo === 'lenda') return 'ICON'
    return tipo.toUpperCase()
  }

  if (raridade === 'iconic') return 'ICON'
  if (raridade === 'special') return 'SPECIAL'
  if (raridade === 'gold') return 'GOLD'
  if (raridade === 'silver') return 'SILVER'
  if (raridade === 'bronze') return 'BRONZE'

  if (tipo === 'gold') return 'GOLD'
  if (tipo === 'silver') return 'SILVER'
  if (tipo === 'bronze') return 'BRONZE'

  return null
}

function getBaseCardRaridade(overall: number, ranking: number): 'gold' | 'silver' | 'bronze' {
  if ((ranking > 0 && ranking <= 100) || overall >= 84) return 'gold'
  if ((ranking > 0 && ranking <= 500) || overall >= 72) return 'silver'
  return 'bronze'
}

interface FutCardProps {
  nome: string
  nacionalidade?: string
  overall: number
  tour: 'atp' | 'wta'
  ranking: number
  modalidade?: 'simples' | 'duplas'
  nivel?: number
  atributos?: Record<string, number>
  atributosPsicologicos?: Record<string, number>
  cartaTipo?: string
  cartaRaridade?: string
  cartaCor?: string
  overallBoosted?: number
  atributosBoosted?: Record<string, number>
}

export function FutCard({
  nome,
  nacionalidade,
  overall,
  tour,
  ranking,
  modalidade = 'simples',
  nivel = 1,
  atributos = {},
  atributosPsicologicos = {},
  cartaTipo,
  cartaRaridade,
  cartaCor,
  overallBoosted,
  atributosBoosted,
}: FutCardProps) {
  const { isLight } = useTheme()
  const specialDuplas = isDoublesSpecialist(atributos, modalidade)
  const palette = getSpecialCardPalette(specialDuplas, tour)
  const duplas = getDuplasRating(atributos)
  const tier = getOverallTierLabel(overall, ranking)
  const resolvedBaseRaridade = getBaseCardRaridade(overall, ranking)
  const resolvedCartaTipo = cartaTipo ?? resolvedBaseRaridade
  const resolvedCartaRaridade = cartaRaridade ?? resolvedBaseRaridade
  const resolvedCartaCor = cartaCor
    ?? (resolvedCartaRaridade === 'gold'
      ? '#FFD700'
      : resolvedCartaRaridade === 'silver'
        ? '#C0C0C0'
        : '#CD7F32')

  // Effective atributos for stat display (boosted if special card)
  const effectiveAtributos = atributosBoosted ?? atributos
  // OVR visual do card segue a média dos stats exibidos
  const displayOvr = calcularOverallCard(effectiveAtributos, atributosPsicologicos)
  const boostDiff = overallBoosted ? Math.max(0, overallBoosted - overall) : 0

  // Card border + accent
  const borderColor = getBorderColor(resolvedCartaRaridade, resolvedCartaCor, palette.accent)
  const accentVar = borderColor
  const cartaBadge = getCartaBadgeLabel(resolvedCartaTipo, resolvedCartaRaridade)

  const colorVar = ovrColorVar(displayOvr)

  // Card background
  const cardBg = getCardBackground(
    resolvedCartaRaridade,
    resolvedCartaTipo,
    resolvedCartaCor,
    specialDuplas,
    palette,
  )

  // Glow effect
  const glowColor = resolvedCartaCor
    ? `0 0 0 1px var(--bg-dark), 0 0 20px ${resolvedCartaCor}44, inset 0 0 40px rgba(0,0,0,0.8)`
    : `0 0 0 1px var(--bg-dark), ${palette.glow}, inset 0 0 40px rgba(0,0,0,0.8)`

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="app-panel relative w-full border-2"
      style={{
        borderColor: accentVar,
        boxShadow: isLight ? 'var(--panel-shadow)' : glowColor,
        background: cardBg,
      }}
    >
      {/* scanline overlay — apenas no modo escuro */}
      {!isLight && (
        <div
          className="absolute inset-0 pointer-events-none z-10"
          style={{
            backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.18) 0px, rgba(0,0,0,0.18) 1px, transparent 1px, transparent 2px)',
          }}
        />
      )}

      {/* corner pixels */}
      <div className="absolute top-0 left-0 w-2 h-2" style={{ background: accentVar }} />
      <div className="absolute top-0 right-0 w-2 h-2" style={{ background: accentVar }} />
      <div className="absolute bottom-0 left-0 w-2 h-2" style={{ background: accentVar }} />
      <div className="absolute bottom-0 right-0 w-2 h-2" style={{ background: accentVar }} />

      <div className="relative z-20 p-4">
        {/* top: OVR + carta badge + nivel */}
        <div className="flex items-start justify-between mb-4">
          <div>
            {/* carta badge */}
            {cartaBadge && (
              <div
                className="text-[10px] mb-0.5 leading-none tracking-widest"
                style={{ color: resolvedCartaCor ?? accentVar, fontFamily: 'var(--font-pixel)' }}
              >
                {cartaBadge}
              </div>
            )}
            <div
              className="leading-none tabular-nums"
              style={{
                fontFamily: 'var(--font-pixel)',
                fontSize: '52px',
                color: colorVar,
              }}
            >
              {displayOvr || '--'}
            </div>
            {/* show boosted indicator */}
            {boostDiff > 0 && (
              <div className="text-[8px] leading-none" style={{ color: '#00FF88', fontFamily: 'var(--font-arcade)' }}>
                +{boostDiff} BOOST
              </div>
            )}
            <div className="text-[9px] mt-1" style={{ color: colorVar, fontFamily: 'var(--font-arcade)', letterSpacing: '0.16em' }}>
              OVERALL
            </div>
            <div className="mt-1 text-[8px]" style={{ color: accentVar, fontFamily: 'var(--font-arcade)', letterSpacing: '0.14em' }}>
              {tier}
            </div>
            <div
              className="mt-2 border-2 px-2 py-1 text-[9px] inline-block"
              style={{ borderColor: accentVar, color: accentVar, fontFamily: 'var(--font-pixel)' }}
            >
              {specialDuplas ? palette.label : tour.toUpperCase()}
            </div>
          </div>

          <div className="text-right">
            <div className="text-4xl mb-1" style={{ imageRendering: 'pixelated' }}>🎾</div>
            <div className="text-[9px]" style={{ fontFamily: 'var(--font-arcade)', color: 'var(--text-secondary)' }}>
              LVL {nivel}
            </div>
            <div className="text-[9px] mt-0.5" style={{ fontFamily: 'var(--font-arcade)', color: 'var(--text-secondary)' }}>
              #{ranking > 0 ? ranking : '?'} WR
            </div>
            {duplas > 0 && (
              <div className="mt-1 text-[8px]" style={{ fontFamily: 'var(--font-arcade)', color: specialDuplas ? accentVar : 'var(--text-faint)' }}>
                DUP {duplas}
              </div>
            )}
          </div>
        </div>

        {/* name + flag */}
        <div className="mb-3 flex items-center gap-2">
          <PixelFlag countryCode={nacionalidade} size="sm" />
          <div
            className="text-[14px] uppercase tracking-wide truncate leading-tight"
            style={{ fontFamily: 'var(--font-pixel)', color: 'var(--text-primary)' }}
          >
            {nome}
          </div>
        </div>

        {/* pixel divider */}
        <div className="flex gap-[2px] mb-3">
          {Array.from({ length: 20 }).map((_, i) => (
            <div key={i} className="flex-1 h-[3px]" style={{ background: i % 2 === 0 ? accentVar : 'transparent' }} />
          ))}
        </div>

        {/* 6-stat row */}
        <div className="grid grid-cols-6 gap-1 text-center">
          {STAT_KEYS.map(({ key, label }) => {
            const baseVal = resolveStat(key, atributos, atributosPsicologicos)
            const boostedVal = resolveStat(key, effectiveAtributos, atributosPsicologicos)
            const hasBoosted = boostedVal !== undefined && baseVal !== undefined && boostedVal > baseVal
            return (
              <div
                key={key}
                className="border"
                style={{
                  borderColor: `color-mix(in srgb, ${accentVar} 40%, transparent)`,
                  background: 'var(--surface-card)',
                }}
              >
                <div
                  className="text-[14px] font-black tabular-nums py-1.5"
                  style={{ color: 'var(--neon-cyan)', fontFamily: 'var(--font-pixel)' }}
                >
                  {boostedVal ?? '--'}
                </div>
                {hasBoosted && (
                  <div
                    className="text-[7px] leading-none pb-0.5"
                    style={{ color: '#00FF88', fontFamily: 'var(--font-arcade)' }}
                  >
                    +{boostedVal! - baseVal!}
                  </div>
                )}
                <div
                  className="text-[7px] pb-1.5"
                  style={{ color: 'var(--text-faint)', fontFamily: 'var(--font-arcade)', letterSpacing: '0.1em' }}
                >
                  {label}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </motion.div>
  )
}
