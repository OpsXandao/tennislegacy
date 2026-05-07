import { useEffect, useState } from 'react'
import { motion } from 'motion/react'
import { useNavigate } from 'react-router'
import { ActionDock, NeonButton, PixelFlag, PageHeader } from '../components'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'
import type { BracketNode, PartidaScout, TorneioState } from '../../types'

const FASE_ORDEM: Record<string, number> = {
  qualy_r1: -3,
  qualy_1: -3,
  qualy_r2: -2,
  qualy_2: -2,
  qualy_r3: -1,
  r96: 0,
  r128: 0,
  r64: 1,
  r32: 2,
  pre_oitavas: 3,
  oitavas: 4,
  r16: 4,
  quartas: 5,
  qf: 5,
  semis: 6,
  sf: 6,
  semifinal: 6,
  final: 7,
  f: 7,
}

const HEADER_HEIGHT = 44
const CARD_HEIGHT = 64
const CARD_WIDTH = 220
const COLUMN_GAP = 78
const INITIAL_MATCH_GAP = 22

interface MatchCardData {
  id: string
  player1: string
  player2: string
  player1Nationality?: string
  player2Nationality?: string
  score?: string
  winner?: 1 | 2
  isCurrentMatch?: boolean
}

interface ParsedRowScore {
  player1?: string
  player2?: string
}

interface Round {
  name: string
  fase: string
  matches: MatchCardData[]
}

interface LayoutRound {
  round: Round
  x: number
  positions: number[]
}

interface BracketSection {
  id: 'qualy' | 'main'
  title: string
  subtitle: string
  rounds: Round[]
}

function faseOrdem(fase: string) {
  return FASE_ORDEM[fase.toLowerCase()] ?? 99
}

function faseLabelDisplay(fase: string): string {
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

function extractCountry(name: string): string | undefined {
  const match = name.match(/\[(.*?)\]/)
  return match ? match[1] : undefined
}

function cleanName(name: string): string {
  return name.replace(/\[.*?\]/, '').trim()
}

function matchNome(a: string, b: string): boolean {
  const nameA = a.trim().toLowerCase()
  const nameB = b.trim().toLowerCase()
  if (nameA === nameB) return true
  // Suporte para duplas: verifica se o nome do jogador está contido no nome da dupla
  return nameA.includes(nameB) || nameB.includes(nameA)
}

function countSetWins(score: string): ParsedRowScore | null {
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

function parseRowScores(
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
      return {
        player1: leftScore,
        player2: rightScore,
      }
    }

    if (matchNome(leftName, player2Name) && matchNome(rightName, player1Name)) {
      return {
        player1: rightScore,
        player2: leftScore,
      }
    }
  }

  const matchScore = score.match(/(\d+)\s*x\s*(\d+)/i)
  if (matchScore) {
    return {
      player1: matchScore[1],
      player2: matchScore[2],
    }
  }

  return countSetWins(score)
}

function fasesEsperadas(tipo?: string): string[] {
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

function isQualyPhase(fase: string): boolean {
  return fase.toLowerCase().startsWith('qualy')
}

function splitRounds(rounds: Round[], tipo?: string): BracketSection[] {
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

function nodesToRounds(
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

function buildBracketLayout(rounds: Round[]): LayoutRound[] {
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

export function TournamentBracket() {
  const navigate = useNavigate()
  const { jogador, setTorneio, setPartidaId, semana, ano } = useGameStore()
  const nomeJogador = jogador?.nome ?? ''

  const [torneio, setLocal] = useState<TorneioState | null>(null)
  const [rounds, setRounds] = useState<Round[]>([])
  const [sections, setSections] = useState<BracketSection[]>([])
  const [activeSectionId, setActiveSectionId] = useState<'qualy' | 'main'>('main')
  const [loading, setLoading] = useState(true)
  const [temPartidaPendente, setTemPartidaPendente] = useState(false)
  const [avancar, setAvancar] = useState(false)
  const [simulandoRestante, setSimulandoRestante] = useState(false)
  const [campeaoFinal, setCampeaoFinal] = useState<string | null>(null)
  const [erroAcao, setErroAcao] = useState('')
  const [scoutData, setScoutData] = useState<PartidaScout | null>(null)
  const [loadingScout, setLoadingScout] = useState(false)
  const [confirmDesistir, setConfirmDesistir] = useState(false)

  function limparEstadoTorneio() {
    setLocal(null)
    setTorneio(null)
    setRounds([])
    setSections([])
    setTemPartidaPendente(false)
  }

  useEffect(() => {
    api.torneio
      .estado()
      .then((t) => {
        if (!t) {
          limparEstadoTorneio()
          return
        }
        setLocal(t)
        setTorneio(t)
        const parsed = nodesToRounds(t.bracket, t.fase_atual, t.jogador_ativo, nomeJogador)
        const parsedSections = splitRounds(parsed, t.tipo)
        setRounds(parsed)
        setSections(parsedSections)
        setActiveSectionId(isQualyPhase(t.fase_atual) ? 'qualy' : 'main')
        setTemPartidaPendente(!!t.partida_disponivel)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [nomeJogador, setTorneio])

  async function handleAvancarFase() {
    setAvancar(true)
    try {
      await api.torneio.avancarFase()
      const t = await api.torneio.estado()
      if (!t) {
        limparEstadoTorneio()
        navigate('/hub')
        return
      }
      setLocal(t)
      setTorneio(t)
      const parsed = nodesToRounds(t.bracket, t.fase_atual, t.jogador_ativo, nomeJogador)
      const parsedSections = splitRounds(parsed, t.tipo)
      setRounds(parsed)
      setSections(parsedSections)
      setActiveSectionId(isQualyPhase(t.fase_atual) ? 'qualy' : 'main')
      setTemPartidaPendente(!!t.partida_disponivel)
    } catch {
      // Mantem a UI responsiva sem interromper o fluxo do usuario.
    } finally {
      setAvancar(false)
    }
  }

  async function handleAnalisarAdversario() {
    const nomeAdv = torneio?.info_partida?.adversario?.nome
    if (!nomeAdv) {
      handleJogar()
      return
    }
    setLoadingScout(true)
    try {
      const data = await api.partida.scout(nomeAdv)
      setScoutData(data)
    } catch {
      // Scout falhou — ir direto para a partida
      handleJogar()
    } finally {
      setLoadingScout(false)
    }
  }

  async function handleJogar() {
    setScoutData(null)
    setErroAcao('')
    try {
      const ativa = await api.partida.ativa()
      if (ativa?.partida_id) {
        setPartidaId(ativa.partida_id)
      } else {
        setPartidaId(null)
      }
      navigate('/match')
    } catch {
      setPartidaId(null)
      navigate('/match')
    }
  }

  // Helper para mostrar o nome da proxima fase no botao
  const getProximaFaseLabel = () => {
    if (!torneio || !torneio.bracket) return 'PROXIMA FASE'
    const atualKey = torneio.fase_atual.toLowerCase()
    const atualOrdem = FASE_ORDEM[atualKey] ?? 0
    
    // Pega as fases que REALMENTE existem neste bracket
    const fasesNoBracket = Array.from(new Set(torneio.bracket.map(n => n.fase.toLowerCase())))
    
    // Encontra a próxima fase no bracket que tem uma ordem estritamente maior
    const proxima = fasesNoBracket
      .sort((a, b) => FASE_ORDEM[a] - FASE_ORDEM[b])
      .find(f => FASE_ORDEM[f] > atualOrdem)
      
    if (proxima) {
      return `IR PARA ${faseLabelDisplay(proxima)}`
    }
    return 'AVANÇAR RODADA'
  }

  async function handleDesistir() {
    // Só chama desistir se o jogador ainda está ativo (evita sobrescrever eliminação)
    if (torneio?.jogador_ativo) {
      try {
        const r = await api.torneio.desistir()
        if (typeof r.semana === 'number') {
          setTorneio(null)
          setPartidaId(null)
          navigate('/week-advance', {
            replace: true,
            state: {
              fromSemana: semana,
              fromAno: ano,
              toSemana: r.semana,
              toAno: r.ano ?? ano,
              campeoes: r.resumo_mundial?.campeoes ?? [],
              eventos: r.eventos ?? [],
              motivo: 'withdraw',
            },
          })
          return
        }
      } catch {
        // ignora erro — avança mesmo assim
      }
    }
    setTorneio(null)
    navigate('/hub')
  }

  async function handleConcluirTorneio() {
    try {
      if (torneio?.fase_atual === 'finalizado' || campeaoFinal) {
        const r = await api.calendario.avancar()
        navigate('/week-advance', {
          replace: true,
          state: {
            fromSemana: semana,
            fromAno: ano,
            toSemana: r.semana,
            toAno: r.ano ?? ano,
            campeoes: r.resumo_mundial?.campeoes ?? [],
            eventos: r.eventos ?? [],
            motivo: 'tournament_end',
          },
        })
        return
      }
      navigate('/hub')
    } catch {
      navigate('/hub')
    } finally {
      setTorneio(null)
      setPartidaId(null)
    }
  }

  async function handleSimularRestante() {
    setSimulandoRestante(true)
    let iterations = 0
    const MAX_ITERATIONS = 20
    try {
      let t = torneio
      while (t && t.fase_atual !== 'finalizado' && iterations < MAX_ITERATIONS) {
        iterations++
        await api.torneio.avancarFase()
        t = await api.torneio.estado()
        if (!t) break
        setLocal(t)
        setTorneio(t)
        const parsed = nodesToRounds(t.bracket, t.fase_atual, t.jogador_ativo, nomeJogador)
        const parsedSections = splitRounds(parsed, t.tipo)
        setRounds(parsed)
        setSections(parsedSections)
        setActiveSectionId(isQualyPhase(t.fase_atual) ? 'qualy' : 'main')
      }
      if (t?.campeao_simples) {
        setCampeaoFinal(t.campeao_simples)
      }
    } catch {
      // mantém a UI responsiva
    } finally {
      setSimulandoRestante(false)
    }
  }

  return (
    <div className="app-shell min-h-screen overflow-x-clip pb-10">
      <PageHeader
        title={torneio?.nome || 'TOURNAMENT'}
        subtitle={torneio ? `${torneio.tipo} • ${torneio.superficie}` : 'CARREGANDO...'}
        color="green"
        backTo="/hub"
        right={torneio ? (
          <div className="border border-[#ffe600] px-2 py-1 text-[7px] text-[#ffe600]" style={{ fontFamily: 'var(--font-arcade)' }}>
            {torneio.fase_atual.toUpperCase()}
          </div>
        ) : undefined}
      />

      {loading && (
        <motion.div
          animate={{ opacity: [1, 0.3, 1] }}
          transition={{ duration: 1, repeat: Infinity }}
          className="text-center py-20 pixel-font text-sm text-[#00ff88]"
        >
          CARREGANDO...
        </motion.div>
      )}

      {!loading && rounds.length === 0 && (
        <div className="text-center py-20 arcade-font text-sm text-[#888]">
          Nenhum torneio ativo.
        </div>
      )}

      {!loading && rounds.length > 0 && (
        <div className="mx-auto w-full max-w-7xl space-y-5">
          {sections.length > 1 && (
            <div className="flex gap-2 overflow-x-auto pb-1">
              {sections.map((section) => {
                const active = section.id === activeSectionId
                return (
                  <button
                    key={section.id}
                    type="button"
                    onClick={() => setActiveSectionId(section.id)}
                    className="min-w-[160px] border-2 px-4 py-2 text-left transition-all"
                    style={{
                      borderColor: active ? 'var(--neon-yellow)' : 'var(--neon-cyan)',
                      backgroundColor: active
                        ? 'color-mix(in srgb, var(--neon-yellow) 16%, var(--surface-card))'
                        : 'color-mix(in srgb, var(--neon-cyan) 8%, var(--surface-card))',
                      boxShadow: active ? 'var(--glow-gold-sm)' : 'none',
                    }}
                  >
                    <div
                      className="pixel-font text-xs"
                      style={{ color: active ? 'var(--neon-yellow)' : 'var(--neon-cyan)' }}
                    >
                      {section.title}
                    </div>
                    <div className="arcade-font text-[10px] app-muted">
                      {section.subtitle}
                    </div>
                  </button>
                )
              })}
            </div>
          )}

          {sections
            .filter((section) => section.id === activeSectionId)
            .map((section) => (
              <BracketCanvas key={section.title} section={section} />
            ))}
        </div>
      )}

      {!loading && (
        <ActionDock>
          {erroAcao && (
            <div className="mb-3 border border-[#ff0055] bg-[#22040d] px-3 py-2 arcade-font text-[10px] text-[#ff8da9]">
              {erroAcao.toUpperCase()}
            </div>
          )}
          {/* Campeão revelado após simular restante */}
          {campeaoFinal && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-3 border-2 border-[#ffe600] bg-[#ffe600]/10 p-3 text-center shadow-[0_0_15px_rgba(255,230,0,0.3)]"
            >
              <div className="pixel-font text-[10px] text-[#ffe600] mb-1">CAMPEÃO DO TORNEIO</div>
              <div className="arcade-font text-sm text-white font-bold">{campeaoFinal.toUpperCase()}</div>
            </motion.div>
          )}

          {/* Modal de scouting do adversário */}
          {scoutData && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-3 border-2 border-[#00e5ff] bg-[#00e5ff]/5 p-3"
            >
              <div className="flex justify-between items-center mb-2">
                <div className="pixel-font text-[10px] text-[#00e5ff]">ANÁLISE DE ADVERSÁRIO</div>
                <button onClick={() => setScoutData(null)} className="arcade-font text-[9px] text-[#888]">✕ FECHAR</button>
              </div>
              <div className="flex gap-3 items-start mb-2">
                <div>
                  <div className="arcade-font text-[11px] text-white font-bold">{scoutData.nome}</div>
                  <div className="arcade-font text-[9px] text-[#888]">
                    #{scoutData.ranking} • OVR {scoutData.overall} • {scoutData.superficie_favorita}
                  </div>
                </div>
                <div className="ml-auto flex gap-1">
                  {scoutData.forma_recente.map((r: string, i: number) => (
                    <div
                      key={i}
                      className="w-5 h-5 flex items-center justify-center arcade-font text-[8px] font-bold border"
                      style={{
                        background: r === 'V' ? '#00ff8820' : '#ff005520',
                        borderColor: r === 'V' ? '#00ff88' : '#ff0055',
                        color: r === 'V' ? '#00ff88' : '#ff0055',
                      }}
                    >{r}</div>
                  ))}
                </div>
              </div>
              {Object.keys(scoutData.atributos || {}).length > 0 && (
                <div className="grid grid-cols-4 gap-1 mb-2">
                  {Object.entries(scoutData.atributos as Record<string, number>).slice(0, 8).map(([k, v]) => (
                    <div key={k} className="border border-[#00e5ff]/30 bg-black/30 px-1 py-1 text-center">
                      <div className="arcade-font text-[7px] text-[#8eb5c8]">{k.slice(0, 4).toUpperCase()}</div>
                      <div className="pixel-font text-[10px] text-[#00e5ff]">{v}</div>
                    </div>
                  ))}
                </div>
              )}
              <div className="flex justify-between items-center">
                <div className="arcade-font text-[9px] text-[#888]">
                  H2H: <span className="text-[#00ff88]">{scoutData.h2h.vitorias_jogador}V</span>
                  {' '}/{' '}
                  <span className="text-[#ff0055]">{scoutData.h2h.vitorias_adversario}D</span>
                </div>
                <NeonButton variant="yellow" className="text-[9px] px-3 py-1" onClick={handleJogar}>
                  ▶ JOGAR AGORA
                </NeonButton>
              </div>
            </motion.div>
          )}

          {/* Eliminado: mostrar opções de simular restante ou sair */}
          {!torneio || !torneio.jogador_ativo ? (
            campeaoFinal || torneio?.fase_atual === 'finalizado' ? (
              <NeonButton variant="green" className="w-full" onClick={handleConcluirTorneio}>
                AVANÇAR SEMANA
              </NeonButton>
            ) : (
              <div className="grid gap-3 grid-cols-2">
                <NeonButton
                  variant="yellow"
                  className="w-full"
                  onClick={handleSimularRestante}
                  blink={simulandoRestante}
                >
                  {simulandoRestante ? 'SIMULANDO...' : 'SIMULAR RESTANTE'}
                </NeonButton>
                <NeonButton variant="pink" className="w-full" onClick={() => setConfirmDesistir(true)}>
                  SAIR
                </NeonButton>
              </div>
            )
          ) : (
            <div className="grid gap-3 md:grid-cols-2">
              {temPartidaPendente ? (
                <div className="grid grid-cols-2 gap-2">
                  <NeonButton
                    variant="cyan"
                    className="w-full text-[9px]"
                    onClick={handleAnalisarAdversario}
                    blink={loadingScout}
                  >
                    {loadingScout ? '...' : '🔍 ANALISAR'}
                  </NeonButton>
                  <NeonButton variant="yellow" className="w-full" onClick={handleJogar} blink>
                    ▶ JOGAR
                  </NeonButton>
                </div>
              ) : (
                <NeonButton
                  variant="green"
                  className="w-full"
                  onClick={handleAvancarFase}
                  blink={avancar}
                >
                  {avancar ? 'AVANÇANDO...' : getProximaFaseLabel()}
                </NeonButton>
              )}
              <NeonButton variant="pink" className="w-full" onClick={() => setConfirmDesistir(true)}>
                DESISTIR
              </NeonButton>
            </div>
          )}
        </ActionDock>
      )}

      {confirmDesistir && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-sm border-2 border-[#ff0055] bg-[#0d0006] p-5 shadow-[0_0_24px_rgba(255,0,85,0.25)]">
            <div className="arcade-font text-[10px] tracking-[0.2em] text-[#ff0055] mb-3">CONFIRMAR DESISTÊNCIA</div>
            <div className="pixel-font text-sm text-white mb-2">Tem certeza que deseja desistir?</div>
            <div className="arcade-font text-[10px] text-[#9b6677] leading-relaxed mb-5">
              Você perderá os pontos desta fase. O torneio continuará sem você.
            </div>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setConfirmDesistir(false)}
                className="min-h-[44px] border-2 border-[#555] px-4 py-3 arcade-font text-[10px] text-[#aaa]"
              >
                CANCELAR
              </button>
              <button
                type="button"
                onClick={() => { setConfirmDesistir(false); handleDesistir() }}
                className="min-h-[44px] border-2 border-[#ff0055] px-4 py-3 arcade-font text-[10px] text-[#ff7d9e]"
              >
                DESISTIR
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function BracketCanvas({ section }: { section: BracketSection }) {
  const layout = buildBracketLayout(section.rounds)
  const totalWidth =
    layout.length > 0 ? layout[layout.length - 1].x + CARD_WIDTH + 20 : CARD_WIDTH
  const totalHeight =
    HEADER_HEIGHT +
    Math.max(
      220,
      ...layout.flatMap((column) => column.positions.map((top) => top + CARD_HEIGHT + 20))
    )

  return (
    <section className="overflow-hidden rounded border border-[#ff0055]/40 bg-[#090909] shadow-[0_0_20px_#ff005533]">
      <div className="sticky top-0 z-[1] flex items-center justify-between border-b border-[#00ff88]/20 bg-[#111] px-4 py-3">
        <div>
          <h3 className="pixel-font text-sm text-[#00ff88]">{section.title}</h3>
          <p className="arcade-font text-[10px] text-[#888]">{section.subtitle}</p>
        </div>
        <div className="arcade-font text-[10px] text-[#ffe600]">
          {section.rounds.length} fases
        </div>
      </div>

      <div className="overflow-x-auto overflow-y-hidden px-3 py-4 sm:p-4">
        <div
          className="relative"
          style={{ width: `${totalWidth}px`, height: `${totalHeight}px` }}
        >
          {layout.map((column, roundIndex) => (
            <div key={column.round.fase}>
              <div
                className="absolute bg-[#131326] border border-[#00ff88] px-3 py-2 text-center shadow-[0_0_12px_#00ff8844]"
                style={{ left: `${column.x}px`, top: '0px', width: `${CARD_WIDTH}px` }}
              >
                <span className="arcade-font text-xs text-[#00ff88]">{column.round.name}</span>
              </div>

              {column.round.matches.map((match, matchIndex) => (
                <div
                  key={match.id}
                  className="absolute"
                  style={{
                    left: `${column.x}px`,
                    top: `${HEADER_HEIGHT + column.positions[matchIndex]}px`,
                    width: `${CARD_WIDTH}px`,
                    height: `${CARD_HEIGHT}px`,
                  }}
                >
                  <BracketMatchCard
                    match={match}
                    showQualifierSlots={section.id === 'main' && roundIndex === 0}
                  />
                </div>
              ))}

              {roundIndex < layout.length - 1 &&
                column.round.matches.map((_, matchIndex) => {
                  const y = HEADER_HEIGHT + column.positions[matchIndex] + CARD_HEIGHT / 2
                  const pairIndex = Math.floor(matchIndex / 2)
                  const nextColumn = layout[roundIndex + 1]
                  const nextY =
                    HEADER_HEIGHT + nextColumn.positions[pairIndex] + CARD_HEIGHT / 2
                  const midX = column.x + CARD_WIDTH + 22
                  const horizontalWidth = 22

                  return (
                    <div key={`${column.round.fase}:connector:${matchIndex}`}>
                      <div
                        className="absolute bg-[#8a8a8a]"
                        style={{
                          left: `${column.x + CARD_WIDTH}px`,
                          top: `${y}px`,
                          width: `${horizontalWidth}px`,
                          height: '2px',
                        }}
                      />
                      {matchIndex % 2 === 0 && (
                        <>
                          <div
                            className="absolute bg-[#8a8a8a]"
                            style={{
                              left: `${midX}px`,
                              top: `${Math.min(
                                y,
                                HEADER_HEIGHT +
                                  (column.positions[matchIndex + 1] ?? column.positions[matchIndex]) +
                                  CARD_HEIGHT / 2
                              )}px`,
                              width: '2px',
                              height: `${Math.abs(
                                (HEADER_HEIGHT +
                                  (column.positions[matchIndex + 1] ?? column.positions[matchIndex]) +
                                  CARD_HEIGHT / 2) -
                                  y
                              )}px`,
                            }}
                          />
                          <div
                            className="absolute bg-[#8a8a8a]"
                            style={{
                              left: `${midX}px`,
                              top: `${nextY}px`,
                              width: `${nextColumn.x - midX}px`,
                              height: '2px',
                            }}
                          />
                        </>
                      )}
                    </div>
                  )
                })}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function BracketMatchCard({
  match,
  showQualifierSlots = false,
}: {
  match: MatchCardData
  showQualifierSlots?: boolean
}) {
  const { jogador } = useGameStore()
  const jogadorNome = jogador?.nome ?? ''

  const getPlayerFlag = (name: string, nationality?: string) => {
    if (nationality && nationality !== '??') return nationality
    if (matchNome(name, jogadorNome)) return jogador?.nacionalidade
    return extractCountry(name)
  }

  const isPlayer1 = matchNome(match.player1, jogadorNome)
  const isPlayer2 = matchNome(match.player2, jogadorNome)
  const borderColor = match.isCurrentMatch ? '#ffe600' : '#8a8a8a'
  const isPlaceholder1 = cleanName(match.player1) === '---'
  const isPlaceholder2 = cleanName(match.player2) === '---'
  const label1 = showQualifierSlots && isPlaceholder1 ? 'Q' : cleanName(match.player1)
  const label2 = showQualifierSlots && isPlaceholder2 ? 'Q' : cleanName(match.player2)
  const parsedScore = parseRowScores(match.score, match.player1, match.player2)

  return (
    <div
      className={`relative h-full bg-[#f2f2f2] text-black border-2 px-2 py-1 ${
        match.isCurrentMatch ? 'shadow-[0_0_12px_#ffe600]' : 'shadow-[0_0_8px_#00000055]'
      }`}
      style={{ borderColor }}
    >
      <div
        className={`flex items-center gap-2 h-1/2 border-b ${
          match.winner === 1 ? 'text-[#0f8c3a]' : match.winner === 2 ? 'text-[#666]' : 'text-black'
        }`}
        style={{ borderColor: '#bdbdbd' }}
      >
        {!isPlaceholder1 && (
          <PixelFlag
            countryCode={getPlayerFlag(match.player1, match.player1Nationality)}
            size="sm"
          />
        )}
        <span
          className={`arcade-font text-[10px] truncate flex-1 ${
            isPlayer1 ? 'text-[#b00020]' : ''
          } ${showQualifierSlots && isPlaceholder1 ? 'text-[#0048ff]' : ''}`}
        >
          {label1}
        </span>
        {parsedScore?.player1 && (
          <span className="arcade-font text-[10px] min-w-[16px] text-right text-[#003e93]">
            {parsedScore.player1}
          </span>
        )}
      </div>

      <div
        className={`flex items-center gap-2 h-1/2 ${
          match.winner === 2 ? 'text-[#0f8c3a]' : match.winner === 1 ? 'text-[#666]' : 'text-black'
        }`}
      >
        {!isPlaceholder2 && (
          <PixelFlag
            countryCode={getPlayerFlag(match.player2, match.player2Nationality)}
            size="sm"
          />
        )}
        <span
          className={`arcade-font text-[10px] truncate flex-1 ${
            isPlayer2 ? 'text-[#b00020]' : ''
          } ${showQualifierSlots && isPlaceholder2 ? 'text-[#0048ff]' : ''}`}
        >
          {label2}
        </span>
        {parsedScore?.player2 && (
          <span className="arcade-font text-[10px] min-w-[16px] text-right text-[#003e93]">
            {parsedScore.player2}
          </span>
        )}
      </div>
    </div>
  )
}
