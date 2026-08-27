import type { PlacarState } from '../../../types'

interface ScoutingNarrativo {
  texto?: string
  dicas?: string[]
  pontosFortes?: string[]
  fraquezas?: string[]
}

export interface MatchBriefingNarrativo {
  manchete: string
  contexto: string
  conflito: string
  plano: string
}

export interface MatchStoryBeat {
  titulo: string
  texto: string
  cor: string
}

// ─── Headline ─────────────────────────────────────────────────────────────────

export function gerarTituloPartida(
  placar: PlacarState,
  nomeJogador: string,
  nomeAdversario: string,
): string {
  const ganhou = placar.vencedor === 'jogador'
  const sj = placar.stats_j
  const sa = placar.stats_a
  const sobrenomeJ = nomeJogador.split(' ').pop()!.toUpperCase()
  const sobrenomeA = nomeAdversario.split(' ').pop()!.toUpperCase()
  const sets = `${placar.sets[0]}×${placar.sets[1]}`

  if (ganhou) {
    const dominante = sj && sa && sj.winners >= sa.winners + 6 && sa.erros_nao_forcados >= sj.erros_nao_forcados + 5
    const suado = placar.sets[1] > 0 && placar.sets[0] <= 2
    const remontada = placar.sets[1] > 0 && placar.sets[0] > placar.sets[1]

    if (remontada) return `REMONTADA DE ${sobrenomeJ} — ${sets}`
    if (dominante) return `${sobrenomeJ} DOMINA: ${sets} SETS`
    if (suado) return `NO FIO DA NAVALHA — ${sets}`
    return `${sobrenomeJ} VENCE EM ${sets}`
  } else {
    const dominado = sj && sa && sa.winners >= sj.winners + 6
    const lutou = placar.sets[0] > 0

    if (dominado) return `${sobrenomeA} IMPÕE RITMO — ${sets}`
    if (lutou) return `DERROTA HONRADA — ${sets}`
    return `${sobrenomeA} PASSA DIRETO — ${sets}`
  }
}

// ─── Story paragraph ──────────────────────────────────────────────────────────

export function gerarNarrativaPartida(
  placar: PlacarState,
  nomeJogador: string,
  nomeAdversario: string,
  log: string[],
): string {
  const ganhou = placar.vencedor === 'jogador'
  const sj = placar.stats_j
  const sa = placar.stats_a
  const nomeJ = nomeJogador.split(' ').pop()!
  const nomeA = nomeAdversario.split(' ').pop()!
  const parts: string[] = []

  // Abertura — como a partida começou
  if (sj && sa) {
    const acesJ = sj.aces ?? 0
    const acesA = sa.aces ?? 0
    if (acesJ >= 8) parts.push(`${nomeJ} entrou em quadra com o saque em chamas — ${acesJ} aces ao longo da partida deram o tom.`)
    else if (acesA >= 8) parts.push(`${nomeA} dominou o saque desde o início, acumulando ${acesA} aces.`)
    else if (sj.erros_nao_forcados > sa.erros_nao_forcados + 6) parts.push(`O início foi difícil para ${nomeJ}, que cometeu erros demais nos momentos-chave.`)
    else if (sa.erros_nao_forcados > sj.erros_nao_forcados + 6) parts.push(`${nomeA} se autossabotou com excesso de erros não forçados, abrindo espaço para o adversário.`)
    else parts.push(`A partida começou equilibrada — os dois jogadores se estudaram antes de assumir risco.`)
  }

  // Reviravolta — ponto de tensão
  const breakJ = String(sj?.break_points ?? '').match(/^(\d+)\/(\d+)$/)
  const breakA = String(sa?.break_points ?? '').match(/^(\d+)\/(\d+)$/)
  if (breakJ && parseInt(breakJ[1]) >= 2) {
    parts.push(`${nomeJ} foi decisivo nos momentos de break, convertendo ${breakJ[1]} de ${breakJ[2]} oportunidades.`)
  } else if (breakA && parseInt(breakA[1]) >= 2) {
    parts.push(`${nomeA} aproveitou as chances de quebra — ${breakA[1]} de ${breakA[2]} convertidas pesaram no placar.`)
  } else if (placar.sets[0] + placar.sets[1] >= 4) {
    parts.push(`A decisão veio nos momentos mais tensos — cada game foi disputado como se fosse o último.`)
  }

  // Resolução — desfecho
  if (ganhou) {
    const winners = sj?.winners ?? 0
    if (winners >= 20) parts.push(`No final, os ${winners} winners de ${nomeJ} foram o argumento mais forte da noite.`)
    else if (placar.sets[1] === 0) parts.push(`${nomeJ} não deu chances e fechou sem ceder um set sequer.`)
    else parts.push(`A virada de ${nomeJ} mostrou que resistência também é uma forma de talento.`)
  } else {
    const winners = sa?.winners ?? 0
    if (winners >= 20) parts.push(`${nomeA} foi cirúrgico com ${winners} winners — não sobrou espaço para reação.`)
    else if (placar.sets[0] === 0) parts.push(`Uma derrota que dói, mas que ensina. Há pontos fracos para corrigir antes do próximo round.`)
    else parts.push(`${nomeJ} lutou até o fim, mas ${nomeA} teve mais recursos quando mais importava.`)
  }

  // Gancho final do log
  const ultimoMomento = [...log].reverse().find(l => l && l.length > 10)
  if (ultimoMomento) parts.push(`Último momento registrado: "${ultimoMomento}".`)

  return parts.join(' ')
}

export function gerarBriefingNarrativo(args: {
  nomeJogador: string
  nomeAdversario: string
  superficie: string
  planoExecutivo: string
  reportJogador?: ScoutingNarrativo | null
  scoutRival?: ScoutingNarrativo | null
}): MatchBriefingNarrativo {
  const {
    nomeJogador,
    nomeAdversario,
    superficie,
    planoExecutivo,
    reportJogador,
    scoutRival,
  } = args

  const piso = String(superficie || 'quadra').toLowerCase()
  const contexto =
    piso.includes('saibro')
      ? 'No saibro, a partida tende a premiar paciência, físico e construção.'
      : piso.includes('grama')
        ? 'Na grama, tudo acelera: saque, transição e leitura da primeira bola.'
        : piso.includes('dura') || piso.includes('hard')
          ? 'Na quadra dura, quem controla o tempo do ponto costuma mandar no jogo.'
          : 'A quadra de hoje favorece quem ler melhor o ritmo da partida.'

  const conflito =
    scoutRival?.texto
      ? `${nomeAdversario} chega com uma identidade clara: ${scoutRival.texto}`
      : `${nomeAdversario} é o problema da vez. A questão é quem impõe padrão primeiro.`

  const dicaRival = scoutRival?.dicas?.[0]
  const dicaJogador = reportJogador?.dicas?.[0]
  const plano = dicaRival || dicaJogador
    ? `${planoExecutivo} ${dicaRival ?? dicaJogador}`
    : planoExecutivo

  return {
    manchete: `${nomeJogador} vs ${nomeAdversario}`,
    contexto,
    conflito,
    plano,
  }
}

export function gerarBeatsPosJogo(
  placar: PlacarState,
  nomeJogador: string,
  nomeAdversario: string,
  log: string[],
): MatchStoryBeat[] {
  const sj = placar.stats_j
  const sa = placar.stats_a
  const beats: MatchStoryBeat[] = []

  if (sj && sa) {
    const diffWinners = (sj.winners ?? 0) - (sa.winners ?? 0)
    const diffErros = (sa.erros_nao_forcados ?? 0) - (sj.erros_nao_forcados ?? 0)
    const rallyLongo = (sj.rallies_longos ?? 0) + (sa.rallies_longos ?? 0)
    const breakJ = String(sj.break_points ?? '0/0')
    const breakA = String(sa.break_points ?? '0/0')

    if (Math.abs(diffWinners) >= 4) {
      beats.push({
        titulo: 'GOLPE DE IMPACTO',
        texto: diffWinners > 0
          ? `${nomeJogador} encontrou mais bolas de definição e desequilibrou nos winners.`
          : `${nomeAdversario} acelerou melhor os pontos importantes e venceu no poder de fogo.`,
        cor: diffWinners > 0 ? 'var(--neon-green)' : 'var(--neon-pink)',
      })
    }

    if (Math.abs(diffErros) >= 4) {
      beats.push({
        titulo: 'DISCIPLINA DE QUADRA',
        texto: diffErros > 0
          ? `${nomeJogador} sustentou melhor a execução e forçou o rival a ceder mais pontos.`
          : `${nomeAdversario} ofereceu menos erros e empurrou ${nomeJogador} para fora da zona de conforto.`,
        cor: diffErros > 0 ? 'var(--neon-green)' : 'var(--neon-yellow)',
      })
    }

    if (breakJ !== '0/0' || breakA !== '0/0') {
      beats.push({
        titulo: 'PONTOS GRANDES',
        texto: `${nomeJogador} converteu ${breakJ}; ${nomeAdversario} respondeu com ${breakA}. Os games de saque decidiram a narrativa da partida.`,
        cor: 'var(--neon-cyan)',
      })
    }

    if (rallyLongo >= 12) {
      beats.push({
        titulo: 'BATALHA FÍSICA',
        texto: 'As trocas longas pesaram no roteiro da partida. Quem manteve a lucidez física sobreviveu melhor ao desgaste.',
        cor: 'var(--neon-yellow)',
      })
    }
  }

  const ultimoMomento = [...log].reverse().find((item) => item && item.length > 12)
  if (ultimoMomento) {
    beats.push({
      titulo: 'ÚLTIMO RECORTE',
      texto: ultimoMomento,
      cor: 'var(--neon-cyan)',
    })
  }

  return beats.slice(0, 3)
}

// ─── Career chapter ───────────────────────────────────────────────────────────

export interface CareerChapter {
  titulo: string
  descricao: string
  cor: string
  proximoMarco: string
  proximoRanking: number | null
}

export function calcularCapituloCarreira(ranking: number, nivel: number): CareerChapter {
  if (ranking > 500) return {
    titulo: 'CAPÍTULO I — O INÍCIO',
    descricao: 'O circuito mal sabe seu nome. Cada ponto, uma conquista.',
    cor: 'var(--neon-cyan)',
    proximoMarco: 'Entrar no TOP 500',
    proximoRanking: 500,
  }
  if (ranking > 250) return {
    titulo: 'CAPÍTULO II — DESCOBERTO',
    descricao: 'Os resultados começam a aparecer. Alguns adversários já estudam seu jogo.',
    cor: 'var(--neon-cyan)',
    proximoMarco: 'Entrar no TOP 250',
    proximoRanking: 250,
  }
  if (ranking > 100) return {
    titulo: 'CAPÍTULO III — ESTABELECIDO',
    descricao: 'Um nome respeitado no circuito. Os grandes torneios ficam mais próximos.',
    cor: 'var(--neon-green)',
    proximoMarco: 'Entrar no TOP 100',
    proximoRanking: 100,
  }
  if (ranking > 50) return {
    titulo: 'CAPÍTULO IV — CANDIDATO',
    descricao: 'Você está entre os melhores. A elite está ao alcance da mão.',
    cor: 'var(--neon-green)',
    proximoMarco: 'Entrar no TOP 50',
    proximoRanking: 50,
  }
  if (ranking > 20) return {
    titulo: 'CAPÍTULO V — ELITE',
    descricao: 'Nos grandes palcos, seu nome provoca cautela nos adversários.',
    cor: 'var(--neon-yellow)',
    proximoMarco: 'Entrar no TOP 20',
    proximoRanking: 20,
  }
  if (ranking > 10) return {
    titulo: 'CAPÍTULO VI — ESTRELA',
    descricao: 'O mundo do tênis acompanha seu jogo. A imprensa quer entrevistas.',
    cor: 'var(--neon-yellow)',
    proximoMarco: 'Entrar no TOP 10',
    proximoRanking: 10,
  }
  if (ranking > 5) return {
    titulo: 'CAPÍTULO VII — LENDA EM ASCENSÃO',
    descricao: 'Você está entre os dez melhores do planeta. Cada partida é histórica.',
    cor: '#ff9900',
    proximoMarco: 'Entrar no TOP 5',
    proximoRanking: 5,
  }
  if (ranking > 1) return {
    titulo: 'CAPÍTULO VIII — PRETENDENTE',
    descricao: 'O trono está à vista. Toda a carreira convergiu para este momento.',
    cor: 'var(--neon-pink)',
    proximoMarco: 'Conquistar o Nº 1',
    proximoRanking: 1,
  }
  return {
    titulo: 'CAPÍTULO IX — O NÚMERO 1',
    descricao: 'Você é o padrão. Os outros medem seu sucesso pelo seu.',
    cor: 'var(--neon-yellow)',
    proximoMarco: 'Defender a posição',
    proximoRanking: null,
  }
}

// ─── Ranking milestone ────────────────────────────────────────────────────────

const MILESTONE_KEY = 'tennislegacy.milestone.ranking'

const MILESTONES: { ranking: number; titulo: string; texto: string }[] = [
  { ranking: 500, titulo: 'TOP 500 ALCANÇADO', texto: 'Você entrou no radar do circuito profissional.' },
  { ranking: 250, titulo: 'TOP 250 ALCANÇADO', texto: 'Seu nome começa a ser pronunciado nas salas de análise.' },
  { ranking: 100, titulo: 'TOP 100 ALCANÇADO', texto: 'Entrada direta nos Grand Slams. Você chegou ao seleto grupo de 100.' },
  { ranking: 50,  titulo: 'TOP 50 ALCANÇADO',  texto: 'Cabeças de chave em torneios grandes. A elite o reconhece.' },
  { ranking: 20,  titulo: 'TOP 20 ALCANÇADO',  texto: 'Você disputa os títulos mais prestigiosos do circuito.' },
  { ranking: 10,  titulo: 'TOP 10 ALCANÇADO',  texto: 'Dez melhores do mundo. Uma raridade que pouquíssimos atingem.' },
  { ranking: 5,   titulo: 'TOP 5 ALCANÇADO',   texto: 'Você está entre os cinco melhores jogadores do planeta.' },
  { ranking: 1,   titulo: 'Nº 1 DO MUNDO',     texto: 'O topo. Não há mais para onde subir — apenas defender.' },
]

export function checarMarcoRanking(
  ranking: number,
): { titulo: string; texto: string } | null {
  const lastSeen = parseInt(localStorage.getItem(MILESTONE_KEY) ?? '9999', 10)
  for (const m of MILESTONES) {
    if (ranking <= m.ranking && lastSeen > m.ranking) {
      localStorage.setItem(MILESTONE_KEY, String(m.ranking))
      return { titulo: m.titulo, texto: m.texto }
    }
  }
  return null
}

// ─── Pre-match narrative context ─────────────────────────────────────────────

export interface ContextoPartida {
  tipo: 'revanche' | 'rival' | 'historico' | 'estreia' | 'top10' | 'grandslam' | 'comum'
  label: string
  texto: string
  cor: string
}

interface HistoricoVsAdversario {
  vitorias: number
  derrotas: number
  confrontos: number
  ultimoResultado?: 'V' | 'D'
  ultimaFase?: string
  ultimoTorneio?: string
  semanaUltima?: number
  semanaAtual?: number
}

export function gerarContextoPartida(
  nomeAdversario: string,
  rankingAdversario: number,
  faseTorneio: string,
  nomeTorneio: string,
  historico: HistoricoVsAdversario,
): ContextoPartida {
  const sobrenome = nomeAdversario.split(' ').pop()!
  const { vitorias, derrotas, confrontos, ultimoResultado, ultimaFase, ultimoTorneio, semanaUltima, semanaAtual } = historico

  // Grand Slam — sempre o contexto mais dramático
  const isGrandSlam = nomeTorneio?.toLowerCase().includes('open') ||
    nomeTorneio?.toLowerCase().includes('wimbledon') ||
    nomeTorneio?.toLowerCase().includes('roland') ||
    nomeTorneio?.toLowerCase().includes('australian')
  if (isGrandSlam && (faseTorneio === 'semifinal' || faseTorneio === 'final')) {
    return {
      tipo: 'grandslam',
      label: faseTorneio === 'final' ? '🏆 GRANDE FINAL' : '⚡ SEMIFINAL',
      texto: faseTorneio === 'final'
        ? `${nomeTorneio}. Uma final de Grand Slam não se repete — ou você está preparado, ou não está.`
        : `Uma semifinal de Grand Slam. O passo mais difícil antes do sonho.`,
      cor: 'var(--neon-yellow)',
    }
  }

  // Revanche — perdeu para este adversário recentemente
  const semanasDesdeUltima = semanaAtual && semanaUltima ? semanaAtual - semanaUltima : 99
  if (ultimoResultado === 'D' && semanasDesdeUltima <= 12) {
    return {
      tipo: 'revanche',
      label: '🔥 REVANCHE',
      texto: semanasDesdeUltima <= 4
        ? `${sobrenome} te eliminou há ${semanasDesdeUltima} semanas ${ultimaFase ? `nas ${ultimaFase}` : ''} de ${ultimoTorneio ?? 'um torneio anterior'}. A memória ainda dói.`
        : `Você perdeu para ${sobrenome} em ${ultimoTorneio ?? 'um torneio recente'}. É hora de acertar as contas.`,
      cor: 'var(--neon-pink)',
    }
  }

  // Rival histórico — muitos confrontos
  if (confrontos >= 5) {
    const winRate = confrontos > 0 ? Math.round((vitorias / confrontos) * 100) : 0
    const dominante = winRate >= 65 ? `Você domina o confronto.` : winRate <= 35 ? `${sobrenome} tem dominado o confronto.` : `O equilíbrio define esta rivalidade.`
    return {
      tipo: 'rival',
      label: `⚔ RIVALIDADE — ${vitorias}V ${derrotas}D`,
      texto: `${confrontos} partidas entre vocês. ${dominante} Cada vez que se encontram, algo está em jogo.`,
      cor: confrontos >= 10 ? 'var(--neon-yellow)' : 'var(--neon-cyan)',
    }
  }

  // Adversário no Top 10
  if (rankingAdversario <= 10) {
    return {
      tipo: 'top10',
      label: `👑 TOP 10 — Nº ${rankingAdversario}`,
      texto: confrontos === 0
        ? `Primeira vez contra um top 10. Estes são os jogadores que definem o circuito.`
        : `${sobrenome} está no top 10. Cada vitória aqui vale mais do que pontos.`,
      cor: 'var(--neon-yellow)',
    }
  }

  // Primeiro encontro
  if (confrontos === 0) {
    return {
      tipo: 'estreia',
      label: '⚡ ESTREIA',
      texto: `Primeira vez enfrentando ${sobrenome}. Não há histórico para se apoiar — é puro tênis.`,
      cor: 'var(--neon-cyan)',
    }
  }

  // Confronto com histórico positivo
  if (vitorias > derrotas && confrontos >= 2) {
    return {
      tipo: 'historico',
      label: `✓ ${vitorias}V ${derrotas}D`,
      texto: `Você conhece o jogo de ${sobrenome}. Mas cada partida é uma nova história.`,
      cor: 'var(--neon-green)',
    }
  }

  return {
    tipo: 'comum',
    label: confrontos > 0 ? `${vitorias}V ${derrotas}D` : 'PARTIDA',
    texto: `Uma partida de tênis. No fim, só um sai vitorioso.`,
    cor: 'var(--neon-cyan)',
  }
}

// ─── Career event feed ────────────────────────────────────────────────────────

export interface CareerEvent {
  id: string
  tipo: 'streak' | 'queda' | 'ascensao' | 'marco' | 'rival' | 'motivacao'
  titulo: string
  texto: string
  cor: string
  icone: string
}

interface MatchEntry { resultado: 'V' | 'D'; torneio: string; fase: string; adversario: string }
interface RivData { nome: string; confrontos: number; vitorias: number; win_rate: number; rival_ativo: boolean }

export function gerarEventosCarreira(params: {
  historico: MatchEntry[]
  rivalidades: RivData[]
  ranking: number
  rankingAnterior: number
  nivel: number
  semana: number
  nomeJogador: string
}): CareerEvent[] {
  const { historico, rivalidades, ranking, rankingAnterior, nivel, semana, nomeJogador } = params
  const sobrenome = nomeJogador.split(' ').pop()!
  const events: CareerEvent[] = []
  const recentes = historico.slice(0, 10)

  // Sequência de vitórias
  const streak = (() => {
    let s = 0
    for (const m of recentes) {
      if (m.resultado === 'V') s++
      else break
    }
    return s
  })()

  if (streak >= 5) {
    events.push({
      id: `streak-${streak}`,
      tipo: 'streak',
      titulo: `${streak} VITÓRIAS SEGUIDAS`,
      texto: `${sobrenome} está em chamas. ${streak} vitórias consecutivas colocam seu nome na boca do circuito.`,
      cor: 'var(--neon-green)',
      icone: '🔥',
    })
  } else if (streak >= 3) {
    events.push({
      id: `streak-${streak}`,
      tipo: 'streak',
      titulo: `SEQUÊNCIA DE ${streak}`,
      texto: `Três seguidas. O ritmo está chegando. Não pare agora.`,
      cor: 'var(--neon-cyan)',
      icone: '📈',
    })
  }

  // Sequência de derrotas
  const lossStreak = (() => {
    let s = 0
    for (const m of recentes) {
      if (m.resultado === 'D') s++
      else break
    }
    return s
  })()

  if (lossStreak >= 3) {
    events.push({
      id: `queda-${lossStreak}`,
      tipo: 'queda',
      titulo: `${lossStreak} DERROTAS SEGUIDAS`,
      texto: `Esta fase passa. Todo campeão já esteve neste lugar — o que define é o que você faz agora.`,
      cor: 'var(--neon-pink)',
      icone: '⚠',
    })
  }

  // Movimento de ranking
  const deltaRanking = rankingAnterior - ranking
  if (deltaRanking >= 20 && ranking > 0) {
    events.push({
      id: `ascensao-${semana}`,
      tipo: 'ascensao',
      titulo: `↑ ${deltaRanking} POSIÇÕES`,
      texto: `Do nº ${rankingAnterior} ao nº ${ranking}. O circuito está percebendo.`,
      cor: 'var(--neon-green)',
      icone: '⬆',
    })
  } else if (deltaRanking <= -15) {
    events.push({
      id: `queda-rank-${semana}`,
      tipo: 'queda',
      titulo: `↓ ${Math.abs(deltaRanking)} POSIÇÕES`,
      texto: `O ranking caiu. Os pontos expiram — é assim que o circuito funciona. Hora de ganhar de volta.`,
      cor: 'var(--neon-pink)',
      icone: '⬇',
    })
  }

  // Rival ativo
  const rivalAtivo = rivalidades.find(r => r.rival_ativo && r.confrontos >= 3)
  if (rivalAtivo) {
    const winRate = Math.round(rivalAtivo.win_rate * 100)
    events.push({
      id: `rival-${rivalAtivo.nome}`,
      tipo: 'rival',
      titulo: `RIVALIDADE — ${rivalAtivo.nome.split(' ').pop()!.toUpperCase()}`,
      texto: winRate >= 50
        ? `Você lidera o confronto ${rivalAtivo.vitorias}V–${rivalAtivo.confrontos - rivalAtivo.vitorias}D. A rivalidade ainda está viva.`
        : `${rivalAtivo.nome.split(' ').pop()} lidera o confronto. Cada encontro é uma chance de mudar a história.`,
      cor: winRate >= 50 ? 'var(--neon-cyan)' : 'var(--neon-yellow)',
      icone: '⚔',
    })
  }

  // Marco de nível
  if (nivel % 5 === 0 && nivel > 0) {
    events.push({
      id: `marco-nivel-${nivel}`,
      tipo: 'marco',
      titulo: `NÍVEL ${nivel} — MARCO`,
      texto: `Cada ponto de evolução foi ganho em quadra. O jogador que você é hoje não é o mesmo de quando começou.`,
      cor: 'var(--neon-yellow)',
      icone: '⭐',
    })
  }

  // Motivação padrão se não há eventos
  if (events.length === 0) {
    const motivacoes = [
      { t: 'SEMANA DE TRABALHO', tx: 'O circuito não espera. Cada semana é uma nova janela para acumular pontos e avançar.' },
      { t: 'PRÓXIMO TORNEIO', tx: 'A consistência é o que separa quem aparece uma vez de quem constrói uma carreira.' },
      { t: 'FOCO', tx: 'Não existem partidas pequenas. Cada vitória conta, cada derrota ensina.' },
    ]
    const m = motivacoes[semana % motivacoes.length]
    events.push({ id: `motivacao-${semana}`, tipo: 'motivacao', titulo: m.t, texto: m.tx, cor: 'var(--neon-cyan)', icone: '🎾' })
  }

  return events.slice(0, 3)
}
