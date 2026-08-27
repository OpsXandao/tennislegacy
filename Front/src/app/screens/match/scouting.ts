import type { AdversarioInfo, ModoAcomp } from './types'
import { normSurface } from './uiUtils'

export function getScoutingMetrics(adv: AdversarioInfo) {
  const atr = adv.atributos ?? {}
  const psico = adv.atributosPsicologicos ?? {}
  const resumo = adv.resumoFifa ?? {}

  const saque = Number(resumo.SAQ ?? atr.saque ?? atr.vel_saque ?? 50)
  const fundo = Math.round(
    (
      Number(resumo.FOR ?? atr.forehand ?? 50) +
      Number(resumo.BAC ?? atr.backhand ?? 50) +
      Number(resumo.MOV ?? atr.movimento ?? atr.velocidade ?? 50) +
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
  const movimento = Number(atr.movimento ?? atr.velocidade ?? 50)

  return { saque, fundo, mental, voleio, winner, movimento }
}

export function getScoutingMetricsFromData(
  atributos?: Record<string, number>,
  atributosPsicologicos?: Record<string, number>,
  resumoFifa?: Record<string, number>,
) {
  return getScoutingMetrics({ atributos, atributosPsicologicos, resumoFifa } as AdversarioInfo)
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
