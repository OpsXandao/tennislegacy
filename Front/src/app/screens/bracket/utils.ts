import type { BracketNode } from '../../../types'
import {
  FASE_ORDEM,
  HEADER_HEIGHT,
  CARD_HEIGHT,
  CARD_WIDTH,
  COLUMN_GAP,
  INITIAL_MATCH_GAP,
  type MatchCardData,
  type ParsedRowScore,
  type Round,
  type LayoutRound,
  type BracketSection,
} from './types'

export function faseOrdem(fase: string) {
  return FASE_ORDEM[fase.toLowerCase()] ?? 99
}

export function faseLabelDisplay(fase: string): string {
  const map: Record<string, string> = {
    qualy_1: 'QUALY 1',
    qualy_2: 'QUALY 2',
    qualy_r1: 'QUALY 1',
    qualy_r2: 'QUALY 2',
    qualy_r3: 'QUALY 3',
    r96: 'R96',
    r128: 'R128',
    r64: 'R64',
    r32: 'R32',
    r16: 'OF',
    pre_oitavas: 'R32',
    oitavas: 'OF',
    quartas: 'QF',
    qf: 'QF',
    semis: 'SF',
    sf: 'SF',
    semifinal: 'SF',
    final: 'FINAL',
    f: 'FINAL',
  }
  return map[fase.toLowerCase()] ?? fase.toUpperCase()
}

export function extractCountry(name: string): string | undefined {
  const match = name.match(/\[(.*?)\]/)
  return match ? match[1] : undefined
}

export function cleanName(name: string): string {
  return name.replace(/\[.*?\]/, '').trim()
}

export function matchNome(a: string, b: string): boolean {
  const nameA = a.trim().toLowerCase()
  const nameB = b.trim().toLowerCase()
  if (nameA === nameB) return true
  return nameA.includes(nameB) || nameB.includes(nameA)
}

export function countSetWins(score: string): ParsedRowScore | null {
  const sets = score.match(/(\d+)\s*[/\-]\s*(\d+)/g)
  if (!sets || sets.length === 0) return null

  let player1 = 0
  let player2 = 0
  for (const setScore of sets) {
    const parsed = setScore.match(/(\d+)\s*[/\-]\s*(\d+)/)
    if (!parsed) continue
    const a = Number(parsed[1])
    const b = Number(parsed[2])
    if (a > b) player1 += 1
    if (b > a) player2 += 1
  }

  return { player1: String(player1), player2: String(player2) }
}

export function parseRowScores(
  score: string | undefined,
  player1Name?: string,
  player2Name?: string
): ParsedRowScore | null {
  if (!score) return null

  const namedMatch = score.match(/^\s*(.+?)\s+(\d+)\s*x\s*(\d+)\s+(.+?)\s*$/i)
  if (namedMatch && player1Name && player2Name) {
    const leftName = cleanName(namedMatch[1])
    const leftScore = namedMatch[2]
    const rightScore = namedMatch[3]
    const rightName = cleanName(namedMatch[4])

    if (matchNome(leftName, player1Name) && matchNome(rightName, player2Name)) {
      return { player1: leftScore, player2: rightScore }
    }

    if (matchNome(leftName, player2Name) && matchNome(rightName, player1Name)) {
      return { player1: rightScore, player2: leftScore }
    }
  }

  const matchScore = score.match(/(\d+)\s*x\s*(\d+)/i)
  if (matchScore) {
    return { player1: matchScore[1], player2: matchScore[2] }
  }

  return countSetWins(score)
}

export function fasesEsperadas(tipo?: string): string[] {
  const label = String(tipo || '')
  if (label === 'Grand Slam') {
    return ['qualy_r1', 'qualy_r2', 'qualy_r3', 'r128', 'r64', 'r32', 'r16', 'quartas', 'semifinal', 'final']
  }
  if (label.includes('1000')) {
    return ['qualy_1', 'qualy_2', 'r96', 'r64', 'r32', 'r16', 'quartas', 'semifinal', 'final']
  }
  if (label.includes('Finals')) {
    return ['quartas', 'semifinal', 'final']
  }
  return ['qualy_1', 'qualy_2', 'pre_oitavas', 'oitavas', 'quartas', 'semifinal', 'final']
}

export function isQualyPhase(fase: string): boolean {
  return fase.toLowerCase().startsWith('qualy')
}

function expectedMainRounds(tipo?: string): string[] {
  return fasesEsperadas(tipo).filter((fase) => !isQualyPhase(fase))
}

function isPlaceholderMatch(match: MatchCardData): boolean {
  return cleanName(match.player1) === '---' && cleanName(match.player2) === '---'
}

function trimPlaceholderRounds(rounds: Round[]): Round[] {
  return rounds.filter((round) => round.matches.some((match) => !isPlaceholderMatch(match)))
}

function completarMainRounds(rounds: Round[], tipo?: string): Round[] {
  if (rounds.length === 0) return []

  const byFase = new Map(rounds.map((round) => [round.fase, round]))
  const orderedPhases = expectedMainRounds(tipo).filter(
    (fase) => byFase.has(fase) || faseOrdem(fase) >= faseOrdem(rounds[0].fase)
  )
  const result: Round[] = []
  let previousMatchCount = rounds[0].matches.length

  for (const fase of orderedPhases) {
    const existing = byFase.get(fase)
    if (existing) {
      previousMatchCount = Math.max(1, existing.matches.length)
      result.push(existing)
      continue
    }

    const nextCount = Math.max(1, Math.ceil(previousMatchCount / 2))
    result.push({
      name: faseLabelDisplay(fase),
      fase,
      matches: Array.from({ length: nextCount }, (_, index) => ({
        id: `${fase}:placeholder:${index}`,
        player1: '---',
        player2: '---',
      })),
    })
    previousMatchCount = nextCount
  }

  return result
}

export function splitRounds(rounds: Round[], tipo?: string): BracketSection[] {
  const qualyRounds = trimPlaceholderRounds(
    rounds.filter((round) => isQualyPhase(round.fase))
  )
  const mainRounds = completarMainRounds(
    rounds.filter((round) => !isQualyPhase(round.fase)),
    tipo
  )
  const sections: BracketSection[] = []

  if (qualyRounds.length > 0) {
    sections.push({
      id: 'qualy',
      title: 'QUALIFYING',
      subtitle: 'Fase classificatoria',
      rounds: qualyRounds,
    })
  }

  if (mainRounds.length > 0) {
    const mainLabel = String(tipo || '').includes('Finals') ? 'FINALS DRAW' : 'MAIN DRAW'
    sections.push({
      id: 'main',
      title: mainLabel,
      subtitle: 'Chave principal',
      rounds: mainRounds,
    })
  }

  return sections
}

export function nodesToRounds(
  nodes: BracketNode[],
  faseAtual: string,
  jogadorAtivo: boolean,
  nomeJogador: string
): Round[] {
  const byFase = new Map<string, BracketNode[]>()
  for (const node of nodes) {
    const arr = byFase.get(node.fase) ?? []
    arr.push(node)
    byFase.set(node.fase, arr)
  }

  const fasesOrdenadas = [...byFase.keys()].sort(
    (a, b) => faseOrdem(a) - faseOrdem(b)
  )

  return fasesOrdenadas.map((fase) => ({
    name: faseLabelDisplay(fase),
    fase,
    matches: (byFase.get(fase) ?? []).map((node, index) => {
      const temVencedor = !!node.vencedor
      const isAtual =
        !temVencedor &&
        jogadorAtivo &&
        fase.toLowerCase() === faseAtual.toLowerCase() &&
        (matchNome(node.jogador1, nomeJogador) || matchNome(node.jogador2, nomeJogador))

      return {
        id: node.id || `${fase}:${index}`,
        player1: node.jogador1 || '---',
        player2: node.jogador2 || '---',
        player1Nationality: node.jogador1_nacionalidade,
        player2Nationality: node.jogador2_nacionalidade,
        score: node.placar,
        winner: node.vencedor
          ? node.vencedor === node.jogador1
            ? 1
            : 2
          : undefined,
        isCurrentMatch: isAtual,
      }
    }),
  }))
}

export function buildBracketLayout(rounds: Round[]): LayoutRound[] {
  const layout: LayoutRound[] = []

  for (const [roundIndex, round] of rounds.entries()) {
    const x = roundIndex * (CARD_WIDTH + COLUMN_GAP)
    let positions: number[] = []

    if (roundIndex === 0) {
      positions = round.matches.map((_, index) => index * (CARD_HEIGHT + INITIAL_MATCH_GAP))
    } else {
      const prev = rounds[roundIndex - 1]
      const prevLayout = layout[roundIndex - 1]
      positions = round.matches.map((_, index) => {
        const topMatch = prevLayout.positions[index * 2] ?? 0
        const bottomMatch = prevLayout.positions[index * 2 + 1] ?? topMatch
        const topMid = topMatch + CARD_HEIGHT / 2
        const bottomMid = bottomMatch + CARD_HEIGHT / 2
        return (topMid + bottomMid) / 2 - CARD_HEIGHT / 2
      })
      if (!prev.matches.length && round.matches.length) {
        positions = round.matches.map((_, index) => index * (CARD_HEIGHT + INITIAL_MATCH_GAP))
      }
    }

    layout.push({ round, x, positions })
  }

  return layout
}
