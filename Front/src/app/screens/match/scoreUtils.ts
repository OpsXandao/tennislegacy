import type { MatchPointRuntime, PlacarState } from '../../../types'

export interface MatchNarrativePulse {
  headline: string
  subline: string
  color: string
  recommendation: string
  shouldPause: boolean
  pauseKey: string
}

export function detectBreakPoint(p: PlacarState): string {
  const { pontos, servindo } = p
  const j = pontos[0] === '40' || pontos[0] === 'AD'
  const a = pontos[1] === '40' || pontos[1] === 'AD'
  if (servindo === 'adversario' && j && !a) return 'BREAK POINT!'
  if (servindo === 'jogador' && a && !j) return 'BREAK POINT!'
  return ''
}

export function calcMomentum(p: PlacarState): number {
  const map: Record<string, number> = { '0': 0, '15': 1, '30': 2, '40': 3, AD: 4, '-': 0 }
  const sets = (p.sets[0] - p.sets[1]) * 18
  const games = (p.games[0] - p.games[1]) * 4
  const pts = ((map[p.pontos[0]] ?? 0) - (map[p.pontos[1]] ?? 0)) * 3
  return Math.max(0, Math.min(100, 50 + sets + games + pts))
}

export function corMomentum(momentum: number): string {
  if (momentum >= 66) return 'var(--neon-green)'
  if (momentum <= 34) return '#ff4466'
  return 'var(--neon-yellow)'
}

export function detectarPontoCritico(p: PlacarState): { label: string; color: string } | null {
  const j = p.pontos[0]
  const a = p.pontos[1]
  const gamesJ = p.games[0]
  const gamesA = p.games[1]
  const setsJ = p.sets[0]
  const setsA = p.sets[1]
  const melhorDe = Math.max(2, (setsJ + setsA + 1))
  const alvoSets = melhorDe >= 3 ? 2 : 1
  const jogadorEmVantagemNoPonto = j === '40' || j === 'AD'
  const rivalEmVantagemNoPonto = a === '40' || a === 'AD'

  if (setsJ === alvoSets - 1 && gamesJ === 5 && jogadorEmVantagemNoPonto) {
    return { label: 'MATCH POINT', color: 'var(--neon-yellow)' }
  }
  if (setsA === alvoSets - 1 && gamesA === 5 && rivalEmVantagemNoPonto) {
    return { label: 'MATCH POINT CONTRA', color: 'var(--neon-pink)' }
  }
  if (gamesJ === 5 && jogadorEmVantagemNoPonto) return { label: 'SET POINT', color: 'var(--neon-yellow)' }
  if (gamesA === 5 && rivalEmVantagemNoPonto) return { label: 'SET POINT CONTRA', color: '#ff4466' }
  const breakLabel = detectBreakPoint(p)
  if (breakLabel) return { label: breakLabel, color: '#ff9900' }
  return null
}

type LastPointStats = MatchPointRuntime['last_point_stats']

export function resumirPulsoNarrativo(
  stats: LastPointStats,
  placar: PlacarState,
): MatchNarrativePulse | null {
  if (!stats) return null

  const sequenciaRival = stats.sequencia_a ?? 0
  const sequenciaJogador = stats.sequencia_j ?? 0
  const rivalLevou = stats.vencedor === 'a'
  const voceLevou = stats.vencedor === 'j'

  let headline = ''
  let subline = ''
  let color = 'var(--neon-cyan)'
  let recommendation = 'Mantenha o plano, mas monitore o padrão do ponto.'
  let shouldPause = false

  if (stats.momento === 'match_point') {
    headline = 'MATCH POINT'
    subline = rivalLevou ? 'o rival venceu o ponto mais pesado' : 'você respondeu sob máxima pressão'
    color = rivalLevou ? 'var(--neon-pink)' : 'var(--neon-yellow)'
    recommendation = rivalLevou
      ? 'Mude o plano no próximo ponto grande. Priorize consistência ou ataque o segundo saque.'
      : 'Insista no que funcionou no ponto grande e mantenha a execução simples.'
    shouldPause = true
  } else if (stats.momento === 'set_point') {
    headline = 'SET POINT'
    subline = rivalLevou ? 'o rival cresceu na reta do set' : 'você segurou ou atacou no ponto decisivo'
    color = rivalLevou ? 'var(--neon-pink)' : 'var(--neon-yellow)'
    recommendation = rivalLevou
      ? 'Reduza risco gratuito. O set está sendo decidido em execução, não em volume.'
      : 'Se a pressão seguir alta, mantenha o mesmo padrão por mais 1 ou 2 pontos.'
    shouldPause = true
  } else if (stats.momento === 'break_point') {
    headline = 'BREAK POINT'
    subline = rivalLevou ? 'você cedeu espaço no game de saque' : 'você entrou forte na devolução'
    color = rivalLevou ? 'var(--neon-pink)' : 'var(--neon-yellow)'
    recommendation = rivalLevou
      ? 'Proteja o saque com um plano mais limpo no ponto seguinte.'
      : 'Continue pressionando a devolução se o rival seguir curto no segundo saque.'
    shouldPause = true
  } else if (placar.games[0] === 6 && placar.games[1] === 6) {
    headline = 'TIEBREAK'
    subline = 'cada mini-break muda a partida'
    color = 'var(--neon-yellow)'
    recommendation = 'Escolha um padrão simples e repita. Tiebreak pune improviso.'
    shouldPause = true
  } else if (sequenciaRival >= 3) {
    headline = 'RIVAL EM SEQUÊNCIA'
    subline = `${sequenciaRival} pontos seguidos contra você`
    color = 'var(--neon-pink)'
    recommendation = 'Quebre o ritmo agora: mude mentalidade ou ataque uma fraqueza específica.'
    shouldPause = true
  } else if (sequenciaJogador >= 3) {
    headline = 'VOCÊ ASSUMIU O CONTROLE'
    subline = `${sequenciaJogador} pontos seguidos no seu lado`
    color = 'var(--neon-green)'
    recommendation = 'Não entregue iniciativa. Continue no padrão que está desmontando o rival.'
  } else if (stats.padrao) {
    headline = stats.padrao.toUpperCase()
    subline = stats.intensidade === 'longo' ? 'troca longa virou a história do ponto' : 'o padrão do ponto apareceu cedo'
    color = voceLevou ? 'var(--neon-green)' : 'var(--neon-cyan)'
    recommendation = rivalLevou
      ? 'Responda ao padrão dominante do rival antes que ele vire tendência.'
      : 'Se esse padrão se repetir, transforme isso no seu plano principal.'
  }

  if (!headline) return null
  return {
    headline,
    subline,
    color,
    recommendation,
    shouldPause,
    pauseKey: `${stats.momento}-${stats.sequencia_j}-${stats.sequencia_a}-${placar.games[0]}-${placar.games[1]}-${placar.pontos[0]}-${placar.pontos[1]}`,
  }
}
