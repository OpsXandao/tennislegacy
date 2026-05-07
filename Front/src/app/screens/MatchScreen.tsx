import { useEffect, useRef, useState, useCallback } from 'react'
import { useNavigate } from 'react-router'
import { ArrowLeft } from 'lucide-react'
import { AnimatePresence, motion } from 'motion/react'
import { NeonButton } from '../components/NeonButton'
import { FutCard } from '../components/FutCard'
import { api, ApiError } from '../../api/client'
import { useGameStore } from '../../store/gameStore'
import type { MatchStrategySummary, PlacarEvent, PlacarState } from '../../types'

// ── Types ─────────────────────────────────────────────────────────────────

type Fase =
  | 'setup'
  | 'aguardando'
  | 'jogando'
  | 'entre-games'
  | 'entre-sets'
  | 'encerrada'
  | 'pos-stats'
  | 'pos-consequencias'

type ModoAcomp = 'estrategista' | 'detalhado' | 'game' | 'auto'
type PlanoValor = 'pressionar' | 'consistencia' | 'variar'
type Faixa = 'FUNDO' | 'MEIO' | 'REDE'
type Alvo = 'ESQUERDA' | 'CENTRO' | 'DIREITA'
type SegundoSaqueModo = 'SEGURO' | 'FORCAR'
type VelocidadeRapida = 'lenta' | 'normal' | 'rapida' | 'turbo'
type MentalidadeValor = 'EQUILIBRADA' | 'OFENSIVA' | 'DEFENSIVA'
type AbordagemValor = 'BASELINE' | 'SERVE_VOLLEY' | 'COUNTER'
type InstrucaoValor = 'PADRAO' | 'FORCAR_BACKHAND' | 'TROCAS_LONGAS' | 'ATACAR_SAQUE'

interface PacoteTaticoState {
  mentalidade: MentalidadeValor
  abordagem: AbordagemValor
  instrucao: InstrucaoValor
  segundoSaque: SegundoSaqueModo
  modo: ModoAcomp
}

interface GameResult {
  quemGanhou: 'jogador' | 'adversario'
  foiBreak: boolean
  placarGames: [number, number]
}

interface AdversarioInfo {
  nome: string
  nacionalidade?: string | null
  idade?: number | null
  altura?: number | null
  peso?: number | null
  maoDominante?: string | null
  reves?: string | null
  energia: number
  fadiga: number
  ranking: number | null
  overall?: number | null
  trofeus?: Array<Record<string, unknown>>
  atributos?: Record<string, number>
  atributosPsicologicos?: Record<string, number>
  historicoTorneios?: Array<Record<string, unknown>>
  historicoPartidas?: Array<Record<string, unknown>>
  resumoFifa?: Record<string, number>
  carta?: any
  overallBoosted?: number
  atributosBoosted?: Record<string, number>
  estilo: string
}

const ESTRATEGIA_PADRAO_UI: MatchStrategySummary = {
  estilo: 'atacar_do_fundo',
  saque: 'seguro',
  saque_tipo: 'variado',
  intencao: 'paciente',
}

// ── Constants ─────────────────────────────────────────────────────────────

const PLANOS = [
  {
    valor: 'pressionar' as PlanoValor,
    label: 'PRESSIONAR',
    desc: 'Saque forte · atacar à rede',
    estilo: 'SERVE E VOLEIO',
    saque: 'AGRESSIVO',
    color: '#ff0055',
    forca: 'Encurta pontos e força erros sob pressão.',
    risco: 'Gasta mais energia e pune mal posicionamento.',
  },
  {
    valor: 'consistencia' as PlanoValor,
    label: 'CONSISTÊNCIA',
    desc: 'Rally longo · errar pouco',
    estilo: 'BASELINE',
    saque: 'SEGURO',
    color: '#00e5ff',
    forca: 'Controla o ritmo e reduz erros não forçados.',
    risco: 'Dá menos pontos grátis e depende de paciência.',
  },
  {
    valor: 'variar' as PlanoValor,
    label: 'VARIAR',
    desc: 'Mudanças de ritmo · surpresas',
    estilo: 'EQUILIBRADO',
    saque: 'VARIADO',
    color: '#ffe600',
    forca: 'Quebra padrão do rival e mistura alturas e zonas.',
    risco: 'Se executado mal, entrega iniciativa ao adversário.',
  },
] as const

const MODOS_ACOMP = [
  {
    valor: 'estrategista' as ModoAcomp,
    label: 'MANUAL',
    desc: 'Você decide ponto a ponto.',
  },
  {
    valor: 'detalhado' as ModoAcomp,
    label: 'RÁPIDA',
    desc: 'A partida avança sozinha, mas você ainda pode retomar o controle.',
  },
  {
    valor: 'auto' as ModoAcomp,
    label: 'ATÉ O FIM',
    desc: 'Simula a partida inteira no ritmo máximo.',
  },
] as const

const MODOS_VISIVEIS = MODOS_ACOMP.filter((m) => m.valor !== 'game')

const VELOCIDADES_RAPIDAS = [
  { valor: 'lenta' as VelocidadeRapida, label: '1X', desc: 'Leitura confortável', delay: 1200 },
  { valor: 'normal' as VelocidadeRapida, label: '2X', desc: 'Ritmo padrão', delay: 700 },
  { valor: 'rapida' as VelocidadeRapida, label: '4X', desc: 'Clima Brasfoot', delay: 350 },
  { valor: 'turbo' as VelocidadeRapida, label: '8X', desc: 'Máxima velocidade', delay: 150 },
] as const

const INTENCOES = [
  { valor: 'ARRISCAR', label: 'PRESSIONAR', sub: 'Winner / Ace', color: '#ff0055', emoji: '⚡' },
  { valor: 'EQUILIBRADO', label: 'CONSTRUIR', sub: 'Rally consistente', color: '#00e5ff', emoji: '◎' },
  { valor: 'DEFENSIVO', label: 'DEFENDER', sub: 'Cansar o rival', color: '#00ff88', emoji: '🛡' },
] as const

const FAIXAS: { valor: Faixa; label: string }[] = [
  { valor: 'FUNDO', label: 'FND' },
  { valor: 'MEIO', label: 'MIO' },
  { valor: 'REDE', label: 'RDE' },
]

const ALVOS: { valor: Alvo; label: string }[] = [
  { valor: 'ESQUERDA', label: 'ESQ' },
  { valor: 'CENTRO', label: 'CTR' },
  { valor: 'DIREITA', label: 'DIR' },
]

const PLACAR_INICIAL: PlacarState = {
  sets: [0, 0],
  games: [0, 0],
  pontos: ['0', '0'],
  servindo: 'jogador',
  log: [],
  encerrado: false,
}

const COURT_COLORS = { hard: '#1e3a5f', clay: '#8b3a1e', grass: '#1a4a25' } as const
type Surface = keyof typeof COURT_COLORS
const MATCH_SETTINGS_KEY = 'tennislegacy.match.tactical-package'
const MATCH_AUTOSAVE_KEY = 'tennislegacy.match.autosave'

// ── Helpers ───────────────────────────────────────────────────────────────

function normSurface(s?: string): Surface {
  const v = String(s ?? '').toLowerCase()
  if (v.includes('saibro') || v.includes('clay')) return 'clay'
  if (v.includes('grama') || v.includes('grass')) return 'grass'
  return 'hard'
}

function detectBreakPoint(p: PlacarState): string {
  const { pontos, servindo } = p
  const j = pontos[0] === '40' || pontos[0] === 'AD'
  const a = pontos[1] === '40' || pontos[1] === 'AD'
  if (servindo === 'adversario' && j && !a) return 'BREAK POINT!'
  if (servindo === 'jogador' && a && !j) return 'BREAK POINT!'
  return ''
}

function calcMomentum(p: PlacarState): number {
  const map: Record<string, number> = { '0': 0, '15': 1, '30': 2, '40': 3, AD: 4, '-': 0 }
  const sets = (p.sets[0] - p.sets[1]) * 18
  const games = (p.games[0] - p.games[1]) * 4
  const pts = ((map[p.pontos[0]] ?? 0) - (map[p.pontos[1]] ?? 0)) * 3
  return Math.max(0, Math.min(100, 50 + sets + games + pts))
}

function derivarEstrategia(
  plano: PlanoValor,
  saqueOverride?: string,
  segundoSaque: SegundoSaqueModo = 'SEGURO',
): string {
  const p = PLANOS.find(x => x.valor === plano)!
  const estilo = p.estilo
  const saque = saqueOverride || p.saque
  let estrategiaBase = 'EQUILIBRADO'
  if (estilo === 'SERVE E VOLEIO') estrategiaBase = 'SERVE E VOLEIO'
  else if (estilo === 'BASELINE') estrategiaBase = saque === 'AGRESSIVO' ? 'AGRESSIVO' : 'BASELINE'
  return `${estrategiaBase}::${segundoSaque.toLowerCase()}`
}

function inferirPlanoDoPacote(
  mentalidade: MentalidadeValor,
  abordagem: AbordagemValor,
  instrucao: InstrucaoValor,
): PlanoValor {
  if (mentalidade === 'OFENSIVA' || abordagem === 'SERVE_VOLLEY') return 'pressionar'
  if (mentalidade === 'DEFENSIVA' || abordagem === 'COUNTER' || instrucao === 'TROCAS_LONGAS') return 'consistencia'
  return 'variar'
}

function carregarPacoteTaticoInicial(): PacoteTaticoState {
  const padrao: PacoteTaticoState = {
    mentalidade: 'EQUILIBRADA',
    abordagem: 'BASELINE',
    instrucao: 'PADRAO',
    segundoSaque: 'SEGURO',
    modo: 'detalhado',
  }
  if (typeof window === 'undefined') return padrao
  try {
    const bruto = window.localStorage.getItem(MATCH_SETTINGS_KEY)
    if (!bruto) return padrao
    const salvo = JSON.parse(bruto) as Partial<PacoteTaticoState>
    return {
      mentalidade: salvo.mentalidade === 'OFENSIVA' || salvo.mentalidade === 'DEFENSIVA' ? salvo.mentalidade : 'EQUILIBRADA',
      abordagem: salvo.abordagem === 'SERVE_VOLLEY' || salvo.abordagem === 'COUNTER' ? salvo.abordagem : 'BASELINE',
      instrucao:
        salvo.instrucao === 'FORCAR_BACKHAND' || salvo.instrucao === 'TROCAS_LONGAS' || salvo.instrucao === 'ATACAR_SAQUE'
          ? salvo.instrucao
          : 'PADRAO',
      segundoSaque: salvo.segundoSaque === 'FORCAR' ? 'FORCAR' : 'SEGURO',
      modo: salvo.modo === 'estrategista' || salvo.modo === 'auto' || salvo.modo === 'game' ? salvo.modo : 'detalhado',
    }
  } catch {
    return padrao
  }
}

function carregarPreferenciaAutoSave(): boolean {
  if (typeof window === 'undefined') return false
  return window.localStorage.getItem(MATCH_AUTOSAVE_KEY) === 'true'
}

function estrategiaPonto(intencao: string, faixa: Faixa): string {
  if (faixa === 'REDE') return 'rede'
  if (intencao === 'ARRISCAR') return 'agressivo'
  if (intencao === 'DEFENSIVO') return 'defensivo'
  if (faixa === 'MEIO') return 'variado'
  return 'baseline'
}

function inferirEstilo(atributos?: Record<string, number>): string {
  if (!atributos) return 'Equilibrado'
  const saque = atributos.saque ?? 50
  const voleio = atributos.voleio ?? 50
  const winner = atributos.winner ?? 50
  const movimento = atributos.movimento ?? 50
  if (saque >= 72 && voleio >= 66) return 'Serve & Voleio'
  if (winner >= 72 && saque >= 68) return 'Agressivo'
  if (movimento >= 70) return 'Baseline'
  return 'Equilibrado'
}

function flashColor(desc: string): string {
  const d = desc.toLowerCase()
  if (d.includes('ace')) return '#00ff88'
  if (d.includes('winner')) return '#ffe600'
  if (d.includes('break')) return '#ff9900'
  if (d.includes('erro') || d.includes('falta dupla')) return '#ff0055'
  return '#00e5ff'
}

function getScoutingMetrics(adv: AdversarioInfo) {
  const atr = adv.atributos ?? {}
  const psico = adv.atributosPsicologicos ?? {}
  const resumo = adv.resumoFifa ?? {}

  const saque = Number(resumo.SAQ ?? atr.saque ?? 50)
  const fundo = Math.round(
    (
      Number(resumo.FOR ?? atr.forehand ?? 50) +
      Number(resumo.BAC ?? atr.backhand ?? 50) +
      Number(resumo.MOV ?? atr.movimento ?? 50) +
      Number(atr.winner ?? 50)
    ) / 4
  )
  const mental = Math.round(
    (
      Number(psico.concentracao ?? 50) +
      Number(psico.determinacao ?? 50) +
      Number(psico.leitura_de_jogo ?? 50)
    ) / 3
  )
  const voleio = Number(atr.voleio ?? 50)
  const winner = Number(atr.winner ?? 50)
  const movimento = Number(atr.movimento ?? 50)

  return { saque, fundo, mental, voleio, winner, movimento }
}

function getScoutingMetricsFromData(
  atributos?: Record<string, number>,
  atributosPsicologicos?: Record<string, number>,
  resumoFifa?: Record<string, number>,
) {
  const atr = atributos ?? {}
  const psico = atributosPsicologicos ?? {}
  const resumo = resumoFifa ?? {}

  const saque = Number(resumo.SAQ ?? atr.saque ?? 50)
  const fundo = Math.round(
    (
      Number(resumo.FOR ?? atr.forehand ?? 50) +
      Number(resumo.BAC ?? atr.backhand ?? 50) +
      Number(resumo.MOV ?? atr.movimento ?? 50) +
      Number(atr.winner ?? 50)
    ) / 4
  )
  const mental = Math.round(
    (
      Number(psico.concentracao ?? 50) +
      Number(psico.determinacao ?? 50) +
      Number(psico.leitura_de_jogo ?? 50)
    ) / 3
  )
  const voleio = Number(atr.voleio ?? 50)
  const winner = Number(atr.winner ?? 50)
  const movimento = Number(atr.movimento ?? 50)

  return { saque, fundo, mental, voleio, winner, movimento }
}

function calcularOverallCardMatch(metrics: {
  saque: number
  fundo: number
  mental: number
  voleio: number
  winner: number
  movimento: number
}): number {
  const valores = [metrics.saque, metrics.fundo, metrics.mental, metrics.voleio, metrics.winner, metrics.movimento]
  return Math.round(valores.reduce((acc, value) => acc + value, 0) / valores.length)
}

function accentFromCarta(carta?: { raridade?: string; tipo?: string; cor_primaria?: string | null }, fallback = '#ff4466'): string {
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

function alpha(hex: string, opacity: string): string {
  if (!hex.startsWith('#')) return hex
  const normalized = hex.length === 4
    ? `#${hex[1]}${hex[1]}${hex[2]}${hex[2]}${hex[3]}${hex[3]}`
    : hex
  return `${normalized}${opacity}`
}

function resumoModo(modo: ModoAcomp): string {
  if (modo === 'estrategista') return 'VOCÊ DECIDE CADA PONTO.'
  if (modo === 'detalhado') return 'SIMULAÇÃO RÁPIDA COM VELOCIDADE AJUSTÁVEL E PAUSA TÁTICA.'
  if (modo === 'game') return 'MODO LEGADO: PAUSA AO FIM DE CADA GAME.'
  return 'A PARTIDA INTEIRA SERÁ SIMULADA.'
}

function resumoMomentum(momentum: number): string {
  if (momentum >= 66) return 'VOCÊ ESTÁ PRESSIONANDO'
  if (momentum <= 34) return 'O ADVERSÁRIO ESTÁ MELHOR'
  return 'PARTIDA EQUILIBRADA'
}

function corMomentum(momentum: number): string {
  if (momentum >= 66) return '#00ff88'
  if (momentum <= 34) return '#ff4466'
  return '#ffe600'
}

function destaquePartida(placar: PlacarState, nomeJogador: string, nomeAdv: string, log: string[]): string {
  const sj = placar.stats_j
  const sa = placar.stats_a
  if (sj && sa) {
    const diffWinners = (sj.winners ?? 0) - (sa.winners ?? 0)
    const diffErros = (sa.erros_nao_forcados ?? 0) - (sj.erros_nao_forcados ?? 0)
    const breakJ = String(sj.break_points ?? '0/0')
    const breakA = String(sa.break_points ?? '0/0')
    if (Math.abs(diffWinners) >= 4) {
      return diffWinners > 0
        ? `${nomeJogador} desequilibrou nos winners.`
        : `${nomeAdv} impôs mais winners nos momentos-chave.`
    }
    if (Math.abs(diffErros) >= 4) {
      return diffErros > 0
        ? `${nomeJogador} errou menos e controlou a consistência da partida.`
        : `${nomeAdv} foi mais limpo nas trocas longas.`
    }
    if (breakJ !== '0/0' || breakA !== '0/0') {
      return `Break points foram decisivos: ${nomeJogador} ${breakJ} · ${nomeAdv} ${breakA}.`
    }
  }

  const ultimoMomento = [...log].reverse().find(item => item && !item.toLowerCase().includes('ponto'))
  if (ultimoMomento) return `Momento-chave: ${ultimoMomento}`
  return 'A partida foi definida pela regularidade nos momentos importantes.'
}

function tendenciaAdversario(adv: AdversarioInfo): string {
  const atributos = adv.atributos ?? {}
  const saque = atributos.saque ?? 50
  const voleio = atributos.voleio ?? 50
  const winner = atributos.winner ?? 50
  const movimento = atributos.movimento ?? 50

  if (saque >= 72 && voleio >= 66) return 'Vai encurtar pontos e buscar a rede.'
  if (winner >= 72) return 'Vai acelerar cedo e buscar winner.'
  if (movimento >= 70) return 'Deve alongar trocas no fundo.'
  return 'Perfil equilibrado, sem tendência extrema.'
}

function resumoScouting(adv: AdversarioInfo, superficie: string): { texto: string; dicas: string[]; pontosFortes: string[]; fraquezas: string[] } {
  const { saque, fundo, mental, voleio, winner, movimento } = getScoutingMetrics(adv)
  const atr = adv.atributos ?? {}
  const psico = adv.atributosPsicologicos ?? {}
  const surf = normSurface(superficie)
  
  const pontosFortes: string[] = []
  const fraquezas: string[] = []
  const dicas: string[] = []

  // --- SAQUE ---
  if (saque >= 82) {
    pontosFortes.push('CANHÃO DE SAQUE')
    dicas.push('Prepare devoluções curtas; o objetivo é apenas colocar a bola em jogo.')
    if (surf === 'grass' || surf === 'hard') dicas.push('Em quadras rápidas, ele buscará o ace em todos os pontos importantes.')
  } else if (saque >= 74) {
    pontosFortes.push('SAQUE PRECISO')
    dicas.push('Ele varia bem o alvo do saque. Não antecipe o lado da devolução.')
  } else if (saque <= 55) {
    fraquezas.push('2º SAQUE FRÁGIL')
    dicas.push('Ataque o second serve dele sem piedade; entre na quadra para punir.')
  }

  // --- FUNDO DE QUADRA & WINNERS ---
  if (fundo >= 80) {
    pontosFortes.push('MURO NO FUNDO')
    dicas.push('Ele não erra. Você precisará de ângulos curtos para tirá-lo da zona de conforto.')
    if (surf === 'clay') dicas.push('No saibro ele é uma máquina de consistência. Tente curtinhas (dropshots).')
  } 
  
  if (winner >= 78) {
    pontosFortes.push('GOLPES EXPLOSIVOS')
    dicas.push('Mantenha a bola profunda. Se der uma bola curta no meio, o ponto acaba.')
    if (psico.agressividade > 70) dicas.push('Ele arrisca muito. Se você for consistente, ele pode se autodestruir em erros.')
  } else if (winner <= 50) {
    fraquezas.push('POUCO PODER DE FOGO')
    dicas.push('Você pode subir à rede com mais segurança; ele tem dificuldade em dar passadas fortes.')
  }

  // --- MOVIMENTAÇÃO ---
  if (movimento >= 80) {
    pontosFortes.push('COBERTURA ELITE')
    dicas.push('Use o contra-pé. Ele corre tão rápido que muitas vezes não consegue frear para voltar.')
  } else if (movimento <= 58) {
    fraquezas.push('MOBILIDADE REDUZIDA')
    dicas.push('Mova-o lateralmente o tempo todo. Ele perde precisão quando precisa bater correndo.')
    if (saque >= 75) dicas.push('O plano dele é sacar e definir logo; se você devolver fundo, ele sofrerá no rally.')
  }

  // --- REDE & VARIAÇÃO ---
  if (voleio >= 75) {
    pontosFortes.push('MESTRE DO VOLEIO')
    dicas.push('Evite jogar bolas altas ou lentas quando ele estiver na rede; use o "dip" nos pés dele.')
    if (atr.slice >= 70) dicas.push('Ele usa muito o slice para preparar a subida. Esteja atento à mudança de ritmo.')
  } else if (voleio <= 50) {
    fraquezas.push('INSEGURO NA REDE')
    dicas.push('Traga-o para a rede com curtinhas; ele costuma se atrapalhar em bolas baixas perto da fita.')
  }

  // --- MENTAL & PRESSÃO ---
  if (mental >= 80) {
    pontosFortes.push('GELO NAS VEIAS')
    dicas.push('Não espere "presentes" em Match Points. Você terá que ganhar o ponto por mérito.')
  } else if (mental <= 60) {
    fraquezas.push('MENTAL OSCILANTE')
    dicas.push('Se você forçar um tiebreak ou um set longo, a confiança dele despenca.')
    if (psico.determinacao < 50) dicas.push('Ele costuma desistir mentalmente de sets se estiver uma quebra abaixo.')
  }

  // --- CONTEXTO FÍSICO ---
  if (adv.energia < 60) {
    fraquezas.push('EXAUSTÃO VISÍVEL')
    dicas.push('Alongue todos os rallies. Ele não tem pernas para um jogo de 3 sets hoje.')
  }

  // Fallback e Texto de Perfil
  if (pontosFortes.length === 0) pontosFortes.push('EQUILIBRADO')
  
  let texto = `${adv.nome} tem um perfil `;
  if (saque >= 75 && voleio >= 70) texto += "de 'Serve & Volleyer' clássico, pressionando o tempo todo.";
  else if (fundo >= 75 && movimento >= 75) texto += "de 'Counter-Puncher', uma parede impossível de ultrapassar.";
  else if (winner >= 75 && saque >= 70) texto += "agressivo, que tenta ditar o ritmo com golpes potentes.";
  else texto += "versátil, adaptando-se ao que a partida exige.";

  return { 
    texto, 
    dicas: dicas.sort(() => 0.5 - Math.random()).slice(0, 3), 
    pontosFortes: pontosFortes.slice(0, 3), 
    fraquezas: fraquezas.slice(0, 3) 
  }
}

function montarRelatorioJogador(args: {
  nome: string
  energia: number
  fadiga: number
  encaixeFisico: string
  metrics: { saque: number; fundo: number; mental: number; voleio: number; winner: number; movimento: number }
  superficie: string
}): { texto: string; dicas: string[]; pontosFortes: string[]; fraquezas: string[] } {
  const { nome, energia, fadiga, encaixeFisico, metrics, superficie } = args
  const surf = normSurface(superficie)
  const pontosFortes: string[] = []
  const fraquezas: string[] = []
  const dicas: string[] = []

  if (metrics.saque >= 78) {
    pontosFortes.push('SAQUE DE IMPACTO')
    dicas.push('Vale abrir pontos com o serviço e atacar a segunda bola.')
  } else if (metrics.saque <= 58) {
    fraquezas.push('SAQUE INSTÁVEL')
    dicas.push('Evite forçar demais o primeiro saque nos momentos de pressão.')
  }

  if (metrics.fundo >= 76) {
    pontosFortes.push('BASE FORTE')
    dicas.push('Seu melhor caminho é construir do fundo até encontrar a bola curta.')
    if (surf === 'clay') dicas.push('No saibro, alongar rallies tende a valorizar seu jogo de fundo.')
  } else if (metrics.fundo <= 58) {
    fraquezas.push('RALLY VULNERÁVEL')
    dicas.push('Busque pontos mais curtos e não aceite trocas neutras longas.')
  }

  if (metrics.voleio >= 72) {
    pontosFortes.push('TRANSIÇÃO À REDE')
    dicas.push('Há espaço para subir após golpes profundos e encurtar pontos.')
  }

  if (metrics.mental >= 76) {
    pontosFortes.push('MENTAL COMPETITIVO')
  } else if (metrics.mental <= 60) {
    fraquezas.push('PRESSÃO DECISIVA')
    dicas.push('Nos pontos grandes, priorize padrões simples e execução limpa.')
  }

  if (metrics.movimento >= 74) {
    pontosFortes.push('COBERTURA SÓLIDA')
  } else if (metrics.movimento <= 58) {
    fraquezas.push('DESLOCAMENTO EXIGIDO')
    dicas.push('Evite ficar exposto a trocas muito abertas de lado a lado.')
  }

  if (energia < 65 || fadiga >= 18 || encaixeFisico === 'BAIXO') {
    fraquezas.push('FÍSICO SOB ALERTA')
    dicas.push('Administre intensidade e escolha melhor os momentos de aceleração.')
  } else if (energia >= 85 && fadiga <= 8) {
    pontosFortes.push('PLENO FISICAMENTE')
  }

  if (pontosFortes.length === 0) pontosFortes.push('JOGO AJUSTÁVEL')

  let texto = `${nome} chega com perfil `
  if (metrics.saque >= 75 && metrics.winner >= 72) texto += 'agressivo, capaz de assumir a frente dos pontos cedo.'
  else if (metrics.fundo >= 74 && metrics.movimento >= 72) texto += 'consistente, sustentando bem trocas e cobertura de quadra.'
  else texto += 'equilibrado, com margem para adaptar o plano à partida.'

  return {
    texto,
    dicas: dicas.slice(0, 3),
    pontosFortes: pontosFortes.slice(0, 3),
    fraquezas: fraquezas.slice(0, 3),
  }
}

function leituraFisica(energia: number, fadiga: number): string {
  if (energia <= 45) return 'Estado físico comprometido.'
  if (fadiga >= 25) return 'Há desgaste acumulado importante.'
  if (energia >= 80 && fadiga <= 10) return 'Chega inteiro para a partida.'
  return 'Condição estável, mas exige gestão.'
}

function rankingValido(valor: unknown): number | null {
  const numero = Number(valor)
  if (!Number.isFinite(numero) || numero <= 0) return null
  return Math.round(numero)
}

function formatarNacionalidade(valor?: string | null): string {
  const texto = String(valor ?? '').trim()
  if (!texto) return 'Nacionalidade não informada'
  return texto
}

function resumirHistoricoRival(
  historicoPartidas?: Array<Record<string, unknown>>,
  historicoTorneios?: Array<Record<string, unknown>>
): string[] {
  if (Array.isArray(historicoPartidas) && historicoPartidas.length > 0) {
    return historicoPartidas
      .slice(-3)
      .reverse()
      .map(item => {
        const torneio = String(item.torneio ?? 'Partida')
        const fase = String(item.fase ?? '').trim()
        const resultado = String(item.resultado ?? '').trim().toUpperCase()
        const adversario = String(item.adversario ?? '').trim()
        const placar = String(item.placar ?? '').trim()
        const partes = [torneio, fase, resultado].filter(Boolean).join(' · ')
        const cauda = [adversario, placar].filter(Boolean).join(' · ')
        return cauda ? `${partes} · ${cauda}` : partes
      })
  }
  if (!Array.isArray(historicoTorneios) || historicoTorneios.length === 0) return []
  return historicoTorneios
    .slice(-3)
    .reverse()
    .map(item => {
      const nome = String(item.nome ?? item.torneio ?? 'Torneio')
      const fase = String(item.fase ?? item.resultado ?? '').trim()
      return fase ? `${nome} · ${fase}` : nome
    })
}

function resumirTitulosRival(trofeus?: Array<Record<string, unknown>>): string[] {
  if (!Array.isArray(trofeus) || trofeus.length === 0) return []
  return trofeus
    .slice(-5)
    .reverse()
    .map((item) => {
      const nome = String(item.nome ?? 'Título')
      const categoria = String(item.categoria ?? '').trim()
      const ano = String(item.ano ?? '').trim()
      return [nome, categoria, ano].filter(Boolean).join(' · ')
    })
}

function recomendacaoPlano(
  plano: (typeof PLANOS)[number],
  energia: number,
  fadiga: number,
  rival: AdversarioInfo
): string {
  const rivalAtributos = rival.atributos ?? {}
  const rivalWinner = rivalAtributos.winner ?? 50
  const rivalMovimento = rivalAtributos.movimento ?? 50

  if (plano.valor === 'pressionar') {
    if (energia >= 75 && fadiga <= 12) return 'Boa janela se você quer dominar cedo.'
    return 'Use com cuidado: seu físico precisa sustentar agressividade.'
  }
  if (plano.valor === 'consistencia') {
    if (rivalWinner >= 70) return 'Boa resposta contra rival agressivo.'
    return 'Plano seguro para estabilizar a partida.'
  }
  if (rivalMovimento >= 70) return 'Vale para tirar o rival da zona de conforto.'
  return 'Melhor quando o adversário lê bem padrões simples.'
}

function detectarPontoCritico(p: PlacarState): { label: string; color: string } | null {
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
    return { label: 'MATCH POINT', color: '#ffe600' }
  }
  if (setsA === alvoSets - 1 && gamesA === 5 && rivalEmVantagemNoPonto) {
    return { label: 'MATCH POINT CONTRA', color: '#ff0055' }
  }
  if (gamesJ === 5 && jogadorEmVantagemNoPonto) return { label: 'SET POINT', color: '#ffe600' }
  if (gamesA === 5 && rivalEmVantagemNoPonto) return { label: 'SET POINT CONTRA', color: '#ff4466' }
  const breakLabel = detectBreakPoint(p)
  if (breakLabel) return { label: breakLabel, color: '#ff9900' }
  return null
}

function serializarPacoteTatico(
  mentalidade: MentalidadeValor,
  abordagem: AbordagemValor,
  instrucao: InstrucaoValor,
  segundoSaque: SegundoSaqueModo,
): string {
  return `fm|${mentalidade}|${abordagem}|${instrucao}|${segundoSaque}`
}

function traduzirCampoEstrategia(valor?: string): string {
  const v = String(valor ?? '').trim().toLowerCase()
  if (v === 'atacar_na_rede') return 'Saque e rede'
  if (v === 'atacar_do_fundo') return 'Fundo agressivo'
  if (v === 'atacar_pelo_meio') return 'All court'
  if (v === 'forcar') return 'Forçar'
  if (v === 'seguro') return 'Seguro'
  if (v === 'agressivo') return 'Agressivo'
  if (v === 'variado') return 'Variado'
  if (v === 'arriscar') return 'Arriscar'
  if (v === 'paciente') return 'Paciente'
  if (v === 'defensivo') return 'Defensivo'
  if (v === 'ofensiva') return 'Ofensiva'
  if (v === 'equilibrada') return 'Equilibrada'
  if (v === 'serve_volley') return 'Saque e rede'
  if (v === 'baseline') return 'Baseline'
  if (v === 'counter') return 'Contra-ataque'
  if (v === 'padrao') return 'Padrão'
  if (v === 'forcar_backhand') return 'Forçar backhand'
  if (v === 'trocas_longas') return 'Trocas longas'
  if (v === 'atacar_saque') return 'Atacar 2º saque'
  return valor ? String(valor) : '--'
}

function resumirEstrategiaLado(estrategia?: MatchStrategySummary): string[] {
  const dados = { ...ESTRATEGIA_PADRAO_UI, ...(estrategia ?? {}) }
  return [
    `Estilo: ${traduzirCampoEstrategia(dados.estilo)}`,
    `Intenção: ${traduzirCampoEstrategia(dados.intencao)}`,
    `1º saque: ${traduzirCampoEstrategia(dados.saque_tipo)}`,
    `2º saque: ${traduzirCampoEstrategia(dados.saque)}`,
  ]
}

function CourtMini({
  servindo,
  faixa,
  alvo,
  intencao,
}: {
  servindo: 'jogador' | 'adversario'
  faixa: Faixa
  alvo: Alvo
  intencao: string | null
}) {
  const alvoX = alvo === 'ESQUERDA' ? '22%' : alvo === 'DIREITA' ? '78%' : '50%'
  const alvoY = faixa === 'REDE' ? '35%' : faixa === 'MEIO' ? '50%' : '66%'
  const bolaX = servindo === 'jogador' ? '38%' : '62%'
  const bolaY = servindo === 'jogador' ? '64%' : '36%'
  const intencaoColor =
    intencao === 'ARRISCAR' ? '#ffe600' : intencao === 'DEFENSIVO' ? '#00ff88' : '#00e5ff'

  return (
    <div className="border border-[#00e5ff]/25 bg-[#07121c] px-3 py-3">
      <div className="flex items-center justify-between mb-2">
        <div className="arcade-font text-[7px] text-[#6fa7b5] tracking-widest">QUADRA TÁTICA</div>
        <div className="arcade-font text-[7px] text-[#7b91a7]">
          {servindo === 'jogador' ? 'SEU SAQUE' : 'SAQUE RIVAL'}
        </div>
      </div>
      <div className="relative h-36 border border-[#7cc7d9] bg-[linear-gradient(180deg,#0f2840_0%,#11273b_45%,#0f2840_100%)] overflow-hidden">
        <div className="absolute inset-y-0 left-1/2 w-px bg-white/35 -translate-x-1/2" />
        <div className="absolute left-[12%] right-[12%] top-[16%] bottom-[16%] border border-white/40" />
        <div className="absolute left-[12%] right-[12%] top-1/2 h-px bg-white/40 -translate-y-1/2" />
        <div className="absolute left-1/2 top-[16%] bottom-[16%] w-px bg-white/30 -translate-x-1/2" />
        <div
          className="absolute h-3.5 w-3.5 -translate-x-1/2 -translate-y-1/2 border-2 border-[#00ff88] bg-[#04190e] shadow-[0_0_12px_rgba(0,255,136,0.45)]"
          style={{ left: '18%', top: '72%' }}
        />
        <div
          className="absolute h-3.5 w-3.5 -translate-x-1/2 -translate-y-1/2 border-2 border-[#ff8d6d] bg-[#28120d] shadow-[0_0_12px_rgba(255,141,109,0.4)]"
          style={{ left: '82%', top: '28%' }}
        />
        <motion.div
          className="absolute h-2.5 w-2.5 rounded-full border border-white/40"
          style={{ background: intencaoColor }}
          animate={{ left: [bolaX, alvoX], top: [bolaY, alvoY], scale: [0.9, 1.15, 1] }}
          transition={{ duration: 0.55, ease: 'easeOut' }}
        />
        <div
          className="absolute h-5 w-5 -translate-x-1/2 -translate-y-1/2 rounded-full border border-[#ffe600] bg-[#ffe60014] shadow-[0_0_18px_rgba(255,230,0,0.28)]"
          style={{ left: alvoX, top: alvoY }}
        />
      </div>
      <div className="grid grid-cols-3 gap-2 mt-2">
        <div className="border border-[#1c3140] bg-[#08121a] px-2 py-1.5">
          <div className="arcade-font text-[6px] text-[#5e7388] tracking-widest">INTENÇÃO</div>
          <div className="arcade-font text-[8px] mt-1" style={{ color: intencaoColor }}>
            {INTENCOES.find(item => item.valor === intencao)?.label ?? 'CONSTRUIR'}
          </div>
        </div>
        <div className="border border-[#1c3140] bg-[#08121a] px-2 py-1.5">
          <div className="arcade-font text-[6px] text-[#5e7388] tracking-widest">FAIXA</div>
          <div className="arcade-font text-[8px] mt-1 text-[#d6f2ff]">{faixa}</div>
        </div>
        <div className="border border-[#1c3140] bg-[#08121a] px-2 py-1.5">
          <div className="arcade-font text-[6px] text-[#5e7388] tracking-widest">ALVO</div>
          <div className="arcade-font text-[8px] mt-1 text-[#d6f2ff]">{alvo}</div>
        </div>
      </div>
    </div>
  )
}

// ── Sub-components ────────────────────────────────────────────────────────

function EnergyBar({
  label,
  value,
  color,
  inverted,
}: {
  label: string
  value: number
  color: string
  inverted?: boolean
}) {
  const safe = Math.max(0, Math.min(100, Math.round(value)))
  const barColor = inverted
    ? safe > 70 ? '#ff0055' : safe > 40 ? '#ffe600' : '#00ff88'
    : safe < 30 ? '#ff0055' : safe < 60 ? '#ffe600' : color
  return (
    <div>
      <div className="flex justify-between arcade-font text-[7px] text-[#555] mb-0.5">
        <span>{label}</span>
        <span>{safe}%</span>
      </div>
      <div className="h-1.5 bg-black border border-[#1a1a2e] overflow-hidden">
        <div
          className="h-full transition-all duration-300"
          style={{ width: `${safe}%`, background: barColor }}
        />
      </div>
    </div>
  )
}

function CircularGauge({
  label,
  value,
  color,
  track = '#14212d',
}: {
  label: string
  value: number
  color: string
  track?: string
}) {
  const safe = Math.max(0, Math.min(100, Math.round(value)))
  const radius = 27
  const circumference = 2 * Math.PI * radius
  const offset = circumference * (1 - safe / 100)

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative h-20 w-20">
        <svg className="h-20 w-20 -rotate-90" viewBox="0 0 72 72">
          <circle cx="36" cy="36" r={radius} fill="none" stroke={track} strokeWidth="6" />
          <circle
            cx="36"
            cy="36"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ filter: `drop-shadow(0 0 8px ${color})` }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className="pixel-font text-[16px]" style={{ color }}>{safe}</div>
          <div className="arcade-font text-[8px] text-[#9fb0bf]">%</div>
        </div>
      </div>
      <div className="arcade-font text-[10px] tracking-widest" style={{ color }}>
        {label}
      </div>
    </div>
  )
}

// ── Visualização da Quadra (Rally Simulator) ──────────────────────────────

function StatLine({ label, j, a }: { label: string; j: any; a: any }) {
  return (
    <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-3 arcade-font text-[13px]">
      <div className="text-[#00ff88]">{j}</div>
      <div className="text-center text-[12px] text-[#c6d8e8]">{label}</div>
      <div className="text-right text-[#ff8d6d]">{a}</div>
    </div>
  )
}

function InlineMeter({ value, color }: { value: number; color: string }) {
  const blocks = 10
  const filled = Math.round((Math.min(100, Math.max(0, value)) / 100) * blocks)
  return (
    <div className="flex gap-[2px]">
      {Array.from({ length: blocks }).map((_, i) => (
        <div
          key={i}
          className="h-[8px] flex-1"
          style={{
            background: i < filled ? color : '#1a1f27',
            boxShadow: i < filled && i === filled - 1 ? `0 0 6px ${color}` : 'none',
          }}
        />
      ))}
    </div>
  )
}

const MENTALIDADES = [
  { valor: 'DEFENSIVA', label: 'CONSERVADORA', desc: 'Foca na consistência, espera o erro.', color: '#00e5ff', emoji: '🧱' },
  { valor: 'EQUILIBRADA', label: 'EQUILIBRADA', desc: 'Padrão moderno de trocas.', color: '#00ff88', emoji: '⚖️' },
  { valor: 'OFENSIVA', label: 'AGRESSIVA', desc: 'Busca winners e encurta pontos.', color: '#ff4466', emoji: '🔥' },
] as const

const ABORDAGENS = [
  { valor: 'BASELINE', label: 'BASE-LINER', desc: 'Trocas pesadas do fundo.', icon: '🎾' },
  { valor: 'SERVE_VOLLEY', label: 'SAQUE E REDE', desc: 'Agressão máxima na rede.', icon: '👟' },
  { valor: 'COUNTER', label: 'CONTRA-ATAQUE', desc: 'Usa a força do rival.', icon: '🛡️' },
] as const

const INSTRUCOES = [
  { valor: 'PADRAO', label: 'PADRÃO', desc: 'Sem ordens específicas.', emoji: '•' },
  { valor: 'FORCAR_BACKHAND', label: 'FORÇAR BACKHAND', desc: 'Ataca o lado mais fraco.', emoji: '↙️' },
  { valor: 'TROCAS_LONGAS', label: 'TROCAS LONGAS', desc: 'Desgasta o físico do rival.', emoji: '🔁' },
  { valor: 'ATACAR_SAQUE', label: 'ATACAR 2º SAQUE', desc: 'Pressão na devolução.', emoji: '🎯' },
] as const

function TacticalPackageEditor({
  mentalidade,
  abordagem,
  instrucao,
  segundoSaque,
  setMentalidade,
  setAbordagem,
  setInstrucao,
  setSegundoSaque,
  compact = false,
}: {
  mentalidade: MentalidadeValor
  abordagem: AbordagemValor
  instrucao: InstrucaoValor
  segundoSaque: SegundoSaqueModo
  setMentalidade: (valor: MentalidadeValor) => void
  setAbordagem: (valor: AbordagemValor) => void
  setInstrucao: (valor: InstrucaoValor) => void
  setSegundoSaque: (valor: SegundoSaqueModo) => void
  compact?: boolean
}) {
  const sectionLabel = compact ? 'text-[9px]' : 'text-[10px]'
  const itemLabel = compact ? 'text-[10px]' : 'text-[11px]'
  const itemDesc = compact ? 'text-[8px]' : 'text-[9px]'
  const buttonPadding = compact ? 'p-2.5' : 'p-3'
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <div className={`arcade-font ${sectionLabel} text-[#8fa3b5] mb-2 tracking-widest uppercase`}>Mentalidade</div>
        <div className="space-y-2">
          {MENTALIDADES.map(m => (
            <button
              key={m.valor}
              onClick={() => setMentalidade(m.valor)}
              className={`w-full ${buttonPadding} border-2 text-left flex items-center justify-between transition-all`}
              style={{
                borderColor: mentalidade === m.valor ? m.color : '#1a1a2e',
                background: mentalidade === m.valor ? `${m.color}15` : 'transparent',
                boxShadow: mentalidade === m.valor ? `0 0 15px ${m.color}20` : 'none',
              }}
            >
              <div className="flex items-center gap-3">
                <span className={compact ? 'text-base' : 'text-lg'}>{m.emoji}</span>
                <div>
                  <div className={`arcade-font ${itemLabel}`} style={{ color: mentalidade === m.valor ? m.color : '#d6e0ea' }}>{m.label}</div>
                  <div className={`arcade-font ${itemDesc} text-[#8ea3b7]`}>{m.desc}</div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div>
        <div className={`arcade-font ${sectionLabel} text-[#8fa3b5] mb-2 tracking-widest uppercase`}>Abordagem</div>
        <div className="space-y-2">
          {ABORDAGENS.map(a => (
            <button
              key={a.valor}
              onClick={() => setAbordagem(a.valor)}
              className={`w-full ${buttonPadding} border-2 text-left flex items-center justify-between transition-all`}
              style={{
                borderColor: abordagem === a.valor ? '#ffe600' : '#1a1a2e',
                background: abordagem === a.valor ? '#ffe6000a' : 'transparent',
              }}
            >
              <div className="flex items-center gap-3">
                <span className={compact ? 'text-base' : 'text-lg'}>{a.icon}</span>
                <div>
                  <div className={`arcade-font ${itemLabel}`} style={{ color: abordagem === a.valor ? '#ffe600' : '#d6e0ea' }}>{a.label}</div>
                  <div className={`arcade-font ${itemDesc} text-[#9fb0bf]`}>{a.desc}</div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div>
        <div className={`arcade-font ${sectionLabel} text-[#8fa3b5] mb-2 tracking-widest uppercase`}>Instrução Específica</div>
        <div className="space-y-2">
          {INSTRUCOES.map(i => (
            <button
              key={i.valor}
              onClick={() => setInstrucao(i.valor)}
              className={`w-full ${buttonPadding} border-2 text-left transition-all`}
              style={{
                borderColor: instrucao === i.valor ? '#00ff88' : '#1a1a2e',
                background: instrucao === i.valor ? '#00ff880a' : 'transparent',
              }}
            >
              <div className="flex items-center gap-3">
                <span className={compact ? 'text-sm' : 'text-base'}>{i.emoji}</span>
                <div>
                  <div className={`arcade-font ${itemLabel}`} style={{ color: instrucao === i.valor ? '#00ff88' : '#d6e0ea' }}>{i.label}</div>
                  <div className={`arcade-font ${itemDesc} text-[#9fb0bf] mt-1`}>{i.desc}</div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div>
        <div className={`arcade-font ${sectionLabel} text-[#8fa3b5] mb-2 tracking-widest uppercase`}>Segundo Saque</div>
        <div className="space-y-2">
          {([
            {
              valor: 'SEGURO' as SegundoSaqueModo,
              label: '🛡️ SEGURO',
              desc: 'Menos dupla falta, menos pressão imediata.',
              color: '#00ff88',
            },
            {
              valor: 'FORCAR' as SegundoSaqueModo,
              label: '⚡ FORÇAR',
              desc: 'Mais agressão no 2º saque, com risco maior.',
              color: '#ffe600',
            },
          ]).map((opcao) => (
            <button
              key={opcao.valor}
              onClick={() => setSegundoSaque(opcao.valor)}
              className={`w-full border px-3 ${compact ? 'py-2.5' : 'py-3'} text-left transition-all`}
              style={{
                borderColor: segundoSaque === opcao.valor ? opcao.color : '#1a1a2e',
                background: segundoSaque === opcao.valor ? `${opcao.color}10` : 'transparent',
              }}
            >
              <div className={`arcade-font ${itemLabel}`} style={{ color: segundoSaque === opcao.valor ? opcao.color : '#d6e0ea' }}>
                {opcao.label}
              </div>
              <div className={`arcade-font ${itemDesc} text-[#9fb0bf] mt-1`}>{opcao.desc}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

function ScoutingReport({
  titulo,
  overall,
  metrics,
  report,
  accent,
}: {
  titulo: string
  overall: number | null | undefined
  metrics: { saque: number; fundo: number; mental: number }
  report: ReturnType<typeof resumoScouting>
  accent: string
}) {
  const stats = [
    { label: 'Saque', val: metrics.saque },
    { label: 'Fundo', val: metrics.fundo },
    { label: 'Mental', val: metrics.mental },
  ]

  return (
    <div className="border p-4 space-y-4" style={{ borderColor: `${accent}40`, background: `${accent}0a` }}>
      <div className="flex items-center justify-between border-b pb-2" style={{ borderColor: `${accent}20` }}>
        <div className="arcade-font text-[11px] tracking-widest uppercase" style={{ color: accent }}>{titulo}</div>
        <div className="pixel-font text-[14px] text-white">OVR {overall ?? '??'}</div>
      </div>

      <div className="grid grid-cols-3 gap-2">
        {stats.map(s => (
          <div key={s.label} className="text-center bg-black/40 p-1.5 border" style={{ borderColor: `${accent}20` }}>
            <div className="arcade-font text-[9px] text-[#888] mb-1">{s.label.toUpperCase()}</div>
            <div className="pixel-font text-[15px]" style={{ color: s.val > 80 ? '#00ff88' : s.val > 65 ? '#ffe600' : '#ff4466' }}>{s.val}</div>
          </div>
        ))}
      </div>

      <div className="space-y-3">
        {/* Tags de Análise */}
        <div className="flex flex-wrap gap-1.5">
          {report.pontosFortes.map(tag => (
            <span key={tag} className="arcade-font text-[7px] px-1.5 py-0.5 bg-[#00ff88]/10 text-[#00ff88] border border-[#00ff88]/20">
              {tag}
            </span>
          ))}
          {report.fraquezas.map(tag => (
            <span key={tag} className="arcade-font text-[7px] px-1.5 py-0.5 bg-[#ff4466]/10 text-[#ff4466] border border-[#ff4466]/20">
              {tag}
            </span>
          ))}
        </div>

        {/* Resumo e Dicas */}
        <div className="space-y-2">
          <div className="arcade-font text-[10px] text-white/80 leading-relaxed">
            {report.texto}
          </div>
          {report.dicas.length > 0 && (
            <div className="bg-[#ffe600]/5 border-l-2 border-[#ffe600] p-2 space-y-1">
              <div className="arcade-font text-[8px] text-[#ffe600] tracking-widest">DICA TÁTICA</div>
              {report.dicas.map((dica, idx) => (
                <div key={idx} className="arcade-font text-[9px] text-[#d6f2ff] leading-snug">
                  • {dica}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function OpponentScouting({ adv, accent, superficie }: { adv: AdversarioInfo; accent: string; superficie: string }) {
  const { saque, fundo, mental } = getScoutingMetrics(adv)
  const report = resumoScouting(adv, superficie)
  return (
    <ScoutingReport
      titulo="Scouting Report"
      overall={calcularOverallCardMatch(getScoutingMetrics(adv))}
      metrics={{ saque, fundo, mental }}
      report={report}
      accent={accent}
    />
  )
}

// ── Main Component ────────────────────────────────────────────────────────

export function MatchScreen() {
  const navigate = useNavigate()
  const { jogador, saveAtivo, setJogador, setPartidaId, setSemana, setTorneio, fetchJogador, ano } = useGameStore()
  const nomeJogador = jogador?.nome ?? 'VOCÊ'
  const pacoteInicial = carregarPacoteTaticoInicial()

  // FM-style tactical state
  const [mentalidade, setMentalidade] = useState<MentalidadeValor>(pacoteInicial.mentalidade)
  const [abordagem, setAbordagem] = useState<AbordagemValor>(pacoteInicial.abordagem)
  const [instrucao, setInstrucao] = useState<InstrucaoValor>(pacoteInicial.instrucao)
  const mentalidadeAtual = MENTALIDADES.find(m => m.valor === mentalidade) ?? MENTALIDADES[1]
  const abordagemAtual = ABORDAGENS.find(a => a.valor === abordagem) ?? ABORDAGENS[0]
  const instrucaoAtual = INSTRUCOES.find(i => i.valor === instrucao) ?? INSTRUCOES[0]

  // Core
  const [fase, setFase] = useState<Fase>('setup')
  const [placar, setPlacar] = useState<PlacarState>(PLACAR_INICIAL)
  const [simulando, setSimulando] = useState(false)
  const [simulacaoPausada, setSimulacaoPausada] = useState(false)
  const [velocidadeRapida, setVelocidadeRapida] = useState<VelocidadeRapida>('rapida')
  const [ajustandoPlanoRapido, setAjustandoPlanoRapido] = useState(false)

  // Setup decisions
  const [plano, setPlano] = useState<PlanoValor>(() => inferirPlanoDoPacote(pacoteInicial.mentalidade, pacoteInicial.abordagem, pacoteInicial.instrucao))
  const [modo, setModo] = useState<ModoAcomp>(pacoteInicial.modo)
  const [segundoSaque, setSegundoSaque] = useState<SegundoSaqueModo>(pacoteInicial.segundoSaque)
  const [confirmandoEntrada, setConfirmandoEntrada] = useState(false)
  const [abaRival, setAbaRival] = useState<'registros' | 'historia'>('registros')
  const [abaJogador, setAbaJogador] = useState<'registros' | 'historia'>('registros')

  // Per-point (estrategista)
  const [faixa, setFaixa] = useState<Faixa>('FUNDO')
  const [alvo, setAlvo] = useState<Alvo>('CENTRO')
  const [intencaoAtiva, setIntencaoAtiva] = useState<string | null>(null)
  const [expandirPonto, setExpandirPonto] = useState(false)

  // Match info
  const [adversario, setAdversario] = useState<AdversarioInfo>({
      nome: 'ADVERSÁRIO',
      nacionalidade: null,
      energia: 100,
      fadiga: 0,
      ranking: null,
      overall: null,
      trofeus: [],
      historicoTorneios: [],
      historicoPartidas: [],
      estilo: 'Equilibrado',
  })
  const [energiaJogadorAoVivo, setEnergiaJogadorAoVivo] = useState(100)
  const [fadigaJogadorAoVivo, setFadigaJogadorAoVivo] = useState(0)
  const [energiaAdversarioAoVivo, setEnergiaAdversarioAoVivo] = useState(100)
  const [fadigaAdversarioAoVivo, setFadigaAdversarioAoVivo] = useState(0)
  const [estrategiaJogadorAoVivo, setEstrategiaJogadorAoVivo] = useState<MatchStrategySummary>(ESTRATEGIA_PADRAO_UI)
  const [estrategiaAdversarioAoVivo, setEstrategiaAdversarioAoVivo] = useState<MatchStrategySummary>(ESTRATEGIA_PADRAO_UI)
  const [partidaId, setInternalPartidaId] = useState<string | null>(null)
  const [superficie, setSuperficie] = useState('')
  const [faseTorneio, setFaseTorneio] = useState('')
  const [log, setLog] = useState<string[]>([])
  const [erroEntrada, setErroEntrada] = useState('')
  const [autoSaveAtivo] = useState<boolean>(() => carregarPreferenciaAutoSave())

  // Feedback
  const [flashPonto, setFlashPonto] = useState<{ texto: string; color: string } | null>(null)
  const [alertaBreak, setAlertaBreak] = useState('')

  // Between game/set
  const [gameResult, setGameResult] = useState<GameResult | null>(null)
  const [ajustandoPlanoGame, setAjustandoPlanoGame] = useState(false)
  const [ajustandoPlanoSet, setAjustandoPlanoSet] = useState(false)
  const [contadorSet, setContadorSet] = useState(10)
  const encaixeFisico =
    energiaJogadorAoVivo >= 75 && fadigaJogadorAoVivo <= 10
      ? 'ALTO'
      : energiaJogadorAoVivo >= 55
        ? 'MÉDIO'
        : 'BAIXO'
  const riscoTatico =
    mentalidade === 'OFENSIVA' && abordagem === 'SERVE_VOLLEY'
      ? 'ALTO'
      : mentalidade === 'DEFENSIVA' && instrucao === 'PADRAO'
        ? 'BAIXO'
        : 'MÉDIO'
  const planoExecutivo =
    `${mentalidadeAtual.label} com ${abordagemAtual.label.toLowerCase()} e ${instrucaoAtual.label.toLowerCase()}.`

  // Post-match
  const [jogadorPosjogo, setJogadorPosjogo] = useState<any>(null)
  const jogadorAntesRef = useRef<{ xp: number; ranking: number; nivel: number } | null>(null)

  const lastPlacar = useRef<PlacarState>(PLACAR_INICIAL)
  const modoRef = useRef<ModoAcomp>(modo)
  const partidaAutoSavePerguntadaRef = useRef<string | null>(null)
  useEffect(() => { modoRef.current = modo }, [modo])
  useEffect(() => {
    setEnergiaJogadorAoVivo(Number(jogador?.energia ?? 100))
    setFadigaJogadorAoVivo(Number(jogador?.fadiga ?? 0))
  }, [jogador?.energia, jogador?.fadiga])
  useEffect(() => {
    setEnergiaAdversarioAoVivo(Number(adversario.energia ?? 100))
    setFadigaAdversarioAoVivo(Number(adversario.fadiga ?? 0))
  }, [adversario.energia, adversario.fadiga])
  useEffect(() => {
    setPlano(inferirPlanoDoPacote(mentalidade, abordagem, instrucao))
  }, [mentalidade, abordagem, instrucao])
  useEffect(() => {
    if (typeof window === 'undefined') return
    window.localStorage.setItem(
      MATCH_SETTINGS_KEY,
      JSON.stringify({ mentalidade, abordagem, instrucao, segundoSaque, modo }),
    )
  }, [mentalidade, abordagem, instrucao, segundoSaque, modo])

  const planoAtual = PLANOS.find(p => p.valor === plano)!

  // ─── Init ────────────────────────────────────────────────────────────────

  useEffect(() => {
    let ativo = true

    fetchJogador()
      .then((jAtualizado) => {
        if (!ativo) return
        jogadorAntesRef.current = {
          xp: jAtualizado.xp,
          ranking: jAtualizado.ranking,
          nivel: jAtualizado.nivel,
        }
      })
      .catch(() => {
        if (!ativo || !jogador) return
        jogadorAntesRef.current = {
          xp: jogador.xp,
          ranking: jogador.ranking,
          nivel: jogador.nivel,
        }
      })

    api.partida.ativa().then((res) => {
      if (!ativo || !res?.partida_id) return
      setInternalPartidaId(res.partida_id)
      setPartidaId(res.partida_id)
      const m = (res.config.modo as ModoAcomp) || 'estrategista'
      setModo(m)
      if ((res as any).adversario) applyAdversario((res as any).adversario)
      if (res.placar) {
        setPlacar(res.placar)
        lastPlacar.current = res.placar
      }
      setFase('aguardando')
    }).catch(async (e) => {
      // Sessão perdida (backend reiniciou) — tenta restaurar silenciosamente
      if (e instanceof ApiError && e.status === 400 && saveAtivo) {
        try {
          const r = await api.saves.carregar(saveAtivo)
          if (r.ok) setJogador(r.jogador)
        } catch {
          // fica no setup normalmente
        }
      }
    })

    return () => {
      ativo = false
    }
  }, [fetchJogador, saveAtivo, setJogador, setPartidaId])

  // Load adversário name from torneio for setup screen
  useEffect(() => {
    if (fase !== 'setup') return
    api.torneio.estado().then((t) => {
      if (!t) return
      setSuperficie(t.superficie ?? '')
      setFaseTorneio(String((t as any).fase ?? (t as any).fase_atual ?? ''))
      if (t.info_partida) {
        const meu = nomeJogador.trim().toLowerCase()
        const j1 = t.info_partida.jogador1
        const j2 = t.info_partida.jogador2
        const nomeAdv = j1.trim().toLowerCase() === meu ? j2 : j1
        if ((t.info_partida as any).adversario) {
          applyAdversario((t.info_partida as any).adversario)
        } else {
          setAdversario(prev => ({ ...prev, nome: nomeAdv }))
        }
      }
    }).catch(() => {})
    api.partida.preview().then((res) => {
      if (res?.adversario) applyAdversario(res.adversario)
    }).catch(() => {})
  }, [fase, nomeJogador])

  // Auto-play: game-a-game mode
  useEffect(() => {
    if (modo !== 'game') return
    if (fase !== 'aguardando' || simulando || placar.encerrado || !partidaId) return
    const t = setTimeout(handleSimularGame, 350)
    return () => clearTimeout(t)
  }, [modo, fase, simulando, placar.encerrado, partidaId])

  useEffect(() => {
    if (modo !== 'detalhado') return
    if (simulacaoPausada) return
    if (fase !== 'aguardando' || simulando || placar.encerrado || !partidaId) return
    const delay = VELOCIDADES_RAPIDAS.find((item) => item.valor === velocidadeRapida)?.delay ?? 350
    const t = setTimeout(handleProximoPonto, delay)
    return () => clearTimeout(t)
  }, [modo, fase, simulando, placar.encerrado, partidaId, simulacaoPausada, velocidadeRapida])

  useEffect(() => {
    if (!partidaId || fase === 'setup' || placar.encerrado) return
    if (partidaAutoSavePerguntadaRef.current === partidaId) return
    partidaAutoSavePerguntadaRef.current = partidaId

    if (autoSaveAtivo) {
      api.saves.salvar().catch((err) => {
        console.error("Auto-save falhou:", err)
      })
    }
  }, [autoSaveAtivo, fase, partidaId, placar.encerrado])

  // Fetch post-match player state
  const isMounted = useRef(true)
  useEffect(() => {
    isMounted.current = true
    return () => { isMounted.current = false }
  }, [])

  useEffect(() => {
    if (fase !== 'encerrada') return
    api.jogador.get().then((res) => {
      if (isMounted.current) setJogadorPosjogo(res)
    }).catch((err) => {
      console.error("Erro ao buscar jogador pós-jogo:", err)
    })
  }, [fase])

  useEffect(() => {
    if (fase !== 'encerrada') return
    const timer = window.setTimeout(() => {
      if (isMounted.current) setFase('pos-stats')
    }, 2600)
    return () => window.clearTimeout(timer)
  }, [fase])

  // Countdown timer entre sets — auto-continua em 0
  const continuarSetRef = useRef<() => void>(() => {})
  useEffect(() => {
    continuarSetRef.current = () => {
      if (!isMounted.current) return
      setGameResult(null)
      setAjustandoPlanoSet(false)
      if (partidaId) {
        const est = serializarPacoteTatico(mentalidade, abordagem, instrucao, segundoSaque)
        api.partida.ajusteTatico(partidaId, est, placar.sets[0] + placar.sets[1]).catch((err) => {
          console.error("Erro ao aplicar ajuste tático:", err)
        })
      }
      setFase('aguardando')
    }
  })

  useEffect(() => {
    if (fase !== 'entre-sets') {
      setContadorSet(10)
      return
    }
    setContadorSet(10)
    const id = window.setInterval(() => {
      if (!isMounted.current) {
        window.clearInterval(id)
        return
      }
      setContadorSet((c) => {
        if (c <= 1) {
          window.clearInterval(id)
          continuarSetRef.current()
          return 0
        }
        return c - 1
      })
    }, 1000)
    return () => window.clearInterval(id)
  }, [fase])

  // ─── Session recovery ─────────────────────────────────────────────────────

  async function tentarRestaurarSessao(): Promise<boolean> {
    if (!saveAtivo) return false
    try {
      const r = await api.saves.carregar(saveAtivo)
      if (r.ok) {
        setJogador(r.jogador)
        return true
      }
    } catch {
      // ignora
    }
    return false
  }

  async function reaproveitarPartidaAtiva(): Promise<boolean> {
    try {
      const ativa = await api.partida.ativa()
      if (!ativa?.partida_id) return false
      setInternalPartidaId(ativa.partida_id)
      setPartidaId(ativa.partida_id)
      const m = (ativa.config.modo as ModoAcomp) || 'estrategista'
      setModo(m)
      if ((ativa as any).adversario) applyAdversario((ativa as any).adversario)
      if (ativa.placar) {
        aplicar(ativa.placar)
      } else {
        setFase('aguardando')
      }
      return true
    } catch {
      return false
    }
  }

  // ─── Helpers ─────────────────────────────────────────────────────────────

  function applyAdversario(adv: any) {
    if (!adv) return
    setAdversario({
      nome: adv.nome || 'ADVERSÁRIO',
      nacionalidade: adv.nacionalidade ?? null,
      idade: Number(adv.idade ?? 0) || null,
      altura: Number(adv.altura ?? 0) || null,
      peso: Number(adv.peso ?? 0) || null,
      maoDominante: adv.mao_dominante ?? null,
      reves: adv.reves ?? null,
      energia: Number(adv.energia ?? 100),
      fadiga: Number(adv.fadiga ?? 0),
      ranking: adv.ranking ?? adv.ranking_pos ?? null,
      overall: Number(adv.overall ?? adv.atributos?.overall ?? 0) || null,
      trofeus: Array.isArray(adv.trofeus) ? adv.trofeus : [],
      atributos: adv.atributos,
      atributosPsicologicos: adv.atributos_psicologicos,
      historicoTorneios: Array.isArray(adv.historico_torneios) ? adv.historico_torneios : [],
      historicoPartidas: Array.isArray(adv.historico_partidas) ? adv.historico_partidas : [],
      resumoFifa: adv.resumo_fifa,
      carta: adv.carta,
      overallBoosted: adv.carta?.overall_boosted,
      atributosBoosted: adv.carta?.atributos_boosted,
      estilo: adv.estilo_jogo ?? inferirEstilo(adv.atributos),
    })
    setEnergiaJogadorAoVivo(Number(jogador?.energia ?? 100))
    setFadigaJogadorAoVivo(Number(jogador?.fadiga ?? 0))
    setEnergiaAdversarioAoVivo(Number(adv.energia ?? 100))
    setFadigaAdversarioAoVivo(Number(adv.fadiga ?? 0))
  }

  // ─── Apply placar update ──────────────────────────────────────────────────

  const aplicar = useCallback((estado: PlacarEvent | PlacarState) => {
    const desc = ('descricao' in estado ? estado.descricao : '') || ''
    const tipo = ('tipo' in estado ? estado.tipo : '') as string

    const prevGames: [number, number] = [lastPlacar.current.games[0], lastPlacar.current.games[1]]
    const prevServindo = lastPlacar.current.servindo

    setPlacar(estado)
    lastPlacar.current = estado
    if ('energia_j' in estado && typeof (estado as any).energia_j === 'number') {
      setEnergiaJogadorAoVivo(Number((estado as any).energia_j))
    }
    if ('fadiga_j' in estado && typeof (estado as any).fadiga_j === 'number') {
      setFadigaJogadorAoVivo(Number((estado as any).fadiga_j))
    }
    if ('estrategia_j' in estado && (estado as any).estrategia_j) {
      setEstrategiaJogadorAoVivo((estado as any).estrategia_j as MatchStrategySummary)
    }
    if ('estrategia_a' in estado && (estado as any).estrategia_a) {
      setEstrategiaAdversarioAoVivo((estado as any).estrategia_a as MatchStrategySummary)
    }
    if ('energia_a' in estado || 'fadiga_a' in estado) {
      if (typeof (estado as any).energia_a === 'number') {
        setEnergiaAdversarioAoVivo(Number((estado as any).energia_a))
      }
      if (typeof (estado as any).fadiga_a === 'number') {
        setFadigaAdversarioAoVivo(Number((estado as any).fadiga_a))
      }
      setAdversario(prev => ({
        ...prev,
        energia: typeof (estado as any).energia_a === 'number' ? Number((estado as any).energia_a) : prev.energia,
        fadiga: typeof (estado as any).fadiga_a === 'number' ? Number((estado as any).fadiga_a) : prev.fadiga,
      }))
    }
    if (desc) setLog(p => [...p, desc].slice(-80))
    setAlertaBreak(detectBreakPoint(estado))

    // Point flash (only for individual pontos)
    if (desc && tipo === 'ponto') {
      const color = flashColor(desc)
      setFlashPonto({ texto: desc, color })
      setTimeout(() => setFlashPonto(null), 2200)
    }

    if (estado.encerrado) {
      setFase('encerrada')
      return
    }

    if (tipo === 'set') {
      setGameResult(null)
      setAjustandoPlanoSet(false)
      setFase('entre-sets')
      return
    }

    if (tipo === 'game') {
      const jogadorGanhouGame = estado.games[0] > prevGames[0]
      const quemGanhou: 'jogador' | 'adversario' = jogadorGanhouGame ? 'jogador' : 'adversario'
      const foiBreak = jogadorGanhouGame
        ? prevServindo === 'adversario'
        : prevServindo === 'jogador'

      setGameResult({ quemGanhou, foiBreak, placarGames: estado.games })
      setAjustandoPlanoGame(false)

      if (modoRef.current === 'auto' || modoRef.current === 'detalhado') {
        setFase('aguardando')
      } else {
        setFase('entre-games')
      }
      return
    }

    if (!estado.encerrado) setFase('aguardando')
  }, [])

  // ─── Handlers ────────────────────────────────────────────────────────────

  async function handleIniciar() {
    if (!confirmandoEntrada) {
      setConfirmandoEntrada(true)
      setErroEntrada('')
      return
    }

    setSimulando(true)
    setErroEntrada('')
    try {
      if (await reaproveitarPartidaAtiva()) {
        return
      }

      if (modo === 'auto') {
        const r = await api.partida.iniciar('rapido')
        setInternalPartidaId(r.partida_id)
        setPartidaId(r.partida_id)
        if ((r as any).adversario) applyAdversario((r as any).adversario)
        if (r.placar) {
          aplicar({ ...r.placar, tipo: 'setup' as any, descricao: '' } as any)
        }
        await api.partida.estrategia(
          r.partida_id,
          serializarPacoteTatico(mentalidade, abordagem, instrucao, segundoSaque),
        ).catch(() => {})
        const estado = await api.partida.simularPartida(r.partida_id)
        aplicar({ ...estado, tipo: 'fim' as any, descricao: '' } as any)
        return
      }

      const apiModo = modo === 'estrategista' ? 'estrategista' : 'rapido'
      const r = await api.partida.iniciar(apiModo)
      setInternalPartidaId(r.partida_id)
      setPartidaId(r.partida_id)
      if ((r as any).adversario) applyAdversario((r as any).adversario)
      if (r.placar) {
        aplicar({ ...r.placar, tipo: 'setup' as any, descricao: '' } as any)
      }
      await api.partida.estrategia(
        r.partida_id,
        serializarPacoteTatico(mentalidade, abordagem, instrucao, segundoSaque),
      ).catch(() => {})
      setFase('aguardando')
    } catch (e) {
      if (e instanceof ApiError && e.status === 400) {
        const restaurou = await tentarRestaurarSessao()
        if (restaurou) {
          setSimulando(false)
          handleIniciar()
          return
        }
        navigate('/')
        return
      }
      if (await reaproveitarPartidaAtiva()) {
        return
      }
      setErroEntrada('Nao foi possivel iniciar a partida.')
      console.error(e)
    } finally {
      setSimulando(false)
    }
  }

  async function handleIntencao(intencao: string) {
    if (!partidaId || fase !== 'aguardando') return
    setIntencaoAtiva(intencao)
    setFase('jogando')
    setSimulando(true)
    setAlertaBreak('')
    try {
      await api.partida.estrategia(partidaId, estrategiaPonto(intencao, faixa)).catch(() => {})
      const estado = await api.partida.ponto(partidaId)
      aplicar(estado)
    } catch {
      setFase('aguardando')
    } finally {
      setSimulando(false)
      setIntencaoAtiva(null)
    }
  }

  async function handleProximoPonto() {
    if (!partidaId || fase !== 'aguardando') return
    setFase('jogando')
    setSimulando(true)
    try {
      const estado = await api.partida.ponto(partidaId)
      aplicar(estado)
    } catch {
      setFase('aguardando')
    } finally {
      setSimulando(false)
    }
  }

  async function handleSimularGame() {
    if (!partidaId) return
    setFase('jogando')
    setSimulando(true)
    try {
      let finalEstado: PlacarEvent | null = null
      while (true) {
        const estado = await api.partida.ponto(partidaId) as PlacarEvent
        const tipo = estado.tipo
        if (tipo === 'game' || tipo === 'set' || tipo === 'fim' || estado.encerrado) {
          finalEstado = estado
          break
        }
        // Update ref so game detection works at the end
        lastPlacar.current = estado
      }
      if (finalEstado) aplicar(finalEstado)
    } catch {
      setFase('aguardando')
    } finally {
      setSimulando(false)
    }
  }

  async function handleSimularSet() {
    if (!partidaId) return
    setFase('jogando')
    setSimulando(true)
    try {
      const estado = await api.partida.simularSet(partidaId)
      aplicar({ ...estado, tipo: estado.encerrado ? 'fim' : 'set', descricao: '' } as any)
    } catch {
      setFase('aguardando')
    } finally {
      setSimulando(false)
    }
  }

  async function aplicarEstrategiaAtual() {
    if (!partidaId) return
    const est = serializarPacoteTatico(mentalidade, abordagem, instrucao, segundoSaque)
    await api.partida.estrategia(partidaId, est).catch(err => console.error("Erro ao aplicar estratégia:", err))
  }

  async function handleContinuarGame() {
    if (partidaId) {
      await aplicarEstrategiaAtual()
    }
    setAjustandoPlanoGame(false)
    setGameResult(null)
    setFase('aguardando')
  }

  async function handleContinuarSet() {
    setGameResult(null)
    setAjustandoPlanoSet(false)
    if (partidaId) {
      const est = serializarPacoteTatico(mentalidade, abordagem, instrucao, segundoSaque)
      await api.partida.ajusteTatico(partidaId, est, placar.sets[0] + placar.sets[1]).catch(err => console.error("Ajuste tático falhou:", err))
    }
    setFase('aguardando')
  }

  async function handleEscolherPlanoSet(plano: PlanoValor) {
    const mapa: Record<PlanoValor, { m: MentalidadeValor; a: AbordagemValor; i: InstrucaoValor }> = {
      pressionar: { m: 'OFENSIVA', a: 'SERVE_VOLLEY', i: 'PADRAO' },
      consistencia: { m: 'DEFENSIVA', a: 'BASELINE', i: 'TROCAS_LONGAS' },
      variar: { m: 'EQUILIBRADA', a: 'BASELINE', i: 'PADRAO' },
    }
    const { m, a, i } = mapa[plano]
    setMentalidade(m)
    setAbordagem(a)
    setInstrucao(i)
    const est = serializarPacoteTatico(m, a, i, segundoSaque)
    if (partidaId) {
      await api.partida.ajusteTatico(partidaId, est, placar.sets[0] + placar.sets[1]).catch(err => console.error("Ajuste tático falhou:", err))
    }
    setGameResult(null)
    setAjustandoPlanoSet(false)
    setFase('aguardando')
  }

  async function handleAplicarPausaRapida() {
    await aplicarEstrategiaAtual()
    setAjustandoPlanoRapido(false)
    setSimulacaoPausada(false)
    setFase('aguardando')
  }

  async function handleDesistir() {
    if (!partidaId) return
    if (!window.confirm('Tem certeza? Isso resultará em derrota por W.O.')) return
    try {
      await api.partida.desistir(partidaId)
      navigate('/tournament')
    } catch (e) {
      console.error(e)
    }
  }

  async function handleContinuarPosJogo() {
    try {
      const torneioAtual = await api.torneio.estado().catch(() => null)
      if (torneioAtual?.fase_atual === 'finalizado') {
        const resultado = await api.calendario.avancar()
        setSemana(resultado.semana, resultado.ano ?? ano)
        await fetchJogador().catch(() => {})
        setTorneio(null)
        setPartidaId(null)
        navigate('/hub')
        return
      }

      if (torneioAtual) {
        setTorneio(torneioAtual)
      }
    } catch {
      // Se falhar o avanço automático, mantém saída padrão para não travar o fluxo.
    }
    setPartidaId(null)
    navigate('/tournament')
  }

  const surface = normSurface(superficie)
  const momentum = calcMomentum(placar)
  const pontoCritico = detectarPontoCritico(placar)
  const podeControlarRitmo =
    fase !== 'encerrada' &&
    fase !== 'entre-games' &&
    fase !== 'entre-sets' &&
    fase !== 'jogando' &&
    Boolean(partidaId)
  const leituraJogador = leituraFisica(energiaJogadorAoVivo, fadigaJogadorAoVivo)
  const leituraRival = leituraFisica(energiaAdversarioAoVivo, fadigaAdversarioAoVivo)
  const rankingJogador = rankingValido(jogador?.ranking)
  const rankingAdversario = rankingValido(adversario.ranking)
  const historicoRival = resumirHistoricoRival(adversario.historicoPartidas, adversario.historicoTorneios)
  const titulosRival = resumirTitulosRival(adversario.trofeus)
  const historicoJogador = resumirHistoricoRival(
    Array.isArray((jogador as any)?.historico_partidas) ? (jogador as any).historico_partidas : [],
    Array.isArray((jogador as any)?.historico_torneios) ? (jogador as any).historico_torneios : [],
  )
  const titulosJogador = resumirTitulosRival(Array.isArray((jogador as any)?.trofeus) ? (jogador as any).trofeus : [])
  const corCardRival = accentFromCarta(adversario.carta, '#ff4466')
  const metricsJogador = getScoutingMetricsFromData(
    jogador?.carta?.atributos_boosted ?? jogador?.atributos ?? {},
    jogador?.atributos_psicologicos ?? {},
    (jogador as any)?.resumo_fifa,
  )
  const reportJogador = montarRelatorioJogador({
    nome: nomeJogador,
    energia: energiaJogadorAoVivo,
    fadiga: fadigaJogadorAoVivo,
    encaixeFisico,
    metrics: metricsJogador,
    superficie,
  })
  const overallCardJogador = calcularOverallCardMatch(metricsJogador)
  const metricsAdversario = getScoutingMetrics(adversario)
  const overallCardAdversario = calcularOverallCardMatch(metricsAdversario)
  const destaqueMomento = alertaBreak || flashPonto?.texto || pontoCritico?.label || resumoMomentum(momentum)
  const destaqueMomentoCor = alertaBreak
    ? '#ff4466'
    : flashPonto?.color || pontoCritico?.color || '#00e5ff'
  const ultimosEventos = [...log].reverse().slice(0, 4)
  const velocidadeRapidaAtual = VELOCIDADES_RAPIDAS.find((item) => item.valor === velocidadeRapida) ?? VELOCIDADES_RAPIDAS[2]
  const resumoEstrategiaJogador = resumirEstrategiaLado(estrategiaJogadorAoVivo)
  const resumoEstrategiaAdversario = resumirEstrategiaLado(estrategiaAdversarioAoVivo)

  function trocarModoAcompanhamento(novoModo: ModoAcomp) {
    setModo(novoModo)
    if (novoModo !== 'detalhado') {
      setSimulacaoPausada(false)
      setAjustandoPlanoRapido(false)
    }
  }

  function alternarPausaSimulacao() {
    if (modo !== 'detalhado' || !partidaId || fase === 'encerrada' || fase === 'jogando') return
    setSimulacaoPausada((atual) => {
      const proximo = !atual
      setAjustandoPlanoRapido(proximo)
      return proximo
    })
    if (fase !== 'aguardando') setFase('aguardando')
  }

	  if (fase === 'setup') {
    return (
      <div className="app-shell min-h-screen flex flex-col bg-[#0a0a0f]">
        {/* Header Vestiário */}
        <div className="app-panel p-4 border-b-2 border-[#00ff88] flex items-center justify-between shrink-0 bg-black/40">
          <div className="flex items-center gap-3">
            <button onClick={() => navigate('/tournament')} className="text-[#00ff88] hover:scale-110 transition-transform">
              <ArrowLeft size={22} />
            </button>
            <div>
              <div className="arcade-font text-[10px] text-[#00ff88] tracking-[0.2em]">VESTIÁRIO</div>
              <div className="arcade-font text-[12px] text-white mt-0.5">
                {faseTorneio ? faseTorneio.replaceAll('_', ' ').toUpperCase() : 'PARTIDA'}
              </div>
            </div>
          </div>
          {superficie && (
            <div className="flex flex-col items-end">
              <div className="arcade-font text-[8px] text-[#555] mb-1">QUADRA</div>
              <div className="flex items-center gap-2">
                <div className="h-2 w-6 border border-white/20" style={{ background: COURT_COLORS[surface] }} />
                <span className="arcade-font text-[10px] text-white">{superficie.toUpperCase()}</span>
              </div>
            </div>
          )}
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-6 pb-32">
          
          {/* Cartas FIFA (Pré-Match) */}
          <div className="flex flex-col lg:flex-row gap-6 items-center justify-center py-4 bg-gradient-to-b from-[#0a0a0f] to-transparent">
            <div className="flex flex-col items-center gap-2">
              <div className="arcade-font text-[10px] text-[#00ff88] tracking-widest uppercase mb-2">SEU JOGADOR</div>
              <FutCard
                nome={jogador?.nome ?? 'VOCÊ'}
                nacionalidade={jogador?.nacionalidade ?? ''}
                overall={overallCardJogador}
                tour={(jogador?.tour ?? 'atp').toLowerCase() as 'atp' | 'wta'}
                ranking={rankingJogador ?? 0}
                nivel={jogador?.nivel ?? 1}
                atributos={jogador?.atributos ?? {}}
                atributosPsicologicos={jogador?.atributos_psicologicos ?? {}}
                cartaTipo={jogador?.carta?.tipo}
                cartaRaridade={jogador?.carta?.raridade}
                cartaCor={jogador?.carta?.cor_primaria}
                overallBoosted={jogador?.carta?.overall_boosted}
                atributosBoosted={jogador?.carta?.atributos_boosted}
              />
            </div>

            <div className="flex items-center justify-center">
              <div className="arcade-font text-[24px] text-white/20 italic select-none">VS</div>
            </div>

            <div className="flex flex-col items-center gap-2">
              <div className="arcade-font text-[10px] text-[#ff4466] tracking-widest uppercase mb-2">ADVERSÁRIO</div>
              <FutCard
                nome={adversario.nome}
                nacionalidade={adversario.nacionalidade ?? ''}
                overall={overallCardAdversario}
                tour={(jogador?.tour ?? 'atp').toLowerCase() as 'atp' | 'wta'}
                ranking={rankingAdversario ?? 0}
                nivel={1} // Adversário NPC costuma ser nível 1 ou não mostrado
                atributos={adversario.atributos ?? {}}
                atributosPsicologicos={adversario.atributosPsicologicos ?? {}}
                cartaTipo={adversario.carta?.tipo}
                cartaRaridade={adversario.carta?.raridade}
                cartaCor={adversario.carta?.cor_primaria}
                overallBoosted={adversario.overallBoosted}
                atributosBoosted={adversario.atributosBoosted}
              />
            </div>
          </div>
          
          {/* Match Analysis (FM Style) */}
	          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
	            <div className="space-y-3">
	              <div className="flex items-center gap-2 mb-1">
	                <div className="w-1 h-4" style={{ background: corCardRival }} />
	                <span className="arcade-font text-[12px] tracking-widest" style={{ color: corCardRival }}>ANÁLISE DO RIVAL</span>
	              </div>
	              <div className="app-panel border-2 p-4 relative overflow-hidden" style={{ borderColor: alpha(corCardRival, '66') }}>
                <div className="absolute top-0 right-0 p-2 opacity-5">
                  <div className="text-6xl">🎾</div>
                </div>
		                <div className="flex justify-between items-start mb-4">
		                  <div>
		                    <div className="arcade-font text-xl text-white mb-1">{adversario.nome}</div>
                      <div className="arcade-font text-[10px] text-[#d49aac] mb-1">
                        {formatarNacionalidade(adversario.nacionalidade)}
                      </div>
		                    <div className="arcade-font text-[11px] text-[#888]">
		                      {rankingAdversario ? `#${rankingAdversario} MUNDIAL` : 'SEM RANKING'}
		                    </div>
		                  </div>
	                  <div className="text-right">
	                    <div className="arcade-font text-[10px] mb-1" style={{ color: corCardRival }}>
                        OVR {overallCardAdversario}
                      </div>
		                  </div>
		                </div>
                    <div className="grid grid-cols-1 md:grid-cols-[0.9fr_1.1fr] gap-3 mb-4">
                      <div className="p-3 border" style={{ background: alpha(corCardRival, '0d'), borderColor: alpha(corCardRival, '33') }}>
                        <div className="arcade-font text-[10px] tracking-widest mb-1 uppercase" style={{ color: alpha(corCardRival, 'cc') }}>Leitura</div>
                        <div className="arcade-font text-[12px] text-white leading-relaxed">{leituraRival}</div>
                      </div>
                      <div className="p-3 border" style={{ background: alpha(corCardRival, '0d'), borderColor: alpha(corCardRival, '33') }}>
                        <div className="mb-2 flex items-center justify-between gap-2">
                          <div className="arcade-font text-[10px] tracking-widest uppercase" style={{ color: alpha(corCardRival, 'cc') }}>
                            {abaRival === 'registros' ? 'Últimos Registros' : 'História'}
                          </div>
                          <div className="flex gap-1">
                            <button
                              onClick={() => setAbaRival('registros')}
                              className="border px-2 py-1 arcade-font text-[8px]"
                              style={{
                                borderColor: abaRival === 'registros' ? corCardRival : alpha(corCardRival, '55'),
                                color: abaRival === 'registros' ? '#12060b' : '#ff9bb4',
                                background: abaRival === 'registros' ? corCardRival : 'transparent',
                              }}
                            >
                              REGISTROS
                            </button>
                            <button
                              onClick={() => setAbaRival('historia')}
                              className="border px-2 py-1 arcade-font text-[8px]"
                              style={{
                                borderColor: abaRival === 'historia' ? '#ffe600' : '#6c5f2b',
                                color: abaRival === 'historia' ? '#1b1803' : '#ffe27a',
                                background: abaRival === 'historia' ? '#ffe600' : 'transparent',
                              }}
                            >
                              TÍTULOS
                            </button>
                          </div>
                        </div>
                        {abaRival === 'registros' ? (
                          historicoRival.length > 0 ? (
                            <div className="space-y-1.5">
                              {historicoRival.map(item => (
                                <div key={item} className="arcade-font text-[10px] text-[#ffd7e2] leading-relaxed">
                                  {item}
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div className="arcade-font text-[10px] text-[#c18a9d] leading-relaxed">
                              Sem histórico recente salvo para este adversário.
                            </div>
                          )
                        ) : titulosRival.length > 0 ? (
                          <div className="space-y-1.5">
                            {titulosRival.map(item => (
                              <div key={item} className="arcade-font text-[10px] text-[#fff0a6] leading-relaxed">
                                {item}
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="arcade-font text-[10px] text-[#c9bc7c] leading-relaxed">
                            Nenhum título registrado para este adversário.
                          </div>
                        )}
                        <button
                          onClick={() => navigate(`/player/${(jogador?.tour ?? 'atp').toLowerCase()}/${encodeURIComponent(adversario.nome)}`)}
                          className="mt-3 arcade-font text-[9px] uppercase underline underline-offset-4"
                          style={{ color: corCardRival }}
                        >
                          Ver dossiê completo
                        </button>
                      </div>
                    </div>
	                  <div className="flex items-center justify-end gap-6 mb-4">
	                    <CircularGauge label="ENERGIA" value={energiaAdversarioAoVivo} color={corCardRival} />
	                    <CircularGauge label="FADIGA" value={fadigaAdversarioAoVivo} color="#ffe600" track="#26131b" />
	                  </div>
		                <OpponentScouting adv={adversario} accent={corCardRival} superficie={superficie} />
	              </div>
	            </div>

	            <div className="space-y-3">
	              <div className="flex items-center gap-2 mb-1">
	                <div className="w-1 h-4 bg-[#00ff88]" />
	                <span className="arcade-font text-[12px] text-[#00ff88] tracking-widest">SUA CONDIÇÃO</span>
	              </div>
	              <div className="app-panel border-2 border-[#00ff88]/40 p-4 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-2 opacity-5">
                  <div className="text-6xl">🫀</div>
                </div>
		                <div className="flex justify-between items-start mb-4">
		                  <div>
		                    <div className="arcade-font text-xl text-white mb-1">{nomeJogador}</div>
                      <div className="arcade-font text-[10px] text-[#92ffd1] mb-1">
                        {formatarNacionalidade(jogador?.nacionalidade)}
                      </div>
		                    <div className="arcade-font text-[11px] text-[#888]">
		                      #{rankingJogador || '---'} · OVR {overallCardJogador} · {inferirEstilo(jogador?.atributos)}
		                    </div>
		                  </div>
	                </div>
                  <div className="grid grid-cols-1 md:grid-cols-[0.9fr_1.1fr] gap-3 mb-4">
                    <div className="bg-[#00ff88]/5 border border-[#00ff88]/20 p-3">
	                  <div className="arcade-font text-[10px] text-[#73ffbb] tracking-widest mb-1 uppercase">Leitura</div>
	                  <div className="arcade-font text-[12px] text-white leading-relaxed">{leituraJogador}</div>
                    </div>
                    <div className="bg-[#00ff88]/5 border border-[#00ff88]/20 p-3">
                      <div className="mb-2 flex items-center justify-between gap-2">
                        <div className="arcade-font text-[10px] text-[#73ffbb] tracking-widest uppercase">
                          {abaJogador === 'registros' ? 'Últimos Registros' : 'História'}
                        </div>
                        <div className="flex gap-1">
                          <button
                            onClick={() => setAbaJogador('registros')}
                            className="border px-2 py-1 arcade-font text-[8px]"
                            style={{
                              borderColor: abaJogador === 'registros' ? '#00ff88' : '#245843',
                              color: abaJogador === 'registros' ? '#02120b' : '#9cf6ce',
                              background: abaJogador === 'registros' ? '#00ff88' : 'transparent',
                            }}
                          >
                            REGISTROS
                          </button>
                          <button
                            onClick={() => setAbaJogador('historia')}
                            className="border px-2 py-1 arcade-font text-[8px]"
                            style={{
                              borderColor: abaJogador === 'historia' ? '#ffe600' : '#6c5f2b',
                              color: abaJogador === 'historia' ? '#1b1803' : '#ffe27a',
                              background: abaJogador === 'historia' ? '#ffe600' : 'transparent',
                            }}
                          >
                            TÍTULOS
                          </button>
                        </div>
                      </div>
                      {abaJogador === 'registros' ? (
                        historicoJogador.length > 0 ? (
                          <div className="space-y-1.5">
                            {historicoJogador.map(item => (
                              <div key={item} className="arcade-font text-[10px] text-[#d7fff0] leading-relaxed">
                                {item}
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="arcade-font text-[10px] text-[#8dbda8] leading-relaxed">
                            Sem histórico recente salvo para o seu jogador.
                          </div>
                        )
                      ) : titulosJogador.length > 0 ? (
                        <div className="space-y-1.5">
                          {titulosJogador.map(item => (
                            <div key={item} className="arcade-font text-[10px] text-[#fff0a6] leading-relaxed">
                              {item}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="arcade-font text-[10px] text-[#c9bc7c] leading-relaxed">
                          Nenhum título registrado para o seu jogador.
                        </div>
                      )}
                    </div>
                  </div>
	                <div className="flex items-center justify-end gap-6 mb-4">
                    <CircularGauge label="ENERGIA" value={energiaJogadorAoVivo} color="#00ff88" />
                    <CircularGauge label="FADIGA" value={fadigaJogadorAoVivo} color="#ffe600" track="#102319" />
                  </div>
                  <ScoutingReport
                    titulo="Scouting Report"
                    overall={overallCardJogador}
                    metrics={{ saque: metricsJogador.saque, fundo: metricsJogador.fundo, mental: metricsJogador.mental }}
                    report={reportJogador}
                    accent="#00ff88"
                  />
	              </div>
	            </div>
          </div>

          {/* FM TACTICAL PANEL */}
	          <div className="space-y-4">
	            <div className="flex items-center gap-2">
	              <div className="w-1 h-4 bg-[#ffe600]" />
	              <span className="arcade-font text-[12px] text-[#ffe600] tracking-widest uppercase">Instruções Táticas</span>
	            </div>

            <div className="grid grid-cols-1 gap-4">
                <div className="grid grid-cols-1 md:grid-cols-[1.5fr_0.8fr_0.8fr] gap-4">
                  <div className="app-panel border border-[#ffe600]/20 p-4 bg-[#ffe60008]">
		                  <div className="arcade-font text-[11px] text-[#ffe600] mb-2 tracking-widest uppercase">Resumo do Plano</div>
	                  <div className="arcade-font text-[13px] text-white leading-relaxed">
	                    {planoExecutivo}
	                  </div>
		                  <div className="arcade-font text-[11px] text-[#c8d5df] mt-3 leading-relaxed">
	                    {mentalidade === 'OFENSIVA'
                        ? 'A equipe técnica espera um jogo de imposição e tomada rápida da iniciativa.'
                        : mentalidade === 'DEFENSIVA'
                          ? 'A ideia central é absorver pressão, alongar rallies e baixar o risco.'
                          : 'O plano busca estabilidade, leitura do rival e ajustes durante a partida.'}
                    </div>
                  </div>

                  <div className="app-panel border border-[#00ff88]/20 p-4 bg-[#00ff8808]">
		                    <div className="arcade-font text-[11px] text-[#00ff88] mb-2 tracking-widest uppercase">Encaixe Físico</div>
                    <div
                      className="pixel-font text-xl"
                      style={{ color: encaixeFisico === 'ALTO' ? '#00ff88' : encaixeFisico === 'MÉDIO' ? '#ffe600' : '#ff4466' }}
                    >
                      {encaixeFisico}
                    </div>
		                    <div className="arcade-font text-[11px] text-[#c7ddd0] mt-2 leading-relaxed">
                      {encaixeFisico === 'ALTO'
                        ? 'Seu estado atual sustenta esse plano com conforto.'
                        : encaixeFisico === 'MÉDIO'
                          ? 'Dá para executar, mas precisa dosar intensidade.'
                          : 'Seu físico pede um plano mais conservador.'}
                    </div>
                  </div>

                  <div className="app-panel border border-[#ff4466]/20 p-4 bg-[#ff446608]">
		                    <div className="arcade-font text-[11px] text-[#ff4466] mb-2 tracking-widest uppercase">Risco Tático</div>
                    <div
                      className="pixel-font text-xl"
                      style={{ color: riscoTatico === 'BAIXO' ? '#00ff88' : riscoTatico === 'MÉDIO' ? '#ffe600' : '#ff4466' }}
                    >
                      {riscoTatico}
                    </div>
		                    <div className="arcade-font text-[11px] text-[#dfc6cc] mt-2 leading-relaxed">
                      {riscoTatico === 'ALTO'
                        ? 'Plano agressivo. Erros cedo podem virar pressão contra você.'
                        : riscoTatico === 'MÉDIO'
                          ? 'Existe bom potencial, mas com trade-off claro.'
                          : 'Estrutura segura para entrar no jogo e ajustar depois.'}
                    </div>
                  </div>
                </div>

	              <div className="app-panel border border-white/10 p-4 bg-white/5">
                  <div className="arcade-font text-[11px] text-[#b7c4d1] mb-3 tracking-widest uppercase">Pacote Tático</div>
                  <TacticalPackageEditor
                    mentalidade={mentalidade}
                    abordagem={abordagem}
                    instrucao={instrucao}
                    segundoSaque={segundoSaque}
                    setMentalidade={setMentalidade}
                    setAbordagem={setAbordagem}
                    setInstrucao={setInstrucao}
                    setSegundoSaque={setSegundoSaque}
                  />
                </div>
            </div>
          </div>

          {/* Modo de Acompanhamento (Compacto) */}
          <div className="app-panel border border-white/5 p-4">
            <div className="flex items-center justify-between mb-3">
	              <div className="arcade-font text-[10px] text-[#b7c4d1] tracking-widest uppercase">Velocidade da Experiência</div>
	              <div className="arcade-font text-[10px] text-[#ffe600]">{MODOS_ACOMP.find(m => m.valor === modo)?.label}</div>
            </div>
            <div className="mb-3 arcade-font text-[10px] text-[#95a7b5] leading-relaxed">
              Escolha só entre manual, rápida ou simular até o fim.
            </div>
            <div className="grid grid-cols-3 gap-2">
              {MODOS_VISIVEIS.map(m => (
                <button
                  key={m.valor}
                  onClick={() => trocarModoAcompanhamento(m.valor)}
	                  className="py-2.5 border arcade-font text-[9px] transition-all"
                  style={{
                    borderColor: modo === m.valor ? '#00ff88' : '#1a1a2e',
                    background: modo === m.valor ? '#00ff8812' : 'transparent',
	                    color: modo === m.valor ? '#00ff88' : '#c4d1dc',
                  }}
                >
                  {m.label}
                </button>
              ))}
            </div>
          </div>

        </div>

        {/* Botão de Ação Sticky */}
        <div className="sticky bottom-0 z-30 p-4 border-t border-white/10 bg-black/80 backdrop-blur-md">
          {erroEntrada && (
            <div className="mb-3 border border-[#ff4466] bg-[#22040d] px-3 py-2 arcade-font text-[10px] text-[#ff9bb4]">
              {erroEntrada.toUpperCase()}
            </div>
          )}
          <NeonButton 
            variant="green" 
            className="w-full py-5 text-sm" 
            onClick={handleIniciar} 
            blink={simulando}
          >
            {simulando ? 'CALCULANDO ESTRATÉGIAS...' : confirmandoEntrada ? 'CONFIRMAR E ENTRAR EM QUADRA' : 'DEFINIR PLANO E JOGAR'}
          </NeonButton>
        </div>
      </div>
    )
  }

  // ─── PÓS-STATS ───────────────────────────────────────────────────────────

  if (fase === 'pos-stats') {
    const sj = placar.stats_j
    const sa = placar.stats_a
    const editorial = destaquePartida(placar, nomeJogador, adversario.nome, log)
    return (
      <div className="app-shell min-h-screen flex flex-col">
        <div className="p-4 border-b-2 border-[#00e5ff] app-panel shrink-0">
          <div className="arcade-font text-[9px] text-[#00e5ff] tracking-widest">RESUMO DA PARTIDA</div>
          <div className="arcade-font text-lg text-white mt-1">
            {placar.placar_final || `${placar.sets[0]} × ${placar.sets[1]} sets`}
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <div className="border border-[#00e5ff]/25 bg-[#04101b] p-4">
            <div className="arcade-font text-[10px] text-[#4bb8d1] tracking-widest mb-2">PONTO DE VIRADA</div>
            <div className="arcade-font text-[12px] text-[#d7f3ff] leading-relaxed">{editorial}</div>
          </div>
          {sj && sa ? (
            <div className="border border-[#00e5ff]/20 bg-[#020611] p-4 space-y-2">
              <div className="grid grid-cols-[1fr_auto_1fr] gap-2 arcade-font text-[12px] mb-4">
                <div className="text-[#00ff88] truncate">{nomeJogador}</div>
                <div className="text-[#d7f3ff] text-center text-[14px] tracking-wide">STAT</div>
                <div className="text-right text-[#ff8d6d] truncate">{adversario.nome}</div>
              </div>
              <StatLine label="Aces" j={sj.aces} a={sa.aces} />
              <StatLine label="Duplas faltas" j={sj.duplas_faltas} a={sa.duplas_faltas} />
              <StatLine label="1º saque %" j={sj.primeiro_saque_pct} a={sa.primeiro_saque_pct} />
              <StatLine label="Winners" j={sj.winners} a={sa.winners} />
              <StatLine label="Erros N/F" j={sj.erros_nao_forcados} a={sa.erros_nao_forcados} />
              <StatLine label="Pts saque" j={sj.pontos_saque_pct} a={sa.pontos_saque_pct} />
              <StatLine label="Break pts" j={sj.break_points} a={sa.break_points} />
            </div>
          ) : (
            <div className="arcade-font text-[#555] text-center py-8">
              Estatísticas não disponíveis.
            </div>
          )}
          {log.length > 0 && (
            <div className="border border-[#1a1a2e] p-3">
              <div className="arcade-font text-[14px] text-[#d7f3ff] mb-3 tracking-wide text-center">
                MOMENTOS
              </div>
              <div className="space-y-1 max-h-40 overflow-y-auto">
                {[...log].reverse().slice(0, 20).map((linha, i) => (
                  <div
                    key={i}
                    className="arcade-font text-[12px] flex gap-2 leading-relaxed"
                    style={{ color: i === 0 ? '#d7f3ff' : '#9cb4c7' }}
                  >
                    <span className="text-[#00e5ff]">▸</span>
                    <span>{linha}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        <div className="p-4 border-t border-[#1a1a2e] shrink-0">
          <NeonButton 
            variant="cyan" 
            className="w-full" 
            disabled={!jogadorPosjogo}
            onClick={() => setFase('pos-consequencias')}
          >
            {jogadorPosjogo ? 'VER CONSEQUÊNCIAS →' : 'CARREGANDO DADOS...'}
          </NeonButton>
        </div>
      </div>
    )
  }

  // ─── PÓS-CONSEQUÊNCIAS ───────────────────────────────────────────────────

  if (fase === 'pos-consequencias') {
    const j = jogadorPosjogo || jogador
    const antes = jogadorAntesRef.current
    const xpGanho = j && antes ? j.xp - antes.xp : null
    const rankingDelta = j && antes ? antes.ranking - (j.ranking ?? antes.ranking) : null
    const subiuNivel = j && antes ? j.nivel > antes.nivel : false

    return (
      <div className="app-shell min-h-screen flex flex-col">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {subiuNivel && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="border-2 border-[#ffe600] bg-[#0f0c00] p-5 text-center"
              style={{ boxShadow: '0 0 30px rgba(255,230,0,0.4)' }}
            >
              <div className="pixel-font text-2xl text-[#ffe600]">SUBIU DE NÍVEL!</div>
              <div className="arcade-font text-[10px] text-[#888] mt-2">
                NÍVEL {j?.nivel}
              </div>
            </motion.div>
          )}

          <div className="border-2 border-[#00ff88] bg-[#050e05] p-4">
            <div className="arcade-font text-[9px] text-[#00ff88] mb-4 tracking-widest">
              RESULTADO FINAL
            </div>
            <div className="space-y-3">
              {xpGanho !== null && (
                <div className="flex items-center justify-between">
                  <span className="arcade-font text-[10px] text-[#8aa0b5]">XP GANHO</span>
                  <motion.span
                    initial={{ opacity: 0, x: 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="arcade-font text-[13px] text-[#00ff88]"
                  >
                    +{Math.max(0, xpGanho)}
                  </motion.span>
                </div>
              )}
              {rankingDelta !== null && rankingDelta !== 0 && (
                <div className="flex items-center justify-between">
                  <span className="arcade-font text-[10px] text-[#8aa0b5]">RANKING</span>
                  <span
                    className="arcade-font text-[13px]"
                    style={{ color: rankingDelta > 0 ? '#00ff88' : '#ff0055' }}
                  >
                    {rankingDelta > 0 ? `↑ ${rankingDelta}` : `↓ ${Math.abs(rankingDelta)}`}
                  </span>
                </div>
              )}
              {j && (
                <>
                  <div className="flex items-center justify-between">
                    <span className="arcade-font text-[10px] text-[#8aa0b5]">NÍVEL</span>
                    <span className="arcade-font text-[13px] text-[#ffe600]">{j.nivel}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="arcade-font text-[10px] text-[#8aa0b5]">SALDO</span>
                    <span className="arcade-font text-[13px] text-[#00e5ff]">
                      ${j.dinheiro?.toLocaleString('pt-BR') ?? '-'}
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
        <div className="p-4 border-t border-[#1a1a2e] shrink-0">
          <NeonButton variant="green" className="w-full" onClick={handleContinuarPosJogo}>
            CONTINUAR →
          </NeonButton>
        </div>
      </div>
    )
  }

  // ─── IN-GAME ─────────────────────────────────────────────────────────────

  return (
    <div className="app-shell min-h-screen flex flex-col bg-[#050505]">
      {/* Header sticky — placar compacto */}
      <div className="app-panel sticky top-0 z-20 p-3 border-b-2 border-[#00ff88] flex items-center gap-3 shrink-0 bg-black/80 backdrop-blur-md">
        <button onClick={() => navigate('/tournament')} className="text-[#00ff88] hover:scale-110 transition-transform">
          <ArrowLeft size={18} />
        </button>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <span className="arcade-font text-[9px] text-white truncate max-w-[100px]">{nomeJogador}</span>
            <div className="flex gap-2 arcade-font text-[10px]">
              <span className={placar.sets[0] > placar.sets[1] ? 'text-[#00ff88]' : 'text-[#444]'}>{placar.sets[0]}</span>
              <span className="text-[#222]">|</span>
              <span className={placar.sets[1] > placar.sets[0] ? 'text-[#ff4466]' : 'text-[#444]'}>{placar.sets[1]}</span>
            </div>
            <span className="arcade-font text-[9px] text-white truncate max-w-[100px] text-right">{adversario.nome}</span>
          </div>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto p-3 space-y-3 pb-4">
        <div className="border border-[#00ff88]/30 bg-[#08110b] p-3">
          <div className="mb-2 flex items-center justify-between arcade-font text-[8px] tracking-widest text-[#6f8b77]">
            <span>PLACAR AO VIVO</span>
            <span>{superficie ? superficie.toUpperCase() : 'PARTIDA'}</span>
          </div>
          <div className="mb-2 grid grid-cols-[1fr_auto_auto_auto] gap-2 border-b border-white/5 pb-2 arcade-font text-[7px] text-[#4b5d52]">
            <span />
            <span>SETS</span>
            <span>GAMES</span>
            <span>PTS</span>
          </div>
          <div className="grid grid-cols-[1fr_auto_auto_auto] items-center gap-2 arcade-font text-[12px]">
            <span className="truncate text-[#00ff88]">{nomeJogador}</span>
            <span className="text-[#00ff88]">{placar.sets[0]}</span>
            <span className="text-[#00ff88]">{placar.games[0]}</span>
            <span className="text-[#00ff88]">{placar.pontos[0]}</span>
            <span className="truncate text-[#ff8d6d]">{adversario.nome}</span>
            <span className="text-[#ff8d6d]">{placar.sets[1]}</span>
            <span className="text-[#ff8d6d]">{placar.games[1]}</span>
            <span className="text-[#ff8d6d]">{placar.pontos[1]}</span>
          </div>
        </div>

        <div className="border border-[#2a3440] bg-[#071019] p-3">
          <div className="flex items-center justify-between mb-2 arcade-font text-[8px] tracking-widest text-[#8292a1]">
            <span>MOMENTUM / EMOCIONAL</span>
            <span style={{ color: corMomentum(momentum) }}>{resumoMomentum(momentum)}</span>
          </div>
          <InlineMeter value={momentum} color={corMomentum(momentum)} />
          <div className="mt-2 arcade-font text-[10px] leading-relaxed" style={{ color: destaqueMomentoCor }}>
            {destaqueMomento}
          </div>
          <div className="mt-2 arcade-font text-[9px] text-[#b8c6d1]">
            {resumoModo(modo)}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="border border-[#00ff88]/20 bg-[#07110a] p-3">
            <div className="arcade-font text-[8px] tracking-widest text-[#77d39e] mb-2">VOCÊ</div>
            <div className="space-y-2 arcade-font text-[10px] text-white">
              <div>
                <div className="mb-1 flex items-center justify-between text-[#9fe5bb]">
                  <span>Energia</span>
                  <span>{Math.round(energiaJogadorAoVivo)}%</span>
                </div>
                <InlineMeter value={Math.round(energiaJogadorAoVivo)} color="#00ff88" />
              </div>
              <div>
                <div className="mb-1 flex items-center justify-between text-[#ffe07a]">
                  <span>Fadiga</span>
                  <span>{Math.round(fadigaJogadorAoVivo)}%</span>
                </div>
                <InlineMeter value={Math.round(fadigaJogadorAoVivo)} color="#ffe600" />
              </div>
              <div className="text-[#8fbea1] leading-relaxed">{leituraJogador}</div>
              <div className="border-t border-[#1d3525] pt-2 space-y-1">
                {resumoEstrategiaJogador.map((linha) => (
                  <div key={linha} className="text-[#8fbea1] leading-relaxed">{linha}</div>
                ))}
              </div>
            </div>
          </div>
          <div className="border border-[#ff4466]/20 bg-[#14090d] p-3">
            <div className="arcade-font text-[8px] tracking-widest text-[#ff8ca3] mb-2">RIVAL</div>
            <div className="space-y-2 arcade-font text-[10px] text-white">
              <div>
                <div className="mb-1 flex items-center justify-between text-[#ffb7c6]">
                  <span>Energia</span>
                  <span>{Math.round(energiaAdversarioAoVivo)}%</span>
                </div>
                <InlineMeter value={Math.round(energiaAdversarioAoVivo)} color="#ff4466" />
              </div>
              <div>
                <div className="mb-1 flex items-center justify-between text-[#ffe07a]">
                  <span>Fadiga</span>
                  <span>{Math.round(fadigaAdversarioAoVivo)}%</span>
                </div>
                <InlineMeter value={Math.round(fadigaAdversarioAoVivo)} color="#ffe600" />
              </div>
              <div className="text-[#d7a7b2] leading-relaxed">{leituraRival}</div>
              <div className="border-t border-[#35202a] pt-2 space-y-1">
                {resumoEstrategiaAdversario.map((linha) => (
                  <div key={linha} className="text-[#d7a7b2] leading-relaxed">{linha}</div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {(placar.stats_j || placar.stats_a) && (
          <div className="overflow-hidden border border-[#36505d] bg-[#0b160f]">
            <div className="flex items-center justify-between bg-[#4b2c63] px-3 py-2">
              <div className="arcade-font text-[10px] tracking-widest text-white">MATCH SUMMARY</div>
              <div className="arcade-font text-[8px] text-[#d6c3e7]">AO VIVO</div>
            </div>
            <div className="grid grid-cols-[1fr_auto_1fr] items-center bg-[#24462c] px-3 py-2 arcade-font text-[9px]">
              <div className="truncate text-left text-[#d8f5df]">{nomeJogador.toUpperCase()}</div>
              <div className="text-center text-[#aac7ac]">STAT</div>
              <div className="truncate text-right text-[#ffe0d6]">{adversario.nome.toUpperCase()}</div>
            </div>
            <div className="divide-y divide-[#28402f]">
              {[
                { label: 'Aces', j: placar.stats_j?.aces ?? 0, a: placar.stats_a?.aces ?? 0 },
                { label: 'Double Faults', j: placar.stats_j?.duplas_faltas ?? 0, a: placar.stats_a?.duplas_faltas ?? 0 },
                { label: '1st Serves In', j: placar.stats_j?.primeiro_saque_pct ?? '0%', a: placar.stats_a?.primeiro_saque_pct ?? '0%' },
                { label: 'Winners', j: placar.stats_j?.winners ?? 0, a: placar.stats_a?.winners ?? 0 },
                { label: 'Unforced Errors', j: placar.stats_j?.erros_nao_forcados ?? 0, a: placar.stats_a?.erros_nao_forcados ?? 0 },
                { label: 'Break Points', j: placar.stats_j?.break_points ?? '0/0', a: placar.stats_a?.break_points ?? '0/0' },
              ].map((item, idx) => (
                <div
                  key={item.label}
                  className="grid grid-cols-[1fr_auto_1fr] items-center gap-3 px-3 py-2 arcade-font text-[10px]"
                  style={{ background: idx % 2 === 0 ? '#17331f' : '#12281a' }}
                >
                  <div className="text-left text-[#f0fff4]">{item.j}</div>
                  <div className="text-center text-[#c9dfc9]">{item.label}</div>
                  <div className="text-right text-[#ffe9dc]">{item.a}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="border border-white/10 bg-[#0a0a0a] p-3 space-y-3">
          <div>
            <div className="arcade-font text-[8px] tracking-widest text-[#7f8b96] mb-1">PLANO ATUAL</div>
            <div className="arcade-font text-[12px]" style={{ color: planoAtual.color }}>
              {planoAtual.label}
            </div>
            <div className="arcade-font text-[9px] text-[#b9c4cd] mt-1">{planoAtual.desc}</div>
            <div className="arcade-font text-[9px] text-[#8da6b7] mt-2">
              2º saque: {segundoSaque === 'FORCAR' ? 'forçar' : 'seguro'}
            </div>
          </div>
        </div>

        {fase !== 'encerrada' &&
          fase !== 'entre-games' &&
          fase !== 'entre-sets' &&
          modo === 'detalhado' && (
            <div className="border border-[#ffe600]/25 bg-[#110d02] p-3 space-y-3">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="arcade-font text-[8px] tracking-widest text-[#ffe600]">SIMULAÇÃO RÁPIDA</div>
                  <div className="arcade-font text-[9px] text-[#c8b877] mt-1">
                    Velocidade atual: {velocidadeRapidaAtual.label} · {simulacaoPausada ? 'pausada' : 'rodando'}
                  </div>
                </div>
                <button
                  onClick={alternarPausaSimulacao}
                  disabled={!partidaId || fase === 'jogando'}
                  className="border px-3 py-2 arcade-font text-[8px] transition-all disabled:opacity-40"
                  style={{
                    borderColor: simulacaoPausada ? '#00ff88' : '#ffe600',
                    color: simulacaoPausada ? '#00ff88' : '#ffe600',
                    background: simulacaoPausada ? '#00ff8810' : '#ffe60010',
                  }}
                >
                  {simulacaoPausada ? 'CONTINUAR' : 'PAUSAR'}
                </button>
              </div>

              <div className="grid grid-cols-4 gap-2">
                {VELOCIDADES_RAPIDAS.map((item) => (
                  <button
                    key={item.valor}
                    onClick={() => setVelocidadeRapida(item.valor)}
                    className="border px-2 py-2 text-center transition-all"
                    style={{
                      borderColor: velocidadeRapida === item.valor ? '#ffe600' : '#3a3220',
                      background: velocidadeRapida === item.valor ? '#ffe60012' : 'transparent',
                      color: velocidadeRapida === item.valor ? '#ffe600' : '#bcae72',
                    }}
                  >
                    <div className="arcade-font text-[9px]">{item.label}</div>
                    <div className="arcade-font text-[7px] mt-1 opacity-80">{item.desc}</div>
                  </button>
                ))}
              </div>

              {simulacaoPausada && (
                <div className="border border-[#00e5ff]/20 bg-[#04101b] p-3 space-y-3">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="arcade-font text-[8px] tracking-widest text-[#00e5ff]">PAINEL TÁTICO</div>
                      <div className="arcade-font text-[9px] text-[#90b8c9] mt-1">
                        Pause, ajuste o plano e retome a simulação.
                      </div>
                    </div>
                    <button
                      onClick={() => setAjustandoPlanoRapido((atual) => !atual)}
                      className="border px-3 py-2 arcade-font text-[8px] text-[#00e5ff] transition-all"
                      style={{ borderColor: '#00e5ff33', background: ajustandoPlanoRapido ? '#00e5ff10' : 'transparent' }}
                    >
                      {ajustandoPlanoRapido ? 'OCULTAR' : 'AJUSTAR'}
                    </button>
                  </div>

                  {ajustandoPlanoRapido && (
                    <>
                      <TacticalPackageEditor
                        mentalidade={mentalidade}
                        abordagem={abordagem}
                        instrucao={instrucao}
                        segundoSaque={segundoSaque}
                        setMentalidade={setMentalidade}
                        setAbordagem={setAbordagem}
                        setInstrucao={setInstrucao}
                        setSegundoSaque={setSegundoSaque}
                        compact
                      />

                      <div className="grid grid-cols-2 gap-2">
                        <button
                          onClick={() => {
                            setAjustandoPlanoRapido(false)
                            setSimulacaoPausada(false)
                          }}
                          className="py-3 border border-[#00e5ff]/25 arcade-font text-[9px] text-[#9ac9d8] text-center transition-all hover:border-[#00e5ff]/60"
                        >
                          SEGUIR SEM MUDAR
                        </button>
                        <NeonButton
                          variant="cyan"
                          className="text-[10px] py-3"
                          onClick={handleAplicarPausaRapida}
                        >
                          APLICAR E CONTINUAR
                        </NeonButton>
                      </div>
                    </>
                  )}
                </div>
              )}
            </div>
          )}

        {/* Encerrada — resultado */}
        <AnimatePresence>
          {fase === 'encerrada' && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`border-2 p-8 text-center ${
                placar.vencedor === 'jogador'
                  ? 'border-[#00ff88] bg-[#001a10]'
                  : 'border-[#ff0055] bg-[#1a0010]'
              }`}
            >
              <div
                className={`pixel-font text-4xl mb-3 ${
                  placar.vencedor === 'jogador' ? 'text-[#00ff88]' : 'text-[#ff0055]'
                }`}
              >
                {placar.vencedor === 'jogador' ? 'VITÓRIA!' : 'DERROTA'}
              </div>
              <div className="arcade-font text-base text-[#888]">
                {placar.placar_final || `${placar.sets[0]} × ${placar.sets[1]} sets`}
              </div>
              <div className="arcade-font text-[8px] text-[#7a8994] mt-3 tracking-widest">
                RESUMO DA PARTIDA EM INSTANTES...
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Entre-games */}
        <AnimatePresence>
          {fase === 'entre-games' && gameResult && (
            <motion.div
              key="entre-games"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="border-2 border-[#00e5ff] bg-[#00040d] p-4"
              style={{ boxShadow: '0 0 16px rgba(0,229,255,0.15)' }}
            >
	              <div className="flex items-center justify-between mb-4">
                <div>
                  <div
                    className="arcade-font text-[12px]"
                    style={{
                      color: gameResult.quemGanhou === 'jogador' ? '#00ff88' : '#ff4466',
                    }}
                  >
                    {gameResult.quemGanhou === 'jogador' ? '✓ GAME GANHO' : '✗ GAME PERDIDO'}
                  </div>
                  {gameResult.foiBreak && (
                    <div
                      className="arcade-font text-[9px] mt-0.5"
                      style={{
                        color: gameResult.quemGanhou === 'jogador' ? '#ff9900' : '#ff4444',
                      }}
                    >
                      {gameResult.quemGanhou === 'jogador' ? '⚡ BREAK!' : '⚡ BREAK SOFRIDO'}
                    </div>
                  )}
                </div>
	                <div className="arcade-font text-[13px] text-[#888]">
	                  {gameResult.placarGames[0]} – {gameResult.placarGames[1]}
	                </div>
	              </div>

              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="border border-[#00e5ff]/20 bg-[#04101b] px-3 py-2">
                  <div className="arcade-font text-[7px] text-[#5ba6bd] tracking-widest mb-1">MOMENTO</div>
                  <div className="arcade-font text-[9px] text-[#d6f2ff] uppercase">{resumoMomentum(momentum)}</div>
                </div>
                <div className="border border-[#00e5ff]/20 bg-[#04101b] px-3 py-2">
                  <div className="arcade-font text-[7px] text-[#5ba6bd] tracking-widest mb-1">PLANO ATUAL</div>
                  <div className="arcade-font text-[9px]" style={{ color: planoAtual.color }}>
                    {planoAtual.label}
                  </div>
                </div>
              </div>

              {ajustandoPlanoGame ? (
                <div className="space-y-4">
                  <div className="border border-[#00e5ff]/20 bg-[#04101b] p-3">
                    <div className="arcade-font text-[8px] text-[#5ba6bd] tracking-widest mb-3">MUDAR ESTRATÉGIA</div>
                    <TacticalPackageEditor
                      mentalidade={mentalidade}
                      abordagem={abordagem}
                      instrucao={instrucao}
                      segundoSaque={segundoSaque}
                      setMentalidade={setMentalidade}
                      setAbordagem={setAbordagem}
                      setInstrucao={setInstrucao}
                      setSegundoSaque={setSegundoSaque}
                      compact
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => setAjustandoPlanoGame(false)}
                      className="py-3 border border-[#00e5ff]/25 arcade-font text-[9px] text-[#9ac9d8] text-center transition-all hover:border-[#00e5ff]/60"
                    >
                      CANCELAR
                    </button>
                    <NeonButton
                      variant="cyan"
                      className="text-[10px] py-3"
                      onClick={handleContinuarGame}
                    >
                      APLICAR E JOGAR →
                    </NeonButton>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={handleContinuarGame}
                      disabled={simulando}
                      className="py-3 border border-[#00e5ff]/30 arcade-font text-[9px] text-[#9ac9d8] text-center transition-all hover:text-[#00e5ff] hover:border-[#00e5ff]/60 disabled:opacity-30"
                    >
                      MANTER ESTRATÉGIA
                    </button>
                    <NeonButton
                      variant="cyan"
                      className="text-[10px] py-3"
                      onClick={() => setAjustandoPlanoGame(true)}
                    >
                      MUDAR ESTRATÉGIA →
                    </NeonButton>
                  </div>
                </div>
              )}
	            </motion.div>
          )}
        </AnimatePresence>

        {/* Entre-sets */}
        <AnimatePresence>
          {fase === 'entre-sets' && (
            <motion.div
              key="entre-sets"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-40 flex items-center justify-center bg-black/70 backdrop-blur-[2px] p-4"
            >
              <motion.div
                initial={{ opacity: 0, y: 18, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 12, scale: 0.98 }}
                className="w-full max-w-3xl max-h-[88vh] overflow-y-auto border-2 border-[#ffe600] bg-[#0f0c00] p-5"
                style={{ boxShadow: '0 0 32px rgba(255,230,0,0.24)' }}
              >
                <div className="pixel-font text-[24px] text-[#ffe600] text-center mb-2">
                  SET ENCERRADO
                </div>
                <div className="arcade-font text-[11px] text-[#d6c97f] text-center mb-5 tracking-widest">
                  {placar.sets[0]} × {placar.sets[1]} — AJUSTE TÁTICO
                </div>

                <div className="grid grid-cols-2 gap-4 mb-5">
                  <div className="border border-[#ffe600]/24 bg-[#140f02] px-4 py-3">
                    <div className="arcade-font text-[10px] text-[#d8c46c] tracking-widest mb-2">VOCÊ</div>
                    <div className="arcade-font text-[13px] text-[#fff1a8]">Energia {Math.round(energiaJogadorAoVivo)}%</div>
                    <div className="arcade-font text-[13px] text-[#ffd86d] mt-1.5">Fadiga {Math.round(fadigaJogadorAoVivo)}%</div>
                  </div>
                  <div className="border border-[#ffe600]/24 bg-[#140f02] px-4 py-3">
                    <div className="arcade-font text-[10px] text-[#d8c46c] tracking-widest mb-2">ADVERSÁRIO</div>
                    <div className="arcade-font text-[13px] text-[#fff1a8]">Energia {Math.round(energiaAdversarioAoVivo)}%</div>
                    <div className="arcade-font text-[13px] text-[#ffd86d] mt-1.5">Fadiga {Math.round(fadigaAdversarioAoVivo)}%</div>
                  </div>
                </div>

                {/* Countdown bar */}
                {!ajustandoPlanoSet && (
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-1">
                      <span className="arcade-font text-[8px] text-[#ffe600]/60 tracking-widest">
                        AUTO-CONTINUA EM
                      </span>
                      <span
                        className="arcade-font text-[11px]"
                        style={{ color: contadorSet <= 3 ? '#ff0055' : '#ffe600' }}
                      >
                        {contadorSet}s
                      </span>
                    </div>
                    <div className="h-1 bg-white/10 w-full">
                      <motion.div
                        className="h-full"
                        style={{
                          background: contadorSet <= 3 ? '#ff0055' : '#ffe600',
                          width: `${(contadorSet / 10) * 100}%`,
                        }}
                        transition={{ duration: 0.3 }}
                      />
                    </div>
                  </div>
                )}

                {ajustandoPlanoSet ? (
                  <div className="space-y-4 mb-5">
                    <div className="border border-[#ffe600]/24 bg-[#140f02] p-4">
                      <div className="arcade-font text-[10px] text-[#d8c46c] tracking-widest mb-3">MUDAR ESTRATÉGIA</div>
                      <TacticalPackageEditor
                        mentalidade={mentalidade}
                        abordagem={abordagem}
                        instrucao={instrucao}
                        segundoSaque={segundoSaque}
                        setMentalidade={setMentalidade}
                        setAbordagem={setAbordagem}
                        setInstrucao={setInstrucao}
                        setSegundoSaque={setSegundoSaque}
                        compact
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <button
                        onClick={() => setAjustandoPlanoSet(false)}
                        className="py-3.5 border border-[#ffe600]/25 arcade-font text-[11px] text-[#d6c97f] text-center transition-all hover:border-[#ffe600]/50"
                      >
                        CANCELAR
                      </button>
                      <NeonButton
                        variant="yellow"
                        className="text-[12px] py-3.5"
                        onClick={handleContinuarSet}
                      >
                        APLICAR E CONTINUAR →
                      </NeonButton>
                    </div>
                  </div>
                ) : (
                  <>
                    {/* Quick 3-option tactic cards */}
                    <div className="grid grid-cols-3 gap-2 mb-4">
                      {PLANOS.map((p) => (
                        <button
                          key={p.valor}
                          onClick={() => handleEscolherPlanoSet(p.valor)}
                          disabled={simulando}
                          className="flex flex-col items-center gap-1.5 py-3 px-2 border-2 transition-all disabled:opacity-40 hover:scale-[1.02]"
                          style={{
                            borderColor: p.color + '60',
                            background: p.color + '0f',
                          }}
                          onMouseEnter={(e) => {
                            ;(e.currentTarget as HTMLElement).style.borderColor = p.color
                            ;(e.currentTarget as HTMLElement).style.background = p.color + '20'
                          }}
                          onMouseLeave={(e) => {
                            ;(e.currentTarget as HTMLElement).style.borderColor = p.color + '60'
                            ;(e.currentTarget as HTMLElement).style.background = p.color + '0f'
                          }}
                        >
                          <span
                            className="arcade-font text-[9px] font-bold tracking-widest"
                            style={{ color: p.color }}
                          >
                            {p.label}
                          </span>
                          <span className="text-[8px] text-white/50 text-center leading-relaxed">
                            {p.desc}
                          </span>
                        </button>
                      ))}
                    </div>

                    <div className="grid grid-cols-2 gap-2 mb-5">
                      <button
                        onClick={handleContinuarSet}
                        disabled={simulando}
                        className="py-3.5 border border-[#ffe600]/35 arcade-font text-[11px] text-[#e5d57b] text-center transition-all hover:text-[#ffe600] hover:border-[#ffe600]/60 disabled:opacity-30"
                      >
                        MANTER ESTRATÉGIA
                      </button>
                      <NeonButton
                        variant="yellow"
                        className="text-[12px] py-3.5"
                        onClick={() => setAjustandoPlanoSet(true)}
                      >
                        AJUSTE DETALHADO →
                      </NeonButton>
                    </div>
                  </>
                )}
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Simulando indicator */}
        {simulando && (
          <motion.div
            animate={{ opacity: [1, 0.4, 1] }}
            transition={{ duration: 0.6, repeat: Infinity }}
            className="text-center arcade-font text-[10px] text-[#ffe600] py-2"
          >
            ● SIMULANDO...
          </motion.div>
        )}

        {/* AÇÃO — estrategista */}
        {fase !== 'encerrada' && fase !== 'entre-games' && fase !== 'entre-sets' && modo === 'estrategista' && (
          <div className="border border-[#00e5ff]/30 bg-[#04101b]">
            <div className="arcade-font text-[8px] text-[#00e5ff] px-3 py-2 border-b border-[#00e5ff]/20 tracking-widest">
              ESCOLHA SUA AÇÃO
            </div>
            <div className="space-y-2 p-3">
              {INTENCOES.map((int) => (
                <button
                  key={int.valor}
                  onClick={() => handleIntencao(int.valor)}
                  disabled={fase !== 'aguardando' || simulando}
                  className="w-full border px-3 py-3 text-left transition-all disabled:opacity-25 active:scale-95"
                  style={{
                    borderColor: intencaoAtiva === int.valor ? int.color : '#1f3340',
                    background: intencaoAtiva === int.valor ? `${int.color}16` : 'transparent',
                  }}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="arcade-font text-[10px] font-bold" style={{ color: int.color }}>
                        {int.label}
                      </div>
                      <div className="arcade-font text-[9px] text-[#9fb8c7] mt-1">
                        {int.sub}
                      </div>
                    </div>
                    <div className="text-lg">{int.emoji}</div>
                  </div>
                </button>
              ))}
            </div>
            <div className="border-t border-[#00e5ff]/15 px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="arcade-font text-[8px] text-[#8aaac0] tracking-widest">AJUSTE FINO</div>
                  <div className="arcade-font text-[9px] text-[#6f8798] mt-1">
                    Se você não abrir, o jogo escolhe faixa e alvo compatíveis com a intenção.
                  </div>
                </div>
                <button
                  onClick={() => setExpandirPonto(prev => !prev)}
                  className="px-3 py-2 border arcade-font text-[8px] transition-all"
                  style={{
                    borderColor: expandirPonto ? '#00e5ff' : '#1a1a2e',
                    color: expandirPonto ? '#00e5ff' : '#66748d',
                    background: expandirPonto ? '#00e5ff10' : 'transparent',
                  }}
                >
                  {expandirPonto ? 'OCULTAR' : 'AJUSTAR'}
                </button>
              </div>

              {expandirPonto && (
                <div className="mt-3 grid grid-cols-1 gap-3">
                  <div>
                    <div className="arcade-font text-[8px] text-[#7e97a8] mb-2">FAIXA</div>
                    <div className="space-y-2">
                      {FAIXAS.map((f) => (
                        <button
                          key={f.valor}
                          onClick={() => setFaixa(f.valor)}
                          className="w-full py-2 border text-left px-3 text-[8px] arcade-font transition-all"
                          style={{
                            borderColor: faixa === f.valor ? '#00e5ff' : '#1a1a2e',
                            color: faixa === f.valor ? '#00e5ff' : '#7a8793',
                            background: faixa === f.valor ? '#00e5ff10' : 'transparent',
                          }}
                        >
                          {f.label}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <div className="arcade-font text-[8px] text-[#7e97a8] mb-2">ALVO</div>
                    <div className="space-y-2">
                      {ALVOS.map((a) => (
                        <button
                          key={a.valor}
                          onClick={() => setAlvo(a.valor)}
                          className="w-full py-2 border text-left px-3 text-[8px] arcade-font transition-all"
                          style={{
                            borderColor: alvo === a.valor ? '#ffe600' : '#1a1a2e',
                            color: alvo === a.valor ? '#ffe600' : '#8d8a6d',
                            background: alvo === a.valor ? '#ffe60010' : 'transparent',
                          }}
                        >
                          {a.label}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* STATUS — game/auto */}
        {fase !== 'encerrada' &&
          fase !== 'entre-games' &&
          fase !== 'entre-sets' &&
          (modo === 'game' || modo === 'auto') && (
            <div className="border border-[#1a1a2e] bg-black px-3 py-4">
              {simulando ? (
                <motion.div
                  animate={{ opacity: [1, 0.4, 1] }}
                  transition={{ duration: 0.5, repeat: Infinity }}
                  className="arcade-font text-[10px] text-[#00e5ff] text-center"
                >
                  ● SIMULANDO...
                </motion.div>
              ) : (
                <div className="space-y-2">
                  <div className="arcade-font text-[9px] text-[#93a4b2] uppercase">
                    {modo === 'game' ? 'o jogo vai pausar no fim de cada game' : 'a simulação vai até o fim automaticamente'}
                  </div>
                  <button
                    onClick={() => trocarModoAcompanhamento('estrategista')}
                    className="w-full border border-[#1f3340] px-3 py-2 arcade-font text-[9px] text-[#00e5ff] transition-all hover:bg-[#00e5ff10]"
                  >
                    VOLTAR PARA O CONTROLE MANUAL
                  </button>
                </div>
              )}
            </div>
          )}

      </div>

      {/* Bottom bar */}
      <div className="p-3 app-panel border-t border-[#1a1a2e] shrink-0 space-y-2">
        {fase === 'encerrada' ? (
          <div className="border border-[#1f3340] bg-[#09111a] px-4 py-3 text-center">
            <div className="arcade-font text-[8px] text-[#5b7182] tracking-widest">
              FECHANDO A PARTIDA
            </div>
          </div>
        ) : (
          <>
            <button
              onClick={handleDesistir}
              className="w-full py-2 border border-[#3a1020] text-[8px] arcade-font text-[#3a1020] hover:text-[#ff0055] hover:border-[#ff0055] transition-colors"
            >
              DESISTIR DA PARTIDA (W.O.)
            </button>
          </>
        )}
      </div>
    </div>
  )
}
