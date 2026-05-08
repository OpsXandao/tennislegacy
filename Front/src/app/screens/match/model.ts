import type { MatchStrategySummary, PlacarState } from '../../../types'
import type {
  AdversarioInfo,
  AbordagemValor,
  Faixa,
  InstrucaoValor,
  MentalidadeValor,
  ModoAcomp,
  PacoteTaticoState,
  PlanoValor,
  SegundoSaqueModo,
  Surface,
  Alvo,
  VelocidadeRapida,
} from './types'

export const ESTRATEGIA_PADRAO_UI: MatchStrategySummary = {
  estilo: 'atacar_do_fundo',
  saque: 'seguro',
  saque_tipo: 'variado',
  intencao: 'paciente',
}

export const PLANOS = [
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

export const MODOS_ACOMP = [
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

export const MODOS_VISIVEIS = MODOS_ACOMP.filter((m) => m.valor !== 'game')

export const VELOCIDADES_RAPIDAS = [
  { valor: 'lenta' as VelocidadeRapida, label: '1X', desc: 'Leitura confortável', delay: 1200 },
  { valor: 'normal' as VelocidadeRapida, label: '2X', desc: 'Ritmo padrão', delay: 700 },
  { valor: 'rapida' as VelocidadeRapida, label: '4X', desc: 'Clima Brasfoot', delay: 350 },
  { valor: 'turbo' as VelocidadeRapida, label: '8X', desc: 'Máxima velocidade', delay: 150 },
] as const

export const FAIXAS: { valor: Faixa; label: string }[] = [
  { valor: 'FUNDO', label: 'FND' },
  { valor: 'MEIO', label: 'MIO' },
  { valor: 'REDE', label: 'RDE' },
]

export const ALVOS: { valor: Alvo; label: string }[] = [
  { valor: 'ESQUERDA', label: 'ESQ' },
  { valor: 'CENTRO', label: 'CTR' },
  { valor: 'DIREITA', label: 'DIR' },
]

export const PLACAR_INICIAL: PlacarState = {
  sets: [0, 0],
  games: [0, 0],
  pontos: ['0', '0'],
  servindo: 'jogador',
  log: [],
  encerrado: false,
}

export const COURT_COLORS = { hard: '#1e3a5f', clay: '#8b3a1e', grass: '#1a4a25' } as const
export const MATCH_SETTINGS_KEY = 'tennislegacy.match.tactical-package'
export const MATCH_AUTOSAVE_KEY = 'tennislegacy.match.autosave'

export function normSurface(s?: string): Surface {
  const v = String(s ?? '').toLowerCase()
  if (v.includes('saibro') || v.includes('clay')) return 'clay'
  if (v.includes('grama') || v.includes('grass')) return 'grass'
  return 'hard'
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

export function derivarEstrategia(
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

export function inferirPlanoDoPacote(
  mentalidade: MentalidadeValor,
  abordagem: AbordagemValor,
  instrucao: InstrucaoValor,
): PlanoValor {
  if (mentalidade === 'OFENSIVA' || abordagem === 'SERVE_VOLLEY') return 'pressionar'
  if (mentalidade === 'DEFENSIVA' || abordagem === 'COUNTER' || instrucao === 'TROCAS_LONGAS') return 'consistencia'
  return 'variar'
}

export function carregarPacoteTaticoInicial(): PacoteTaticoState {
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

export function carregarPreferenciaAutoSave(): boolean {
  if (typeof window === 'undefined') return false
  return window.localStorage.getItem(MATCH_AUTOSAVE_KEY) === 'true'
}

export function estrategiaPonto(intencao: string, faixa: Faixa): string {
  if (faixa === 'REDE') return 'rede'
  if (intencao === 'ARRISCAR') return 'agressivo'
  if (intencao === 'DEFENSIVO') return 'defensivo'
  if (faixa === 'MEIO') return 'variado'
  return 'baseline'
}

export function inferirEstilo(atributos?: Record<string, number>): string {
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

export function flashColor(desc: string): string {
  const d = desc.toLowerCase()
  if (d.includes('ace')) return '#00ff88'
  if (d.includes('winner')) return '#ffe600'
  if (d.includes('break')) return '#ff9900'
  if (d.includes('erro') || d.includes('falta dupla')) return '#ff0055'
  return '#00e5ff'
}

export function getScoutingMetrics(adv: AdversarioInfo) {
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

export function getScoutingMetricsFromData(
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

export function calcularOverallCardMatch(metrics: {
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
  if (!hex.startsWith('#')) return hex
  const normalized = hex.length === 4
    ? `#${hex[1]}${hex[1]}${hex[2]}${hex[2]}${hex[3]}${hex[3]}`
    : hex
  return `${normalized}${opacity}`
}

export function resumoModo(modo: ModoAcomp): string {
  if (modo === 'estrategista') return 'VOCÊ DECIDE CADA PONTO.'
  if (modo === 'detalhado') return 'SIMULAÇÃO RÁPIDA COM VELOCIDADE AJUSTÁVEL E PAUSA TÁTICA.'
  if (modo === 'game') return 'MODO LEGADO: PAUSA AO FIM DE CADA GAME.'
  return 'A PARTIDA INTEIRA SERÁ SIMULADA.'
}

export function resumoMomentum(momentum: number): string {
  if (momentum >= 66) return 'VOCÊ ESTÁ PRESSIONANDO'
  if (momentum <= 34) return 'O ADVERSÁRIO ESTÁ MELHOR'
  return 'PARTIDA EQUILIBRADA'
}

export function corMomentum(momentum: number): string {
  if (momentum >= 66) return '#00ff88'
  if (momentum <= 34) return '#ff4466'
  return '#ffe600'
}

export function destaquePartida(placar: PlacarState, nomeJogador: string, nomeAdv: string, log: string[]): string {
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

export function tendenciaAdversario(adv: AdversarioInfo): string {
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

export function resumoScouting(adv: AdversarioInfo, superficie: string): { texto: string; dicas: string[]; pontosFortes: string[]; fraquezas: string[] } {
  const { saque, fundo, mental, voleio, winner, movimento } = getScoutingMetrics(adv)
  const atr = adv.atributos ?? {}
  const psico = adv.atributosPsicologicos ?? {}
  const surf = normSurface(superficie)

  const pontosFortes: string[] = []
  const fraquezas: string[] = []
  const dicas: string[] = []

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

  if (movimento >= 80) {
    pontosFortes.push('COBERTURA ELITE')
    dicas.push('Use o contra-pé. Ele corre tão rápido que muitas vezes não consegue frear para voltar.')
  } else if (movimento <= 58) {
    fraquezas.push('MOBILIDADE REDUZIDA')
    dicas.push('Mova-o lateralmente o tempo todo. Ele perde precisão quando precisa bater correndo.')
    if (saque >= 75) dicas.push('O plano dele é sacar e definir logo; se você devolver fundo, ele sofrerá no rally.')
  }

  if (voleio >= 75) {
    pontosFortes.push('MESTRE DO VOLEIO')
    dicas.push('Evite jogar bolas altas ou lentas quando ele estiver na rede; use o "dip" nos pés dele.')
    if (atr.slice >= 70) dicas.push('Ele usa muito o slice para preparar a subida. Esteja atento à mudança de ritmo.')
  } else if (voleio <= 50) {
    fraquezas.push('INSEGURO NA REDE')
    dicas.push('Traga-o para a rede com curtinhas; ele costuma se atrapalhar em bolas baixas perto da fita.')
  }

  if (mental >= 80) {
    pontosFortes.push('GELO NAS VEIAS')
    dicas.push('Não espere "presentes" em Match Points. Você terá que ganhar o ponto por mérito.')
  } else if (mental <= 60) {
    fraquezas.push('MENTAL OSCILANTE')
    dicas.push('Se você forçar um tiebreak ou um set longo, a confiança dele despenca.')
    if (psico.determinacao < 50) dicas.push('Ele costuma desistir mentalmente de sets se estiver uma quebra abaixo.')
  }

  if (adv.energia < 60) {
    fraquezas.push('EXAUSTÃO VISÍVEL')
    dicas.push('Alongue todos os rallies. Ele não tem pernas para um jogo de 3 sets hoje.')
  }

  if (pontosFortes.length === 0) pontosFortes.push('EQUILIBRADO')

  let texto = `${adv.nome} tem um perfil `
  if (saque >= 75 && voleio >= 70) texto += "de 'Serve & Volleyer' clássico, pressionando o tempo todo."
  else if (fundo >= 75 && movimento >= 75) texto += "de 'Counter-Puncher', uma parede impossível de ultrapassar."
  else if (winner >= 75 && saque >= 70) texto += 'agressivo, que tenta ditar o ritmo com golpes potentes.'
  else texto += 'versátil, adaptando-se ao que a partida exige.'

  return {
    texto,
    dicas: dicas.sort(() => 0.5 - Math.random()).slice(0, 3),
    pontosFortes: pontosFortes.slice(0, 3),
    fraquezas: fraquezas.slice(0, 3),
  }
}

export function montarRelatorioJogador(args: {
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

export function resumirHistoricoRival(
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

export function resumirTitulosRival(trofeus?: Array<Record<string, unknown>>): string[] {
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

export function recomendacaoPlano(
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

export function serializarPacoteTatico(
  mentalidade: MentalidadeValor,
  abordagem: AbordagemValor,
  instrucao: InstrucaoValor,
  segundoSaque: SegundoSaqueModo,
): string {
  return `fm|${mentalidade}|${abordagem}|${instrucao}|${segundoSaque}`
}

export function traduzirCampoEstrategia(valor?: string): string {
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

export function resumirEstrategiaLado(estrategia?: MatchStrategySummary): string[] {
  const dados = { ...ESTRATEGIA_PADRAO_UI, ...(estrategia ?? {}) }
  return [
    `Estilo: ${traduzirCampoEstrategia(dados.estilo)}`,
    `Intenção: ${traduzirCampoEstrategia(dados.intencao)}`,
    `1º saque: ${traduzirCampoEstrategia(dados.saque_tipo)}`,
    `2º saque: ${traduzirCampoEstrategia(dados.saque)}`,
  ]
}
