import { useEffect, useRef, useState, useCallback } from 'react'
import { useNavigate } from 'react-router'
import { NeonButton } from '../components/NeonButton'
import { api, ApiError } from '../../api/client'
import { useGameStore } from '../../store/gameStore'
import type {
  AdversarioInfo as ApiAdversarioInfo,
  JogadorState,
  MatchPointRuntime,
  MatchStrategySummary,
  PlacarState,
} from '../../types'
import type {
  AdversarioInfo,
  Alvo,
  Faixa,
  Fase,
  GameResult,
  InstrucaoValor,
  MentalidadeValor,
  ModoAcomp,
  PlanoValor,
  SegundoSaqueModo,
  VelocidadeRapida,
  AbordagemValor,
} from './match/types'
import {
  ESTRATEGIA_PADRAO_UI,
  MATCH_SETTINGS_KEY,
  PLANOS,
  PLACAR_INICIAL,
  VELOCIDADES_RAPIDAS,
  accentFromCarta,
  calcMomentum,
  calcularOverallCardMatch,
  carregarPacoteTaticoInicial,
  carregarPreferenciaAutoSave,
  corMomentum,
  detectBreakPoint,
  detectarPontoCritico,
  estrategiaPonto,
  flashColor,
  getScoutingMetrics,
  getScoutingMetricsFromData,
  inferirEstilo,
  inferirPlanoDoPacote,
  leituraFisica,
  montarRelatorioJogador,
  normSurface,
  rankingValido,
  resumirEstrategiaLado,
  resumirHistoricoRival,
  resumirTitulosRival,
  resumoModo,
  resumoMomentum,
  serializarPacoteTatico,
} from './match/model'
import {
  criarEventoLocalDePlacar,
  extrairAtualizacaoRuntime,
  extrairAdversarioInfoPartida,
  extrairHistoricoJogador,
  extrairHistoricoTorneiosJogador,
  extrairTrofeusJogador,
  mapApiAdversarioParaMatch,
  modoAcompanhamentoDaApi,
} from './match/bootstrap'
import {
  ABORDAGENS,
  INSTRUCOES,
  MENTALIDADES,
} from './match/components'

import { SetupView } from './match/views/SetupView'
import { PostMatchView } from './match/views/PostMatchView'
import { useOpponentScouting } from './match/useOpponentScouting'
import { InGameView } from './match/views/InGameView'

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
  const [jogadorPosjogo, setJogadorPosjogo] = useState<JogadorState | null>(null)
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
      setModo(modoAcompanhamentoDaApi(res.config.modo))
      if (res.adversario) applyAdversario(res.adversario)
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
      setFaseTorneio(String(t.fase_atual ?? ''))
      const adversarioPartida = extrairAdversarioInfoPartida(t, nomeJogador)
      if (adversarioPartida) {
        applyAdversario(adversarioPartida)
      }
    }).catch((err) => {
      console.error("Erro ao carregar estado do torneio no setup:", err)
    })
    api.partida.preview().then((res) => {
      if (res?.adversario) applyAdversario(res.adversario)
    }).catch((err) => {
      console.error("Erro ao carregar preview da partida:", err)
    })
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
      setModo(modoAcompanhamentoDaApi(ativa.config.modo))
      if (ativa.adversario) applyAdversario(ativa.adversario)
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

  function applyAdversario(adv: ApiAdversarioInfo) {
    if (!adv) return
    const matchAdversario = mapApiAdversarioParaMatch(adv)
    setAdversario(matchAdversario)
    setEnergiaJogadorAoVivo(Number(jogador?.energia ?? 100))
    setFadigaJogadorAoVivo(Number(jogador?.fadiga ?? 0))
    setEnergiaAdversarioAoVivo(matchAdversario.energia)
    setFadigaAdversarioAoVivo(matchAdversario.fadiga)
  }

  // ─── Apply placar update ──────────────────────────────────────────────────

  const aplicar = useCallback((estado: MatchPointRuntime | PlacarState) => {
    const atualizacao = extrairAtualizacaoRuntime(estado)
    const prevGames: [number, number] = [lastPlacar.current.games[0], lastPlacar.current.games[1]]
    const prevServindo = lastPlacar.current.servindo

    setPlacar(atualizacao.placar)
    lastPlacar.current = atualizacao.placar
    if (atualizacao.energiaJogador !== null) {
      setEnergiaJogadorAoVivo(atualizacao.energiaJogador)
    }
    if (atualizacao.fadigaJogador !== null) {
      setFadigaJogadorAoVivo(atualizacao.fadigaJogador)
    }
    if (atualizacao.estrategiaJogador) {
      setEstrategiaJogadorAoVivo(atualizacao.estrategiaJogador)
    }
    if (atualizacao.estrategiaAdversario) {
      setEstrategiaAdversarioAoVivo(atualizacao.estrategiaAdversario)
    }
    if (atualizacao.energiaAdversario !== null || atualizacao.fadigaAdversario !== null) {
      if (atualizacao.energiaAdversario !== null) {
        setEnergiaAdversarioAoVivo(atualizacao.energiaAdversario)
      }
      if (atualizacao.fadigaAdversario !== null) {
        setFadigaAdversarioAoVivo(atualizacao.fadigaAdversario)
      }
      setAdversario(prev => ({
        ...prev,
        energia: atualizacao.energiaAdversario ?? prev.energia,
        fadiga: atualizacao.fadigaAdversario ?? prev.fadiga,
      }))
    }
    if (atualizacao.descricao) setLog(p => [...p, atualizacao.descricao].slice(-80))
    setAlertaBreak(detectBreakPoint(atualizacao.placar))

    // Point flash (only for individual pontos)
    if (atualizacao.descricao && atualizacao.tipo === 'ponto') {
      const color = flashColor(atualizacao.descricao)
      setFlashPonto({ texto: atualizacao.descricao, color })
      setTimeout(() => setFlashPonto(null), 2200)
    }

    if (atualizacao.placar.encerrado) {
      setFase('encerrada')
      return
    }

    if (atualizacao.tipo === 'set') {
      setGameResult(null)
      setAjustandoPlanoSet(false)
      setFase('entre-sets')
      return
    }

    if (atualizacao.tipo === 'game') {
      const jogadorGanhouGame = atualizacao.placar.games[0] > prevGames[0]
      const quemGanhou: 'jogador' | 'adversario' = jogadorGanhouGame ? 'jogador' : 'adversario'
      const foiBreak = jogadorGanhouGame
        ? prevServindo === 'adversario'
        : prevServindo === 'jogador'

      setGameResult({ quemGanhou, foiBreak, placarGames: atualizacao.placar.games })
      setAjustandoPlanoGame(false)

      if (modoRef.current === 'auto' || modoRef.current === 'detalhado') {
        setFase('aguardando')
      } else {
        setFase('entre-games')
      }
      return
    }

    if (!atualizacao.placar.encerrado) setFase('aguardando')
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
        if (r.adversario) applyAdversario(r.adversario)
        if (r.placar) {
          aplicar(criarEventoLocalDePlacar(r.placar, 'setup'))
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
      if (r.adversario) applyAdversario(r.adversario)
      if (r.placar) {
        aplicar(criarEventoLocalDePlacar(r.placar, 'setup'))
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
      let finalEstado: MatchPointRuntime | null = null
      while (true) {
        const estado = await api.partida.ponto(partidaId)
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
      aplicar(criarEventoLocalDePlacar(estado, estado.encerrado ? 'fim' : 'set'))
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
    extrairHistoricoJogador(jogador),
    extrairHistoricoTorneiosJogador(jogador),
  )
  const titulosJogador = resumirTitulosRival(extrairTrofeusJogador(jogador))
  const corCardRival = accentFromCarta(adversario.carta, '#ff4466')
  const scoutRival = useOpponentScouting(fase, adversario.nome)
  const metricsJogador = getScoutingMetricsFromData(
    jogador?.carta?.atributos_boosted ?? jogador?.atributos ?? {},
    jogador?.atributos_psicologicos ?? {},
    jogador?.resumo_fifa,
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
      <SetupView
        faseTorneio={faseTorneio}
        superficie={superficie}
        surface={surface}
        jogador={jogador}
        adversario={adversario}
        overallCardJogador={overallCardJogador}
        rankingJogador={rankingJogador}
        overallCardAdversario={overallCardAdversario}
        rankingAdversario={rankingAdversario}
        corCardRival={corCardRival}
        leituraRival={leituraRival}
        abaRival={abaRival}
        setAbaRival={setAbaRival}
        historicoRival={historicoRival}
        titulosRival={titulosRival}
        energiaAdversarioAoVivo={energiaAdversarioAoVivo}
        fadigaAdversarioAoVivo={fadigaAdversarioAoVivo}
        scoutRival={scoutRival}
        nomeJogador={nomeJogador}
        leituraJogador={leituraJogador}
        abaJogador={abaJogador}
        setAbaJogador={setAbaJogador}
        historicoJogador={historicoJogador}
        titulosJogador={titulosJogador}
        energiaJogadorAoVivo={energiaJogadorAoVivo}
        fadigaJogadorAoVivo={fadigaJogadorAoVivo}
        metricsJogador={metricsJogador}
        reportJogador={reportJogador}
        planoExecutivo={planoExecutivo}
        mentalidade={mentalidade}
        abordagem={abordagem}
        instrucao={instrucao}
        segundoSaque={segundoSaque}
        setMentalidade={setMentalidade}
        setAbordagem={setAbordagem}
        setInstrucao={setInstrucao}
        setSegundoSaque={setSegundoSaque}
        encaixeFisico={encaixeFisico}
        riscoTatico={riscoTatico}
        modo={modo}
        trocarModoAcompanhamento={trocarModoAcompanhamento}
        erroEntrada={erroEntrada}
        handleIniciar={handleIniciar}
        simulando={simulando}
        confirmandoEntrada={confirmandoEntrada}
        inferirEstilo={inferirEstilo}
      />
    )
  }

  // ─── PÓS-STATS ───────────────────────────────────────────────────────────

  if (fase === 'pos-stats' || fase === 'pos-consequencias') {
    return (
      <PostMatchView
        fase={fase}
        placar={placar}
        nomeJogador={nomeJogador}
        adversario={adversario}
        log={log}
        jogadorPosjogo={jogadorPosjogo}
        jogador={jogador}
        jogadorAntesRef={jogadorAntesRef}
        setFase={setFase}
        handleContinuarPosJogo={handleContinuarPosJogo}
      />
    )
  }


  return (
    <InGameView
      nomeJogador={nomeJogador}
      adversario={adversario}
      placar={placar}
      superficie={superficie}
      momentum={momentum}
      destaqueMomento={destaqueMomento}
      destaqueMomentoCor={destaqueMomentoCor}
      leituraJogador={leituraJogador}
      leituraRival={leituraRival}
      energiaJogadorAoVivo={energiaJogadorAoVivo}
      fadigaJogadorAoVivo={fadigaJogadorAoVivo}
      energiaAdversarioAoVivo={energiaAdversarioAoVivo}
      fadigaAdversarioAoVivo={fadigaAdversarioAoVivo}
      resumoEstrategiaJogador={resumoEstrategiaJogador}
      resumoEstrategiaAdversario={resumoEstrategiaAdversario}
      planoAtual={planoAtual}
      segundoSaque={segundoSaque}
      fase={fase}
      modo={modo}
      partidaId={partidaId}
      simulando={simulando}
      simulacaoPausada={simulacaoPausada}
      velocidadeRapidaAtual={velocidadeRapidaAtual}
      velocidadeRapida={velocidadeRapida}
      ajustandoPlanoRapido={ajustandoPlanoRapido}
      mentalidade={mentalidade}
      abordagem={abordagem}
      instrucao={instrucao}
      gameResult={gameResult}
      ajustandoPlanoGame={ajustandoPlanoGame}
      ajustandoPlanoSet={ajustandoPlanoSet}
      contadorSet={contadorSet}
      intencaoAtiva={intencaoAtiva}
      expandirPonto={expandirPonto}
      faixa={faixa}
      alvo={alvo}
      onBack={() => navigate('/tournament')}
      onSurrender={handleDesistir}
      alternarPausaSimulacao={alternarPausaSimulacao}
      setVelocidadeRapida={setVelocidadeRapida}
      setAjustandoPlanoRapido={setAjustandoPlanoRapido}
      setMentalidade={setMentalidade}
      setAbordagem={setAbordagem}
      setInstrucao={setInstrucao}
      setSegundoSaque={setSegundoSaque}
      handleAplicarPausaRapida={handleAplicarPausaRapida}
      setAjustandoPlanoGame={setAjustandoPlanoGame}
      handleContinuarGame={handleContinuarGame}
      setAjustandoPlanoSet={setAjustandoPlanoSet}
      handleContinuarSet={handleContinuarSet}
      handleEscolherPlanoSet={handleEscolherPlanoSet}
      handleIntencao={handleIntencao}
      setExpandirPonto={setExpandirPonto}
      setFaixa={setFaixa}
      setAlvo={setAlvo}
      trocarModoAcompanhamento={trocarModoAcompanhamento}
    />
  )
}
