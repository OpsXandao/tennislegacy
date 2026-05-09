import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router'
import { api, ApiError } from '../../../api/client'
import { useGameStore } from '../../../store/gameStore'
import type {
  AdversarioInfo as ApiAdversarioInfo,
  JogadorState,
  MatchPointRuntime,
  MatchStrategySummary,
  PlacarState,
} from '../../../types'
import type {
  AbordagemValor,
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
} from './types'
import {
  ABORDAGENS,
  INSTRUCOES,
  MENTALIDADES,
} from './components'
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
  resumoMomentum,
  serializarPacoteTatico,
} from './model'
import {
  criarEventoLocalDePlacar,
  extrairAtualizacaoRuntime,
  extrairHistoricoJogador,
  extrairHistoricoTorneiosJogador,
  extrairTrofeusJogador,
  mapApiAdversarioParaMatch,
} from './bootstrap'
import { useOpponentScouting } from './useOpponentScouting'
import { useMatchBootstrap } from './useMatchBootstrap'

const ADVERSARIO_INICIAL = {
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
} as const

export function useMatchController() {
  const navigate = useNavigate()
  const { jogador, saveAtivo, setJogador, setPartidaId, setSemana, setTorneio, fetchJogador, ano } =
    useGameStore()

  const pacoteInicial = carregarPacoteTaticoInicial()

  // ─── Tactical state ──────────────────────────────────────────────────────
  const [mentalidade, setMentalidade] = useState<MentalidadeValor>(pacoteInicial.mentalidade)
  const [abordagem, setAbordagem] = useState<AbordagemValor>(pacoteInicial.abordagem)
  const [instrucao, setInstrucao] = useState<InstrucaoValor>(pacoteInicial.instrucao)

  // ─── Core match state ────────────────────────────────────────────────────
  const [fase, setFase] = useState<Fase>('setup')
  const [placar, setPlacar] = useState<PlacarState>(PLACAR_INICIAL)
  const [simulando, setSimulando] = useState(false)
  const [simulacaoPausada, setSimulacaoPausada] = useState(false)
  const [velocidadeRapida, setVelocidadeRapida] = useState<VelocidadeRapida>('rapida')
  const [ajustandoPlanoRapido, setAjustandoPlanoRapido] = useState(false)

  // ─── Setup state ─────────────────────────────────────────────────────────
  const [plano, setPlano] = useState<PlanoValor>(() =>
    inferirPlanoDoPacote(pacoteInicial.mentalidade, pacoteInicial.abordagem, pacoteInicial.instrucao),
  )
  const [modo, setModo] = useState<ModoAcomp>(pacoteInicial.modo)
  const [segundoSaque, setSegundoSaque] = useState<SegundoSaqueModo>(pacoteInicial.segundoSaque)
  const [confirmandoEntrada, setConfirmandoEntrada] = useState(false)
  const [abaRival, setAbaRival] = useState<'registros' | 'historia'>('registros')
  const [abaJogador, setAbaJogador] = useState<'registros' | 'historia'>('registros')

  // ─── Per-point (estrategista) ─────────────────────────────────────────────
  const [faixa, setFaixa] = useState<Faixa>('FUNDO')
  const [alvo, setAlvo] = useState<Alvo>('CENTRO')
  const [intencaoAtiva, setIntencaoAtiva] = useState<string | null>(null)
  const [expandirPonto, setExpandirPonto] = useState(false)

  // ─── Match info state ─────────────────────────────────────────────────────
  const [adversario, setAdversario] = useState(ADVERSARIO_INICIAL as any)
  const [energiaJogadorAoVivo, setEnergiaJogadorAoVivo] = useState(100)
  const [fadigaJogadorAoVivo, setFadigaJogadorAoVivo] = useState(0)
  const [energiaAdversarioAoVivo, setEnergiaAdversarioAoVivo] = useState(100)
  const [fadigaAdversarioAoVivo, setFadigaAdversarioAoVivo] = useState(0)
  const [estrategiaJogadorAoVivo, setEstrategiaJogadorAoVivo] =
    useState<MatchStrategySummary>(ESTRATEGIA_PADRAO_UI)
  const [estrategiaAdversarioAoVivo, setEstrategiaAdversarioAoVivo] =
    useState<MatchStrategySummary>(ESTRATEGIA_PADRAO_UI)
  const [partidaId, setInternalPartidaId] = useState<string | null>(null)
  const [superficie, setSuperficie] = useState('')
  const [faseTorneio, setFaseTorneio] = useState('')
  const [log, setLog] = useState<string[]>([])
  const [pointInsights, setPointInsights] = useState<string[]>([])
  const [erroEntrada, setErroEntrada] = useState('')
  const [autoSaveAtivo] = useState<boolean>(() => carregarPreferenciaAutoSave())

  // ─── Feedback state ───────────────────────────────────────────────────────
  const [flashPonto, setFlashPonto] = useState<{ texto: string; color: string } | null>(null)
  const [alertaBreak, setAlertaBreak] = useState('')

  // ─── Between game/set state ───────────────────────────────────────────────
  const [gameResult, setGameResult] = useState<GameResult | null>(null)
  const [ajustandoPlanoGame, setAjustandoPlanoGame] = useState(false)
  const [ajustandoPlanoSet, setAjustandoPlanoSet] = useState(false)
  const [contadorSet, setContadorSet] = useState(10)

  // ─── Post-match state ─────────────────────────────────────────────────────
  const [jogadorPosjogo, setJogadorPosjogo] = useState<JogadorState | null>(null)
  const jogadorAntesRef = useRef<{ xp: number; ranking: number; nivel: number } | null>(null)

  // ─── Refs ─────────────────────────────────────────────────────────────────
  const lastPlacar = useRef<PlacarState>(PLACAR_INICIAL)
  const modoRef = useRef<ModoAcomp>(modo)
  const partidaAutoSavePerguntadaRef = useRef<string | null>(null)
  const isMounted = useRef(true)
  const continuarSetRef = useRef<() => void>(() => {})

  // ─── Derived tactical labels ──────────────────────────────────────────────
  const mentalidadeAtual = MENTALIDADES.find((m) => m.valor === mentalidade) ?? MENTALIDADES[1]
  const abordagemAtual = ABORDAGENS.find((a) => a.valor === abordagem) ?? ABORDAGENS[0]
  const instrucaoAtual = INSTRUCOES.find((i) => i.valor === instrucao) ?? INSTRUCOES[0]
  const planoAtual = PLANOS.find((p) => p.valor === plano)!
  const nomeJogador = jogador?.nome ?? 'VOCÊ'

  // ─── aplicar (core state reducer for every point result) ─────────────────
  const aplicar = useCallback((estado: MatchPointRuntime | PlacarState) => {
    const atualizacao = extrairAtualizacaoRuntime(estado)
    const prevGames: [number, number] = [lastPlacar.current.games[0], lastPlacar.current.games[1]]
    const prevServindo = lastPlacar.current.servindo

    setPlacar(atualizacao.placar)
    lastPlacar.current = atualizacao.placar

    if (atualizacao.energiaJogador !== null) setEnergiaJogadorAoVivo(atualizacao.energiaJogador)
    if (atualizacao.fadigaJogador !== null) setFadigaJogadorAoVivo(atualizacao.fadigaJogador)
    if (atualizacao.estrategiaJogador) setEstrategiaJogadorAoVivo(atualizacao.estrategiaJogador)
    if (atualizacao.estrategiaAdversario) setEstrategiaAdversarioAoVivo(atualizacao.estrategiaAdversario)

    if (atualizacao.energiaAdversario !== null || atualizacao.fadigaAdversario !== null) {
      if (atualizacao.energiaAdversario !== null) setEnergiaAdversarioAoVivo(atualizacao.energiaAdversario)
      if (atualizacao.fadigaAdversario !== null) setFadigaAdversarioAoVivo(atualizacao.fadigaAdversario)
      setAdversario((prev: any) => ({
        ...prev,
        energia: atualizacao.energiaAdversario ?? prev.energia,
        fadiga: atualizacao.fadigaAdversario ?? prev.fadiga,
      }))
    }

    if (atualizacao.descricao) setLog((p) => [...p, atualizacao.descricao].slice(-80))
    
    // Insights táticos do último ponto
    if ('last_point_stats' in estado && estado.last_point_stats) {
      const stats = estado.last_point_stats as any
      if (Array.isArray(stats.insights)) {
        setPointInsights(stats.insights)
      }
    } else if (atualizacao.tipo === 'game' || atualizacao.tipo === 'set') {
      setPointInsights([]) // Limpa insights ao mudar de game/set
    }

    setAlertaBreak(detectBreakPoint(atualizacao.placar))

    if (atualizacao.descricao && atualizacao.tipo === 'ponto') {
      const color = flashColor(atualizacao.descricao)
      setFlashPonto({ texto: atualizacao.descricao, color })
      setTimeout(() => setFlashPonto(null), 2200)
    }

    if (atualizacao.placar.encerrado) { setFase('encerrada'); return }

    if (atualizacao.tipo === 'set') {
      setGameResult(null)
      setAjustandoPlanoSet(false)
      setFase('entre-sets')
      return
    }

    if (atualizacao.tipo === 'game') {
      const jogadorGanhouGame = atualizacao.placar.games[0] > prevGames[0]
      const quemGanhou: 'jogador' | 'adversario' = jogadorGanhouGame ? 'jogador' : 'adversario'
      const foiBreak = jogadorGanhouGame ? prevServindo === 'adversario' : prevServindo === 'jogador'
      setGameResult({ quemGanhou, foiBreak, placarGames: atualizacao.placar.games })
      setAjustandoPlanoGame(false)
      setFase(modoRef.current === 'auto' || modoRef.current === 'detalhado' ? 'aguardando' : 'entre-games')
      return
    }

    if (!atualizacao.placar.encerrado) setFase('aguardando')
  }, [])

  // ─── Helpers ─────────────────────────────────────────────────────────────
  function applyAdversario(adv: ApiAdversarioInfo) {
    if (!adv) return
    const match = mapApiAdversarioParaMatch(adv)
    setAdversario(match)
    setEnergiaJogadorAoVivo(Number(jogador?.energia ?? 100))
    setFadigaJogadorAoVivo(Number(jogador?.fadiga ?? 0))
    setEnergiaAdversarioAoVivo(match.energia)
    setFadigaAdversarioAoVivo(match.fadiga)
  }

  const { tentarRestaurarSessao, reaproveitarPartidaAtiva } = useMatchBootstrap({
    saveAtivo,
    jogador,
    nomeJogador,
    fase,
    setJogador,
    setPartidaId,
    setInternalPartidaId,
    setModo,
    setPlacar,
    setFase,
    setSuperficie,
    setFaseTorneio,
    lastPlacar,
    applyAdversario,
    aplicar,
  })

  // ─── Handlers ────────────────────────────────────────────────────────────
  async function handleIniciar() {
    if (!confirmandoEntrada) { setConfirmandoEntrada(true); setErroEntrada(''); return }
    setSimulando(true)
    setErroEntrada('')
    try {
      if (await reaproveitarPartidaAtiva()) return

      if (modo === 'auto') {
        const r = await api.partida.iniciar('rapido')
        setInternalPartidaId(r.partida_id)
        setPartidaId(r.partida_id)
        if (r.adversario) applyAdversario(r.adversario)
        if (r.placar) aplicar(criarEventoLocalDePlacar(r.placar, 'setup'))
        await api.partida.estrategia(r.partida_id, serializarPacoteTatico(mentalidade, abordagem, instrucao, segundoSaque)).catch(() => {})
        const estado = await api.partida.simularPartida(r.partida_id)
        aplicar({ ...estado, tipo: 'fim' as any, descricao: '' } as any)
        return
      }

      const apiModo = modo === 'estrategista' ? 'estrategista' : 'rapido'
      const r = await api.partida.iniciar(apiModo)
      setInternalPartidaId(r.partida_id)
      setPartidaId(r.partida_id)
      if (r.adversario) applyAdversario(r.adversario)
      if (r.placar) aplicar(criarEventoLocalDePlacar(r.placar, 'setup'))
      await api.partida.estrategia(r.partida_id, serializarPacoteTatico(mentalidade, abordagem, instrucao, segundoSaque)).catch(() => {})
      setFase('aguardando')
    } catch (e) {
      if (e instanceof ApiError && e.status === 400) {
        const restaurou = await tentarRestaurarSessao()
        if (restaurou) { setSimulando(false); handleIniciar(); return }
        navigate('/')
        return
      }
      if (await reaproveitarPartidaAtiva()) return
      setErroEntrada('Nao foi possivel iniciar a partida.')
      console.error(e)
    } finally { setSimulando(false) }
  }

  async function handleIntencao(intencao: string) {
    if (!partidaId || fase !== 'aguardando') return
    setIntencaoAtiva(intencao); setFase('jogando'); setSimulando(true); setAlertaBreak('')
    try {
      await api.partida.estrategia(partidaId, estrategiaPonto(intencao, faixa)).catch(() => {})
      const estado = await api.partida.ponto(partidaId)
      aplicar(estado)
    } catch { setFase('aguardando') }
    finally { setSimulando(false); setIntencaoAtiva(null) }
  }

  async function handleProximoPonto() {
    if (!partidaId || fase !== 'aguardando') return
    setFase('jogando'); setSimulando(true)
    try { const estado = await api.partida.ponto(partidaId); aplicar(estado) }
    catch { setFase('aguardando') }
    finally { setSimulando(false) }
  }

  async function handleSimularGame() {
    if (!partidaId) return
    setFase('jogando'); setSimulando(true)
    try {
      let finalEstado: MatchPointRuntime | null = null
      while (true) {
        const estado = await api.partida.ponto(partidaId)
        if (estado.tipo === 'game' || estado.tipo === 'set' || estado.tipo === 'fim' || estado.encerrado) {
          finalEstado = estado; break
        }
        lastPlacar.current = estado
      }
      if (finalEstado) aplicar(finalEstado)
    } catch { setFase('aguardando') }
    finally { setSimulando(false) }
  }

  async function handleSimularSet() {
    if (!partidaId) return
    setFase('jogando'); setSimulando(true)
    try {
      const estado = await api.partida.simularSet(partidaId)
      aplicar(criarEventoLocalDePlacar(estado, estado.encerrado ? 'fim' : 'set'))
    } catch { setFase('aguardando') }
    finally { setSimulando(false) }
  }

  async function aplicarEstrategiaAtual() {
    if (!partidaId) return
    const est = serializarPacoteTatico(mentalidade, abordagem, instrucao, segundoSaque)
    await api.partida.estrategia(partidaId, est).catch((e) => console.error('Erro ao aplicar estratégia:', e))
  }

  async function handleContinuarGame() {
    if (partidaId) await aplicarEstrategiaAtual()
    setAjustandoPlanoGame(false); setGameResult(null); setFase('aguardando')
  }

  async function handleContinuarSet() {
    setGameResult(null); setAjustandoPlanoSet(false)
    if (partidaId) {
      const est = serializarPacoteTatico(mentalidade, abordagem, instrucao, segundoSaque)
      await api.partida.ajusteTatico(partidaId, est, placar.sets[0] + placar.sets[1]).catch((e) => console.error('Ajuste tático falhou:', e))
    }
    setFase('aguardando')
  }

  async function handleEscolherPlanoSet(p: PlanoValor) {
    const mapa: Record<PlanoValor, { m: MentalidadeValor; a: AbordagemValor; i: InstrucaoValor }> = {
      pressionar: { m: 'OFENSIVA', a: 'SERVE_VOLLEY', i: 'PADRAO' },
      consistencia: { m: 'DEFENSIVA', a: 'BASELINE', i: 'TROCAS_LONGAS' },
      variar: { m: 'EQUILIBRADA', a: 'BASELINE', i: 'PADRAO' },
    }
    const { m, a, i } = mapa[p]
    setMentalidade(m); setAbordagem(a); setInstrucao(i)
    const est = serializarPacoteTatico(m, a, i, segundoSaque)
    if (partidaId) await api.partida.ajusteTatico(partidaId, est, placar.sets[0] + placar.sets[1]).catch((e) => console.error('Ajuste tático falhou:', e))
    setGameResult(null); setAjustandoPlanoSet(false); setFase('aguardando')
  }

  async function handleAplicarPausaRapida() {
    await aplicarEstrategiaAtual()
    setAjustandoPlanoRapido(false); setSimulacaoPausada(false); setFase('aguardando')
  }

  async function handleDesistir() {
    if (!partidaId) return
    if (!window.confirm('Tem certeza? Isso resultará em derrota por W.O.')) return
    try { await api.partida.desistir(partidaId); navigate('/tournament') }
    catch (e) { console.error(e) }
  }

  async function handleContinuarPosJogo() {
    try {
      const torneioAtual = await api.torneio.estado().catch(() => null)
      if (torneioAtual?.fase_atual === 'finalizado') {
        const resultado = await api.calendario.avancar()
        setSemana(resultado.semana, resultado.ano ?? ano)
        await fetchJogador().catch(() => {})
        setTorneio(null); setPartidaId(null); navigate('/hub')
        return
      }
      if (torneioAtual) setTorneio(torneioAtual)
    } catch { /* mantém saída padrão */ }
    setPartidaId(null); navigate('/tournament')
  }

  function trocarModoAcompanhamento(novoModo: ModoAcomp) {
    setModo(novoModo)
    if (novoModo !== 'detalhado') { setSimulacaoPausada(false); setAjustandoPlanoRapido(false) }
  }

  function alternarPausaSimulacao() {
    if (modo !== 'detalhado' || !partidaId || fase === 'encerrada' || fase === 'jogando') return
    setSimulacaoPausada((atual) => {
      const proximo = !atual; setAjustandoPlanoRapido(proximo); return proximo
    })
    if (fase !== 'aguardando') setFase('aguardando')
  }

  // ─── Effects ─────────────────────────────────────────────────────────────
  useEffect(() => { modoRef.current = modo }, [modo])
  useEffect(() => { setEnergiaJogadorAoVivo(Number(jogador?.energia ?? 100)); setFadigaJogadorAoVivo(Number(jogador?.fadiga ?? 0)) }, [jogador?.energia, jogador?.fadiga])
  useEffect(() => { setEnergiaAdversarioAoVivo(Number(adversario.energia ?? 100)); setFadigaAdversarioAoVivo(Number(adversario.fadiga ?? 0)) }, [adversario.energia, adversario.fadiga])
  useEffect(() => { setPlano(inferirPlanoDoPacote(mentalidade, abordagem, instrucao)) }, [mentalidade, abordagem, instrucao])
  useEffect(() => {
    window.localStorage.setItem(MATCH_SETTINGS_KEY, JSON.stringify({ mentalidade, abordagem, instrucao, segundoSaque, modo }))
  }, [mentalidade, abordagem, instrucao, segundoSaque, modo])

  useEffect(() => {
    isMounted.current = true
    return () => { isMounted.current = false }
  }, [])

  useEffect(() => {
    let ativo = true
    fetchJogador()
      .then((j) => { if (!ativo) return; jogadorAntesRef.current = { xp: j.xp, ranking: j.ranking, nivel: j.nivel } })
      .catch(() => { if (!ativo || !jogador) return; jogadorAntesRef.current = { xp: jogador.xp, ranking: jogador.ranking, nivel: jogador.nivel } })
    return () => { ativo = false }
  }, [fetchJogador, jogador])

  useEffect(() => {
    if (modo !== 'game') return
    if (fase !== 'aguardando' || simulando || placar.encerrado || !partidaId) return
    const t = setTimeout(handleSimularGame, 350)
    return () => clearTimeout(t)
  }, [modo, fase, simulando, placar.encerrado, partidaId])

  useEffect(() => {
    if (modo !== 'detalhado' || simulacaoPausada) return
    if (fase !== 'aguardando' || simulando || placar.encerrado || !partidaId) return
    const delay = VELOCIDADES_RAPIDAS.find((v) => v.valor === velocidadeRapida)?.delay ?? 350
    const t = setTimeout(handleProximoPonto, delay)
    return () => clearTimeout(t)
  }, [modo, fase, simulando, placar.encerrado, partidaId, simulacaoPausada, velocidadeRapida])

  useEffect(() => {
    if (!partidaId || fase === 'setup' || placar.encerrado) return
    if (partidaAutoSavePerguntadaRef.current === partidaId) return
    partidaAutoSavePerguntadaRef.current = partidaId
    if (autoSaveAtivo) api.saves.salvar().catch((e) => console.error('Auto-save falhou:', e))
  }, [autoSaveAtivo, fase, partidaId, placar.encerrado])

  useEffect(() => {
    if (fase !== 'encerrada') return
    api.jogador.get().then((res) => { if (isMounted.current) setJogadorPosjogo(res) })
      .catch((e) => console.error('Erro ao buscar jogador pós-jogo:', e))
  }, [fase])

  useEffect(() => {
    if (fase !== 'encerrada') return
    const t = window.setTimeout(() => { if (isMounted.current) setFase('pos-stats') }, 2600)
    return () => window.clearTimeout(t)
  }, [fase])

  useEffect(() => {
    continuarSetRef.current = () => {
      if (!isMounted.current) return
      setGameResult(null); setAjustandoPlanoSet(false)
      if (partidaId) {
        const est = serializarPacoteTatico(mentalidade, abordagem, instrucao, segundoSaque)
        api.partida.ajusteTatico(partidaId, est, placar.sets[0] + placar.sets[1]).catch((e) => console.error('Erro ao aplicar ajuste tático:', e))
      }
      setFase('aguardando')
    }
  })

  useEffect(() => {
    if (fase !== 'entre-sets') { setContadorSet(10); return }
    setContadorSet(10)
    const id = window.setInterval(() => {
      if (!isMounted.current) { window.clearInterval(id); return }
      setContadorSet((c) => { if (c <= 1) { window.clearInterval(id); continuarSetRef.current(); return 0 } return c - 1 })
    }, 1000)
    return () => window.clearInterval(id)
  }, [fase])

  // ─── Derived values ───────────────────────────────────────────────────────
  const encaixeFisico =
    energiaJogadorAoVivo >= 75 && fadigaJogadorAoVivo <= 10 ? 'ALTO'
    : energiaJogadorAoVivo >= 55 ? 'MÉDIO' : 'BAIXO'
  const riscoTatico =
    mentalidade === 'OFENSIVA' && abordagem === 'SERVE_VOLLEY' ? 'ALTO'
    : mentalidade === 'DEFENSIVA' && instrucao === 'PADRAO' ? 'BAIXO' : 'MÉDIO'
  const planoExecutivo = `${mentalidadeAtual.label} com ${abordagemAtual.label.toLowerCase()} e ${instrucaoAtual.label.toLowerCase()}.`
  const surface = normSurface(superficie)
  const momentum = calcMomentum(placar)
  const pontoCritico = detectarPontoCritico(placar)
  const leituraJogador = leituraFisica(energiaJogadorAoVivo, fadigaJogadorAoVivo)
  const leituraRival = leituraFisica(energiaAdversarioAoVivo, fadigaAdversarioAoVivo)
  const rankingJogador = rankingValido(jogador?.ranking)
  const rankingAdversario = rankingValido(adversario.ranking)
  const historicoRival = resumirHistoricoRival(adversario.historicoPartidas, adversario.historicoTorneios)
  const titulosRival = resumirTitulosRival(adversario.trofeus)
  const historicoJogador = resumirHistoricoRival(extrairHistoricoJogador(jogador), extrairHistoricoTorneiosJogador(jogador))
  const titulosJogador = resumirTitulosRival(extrairTrofeusJogador(jogador))
  const corCardRival = accentFromCarta(adversario.carta, '#ff4466')
  const scoutRival = useOpponentScouting(fase, adversario.nome)
  const metricsJogador = getScoutingMetricsFromData(
    jogador?.carta?.atributos_boosted ?? jogador?.atributos ?? {},
    jogador?.atributos_psicologicos ?? {},
    jogador?.resumo_fifa,
  )
  const reportJogador = montarRelatorioJogador({ nome: nomeJogador, energia: energiaJogadorAoVivo, fadiga: fadigaJogadorAoVivo, encaixeFisico, metrics: metricsJogador, superficie })
  const overallCardJogador = calcularOverallCardMatch(metricsJogador)
  const metricsAdversario = getScoutingMetrics(adversario)
  const overallCardAdversario = calcularOverallCardMatch(metricsAdversario)
  const destaqueMomento = alertaBreak || flashPonto?.texto || pontoCritico?.label || resumoMomentum(momentum)
  const destaqueMomentoCor = alertaBreak ? '#ff4466' : flashPonto?.color || pontoCritico?.color || '#00e5ff'
  const velocidadeRapidaAtual = VELOCIDADES_RAPIDAS.find((v) => v.valor === velocidadeRapida) ?? VELOCIDADES_RAPIDAS[2]
  const resumoEstrategiaJogador = resumirEstrategiaLado(estrategiaJogadorAoVivo)
  const resumoEstrategiaAdversario = resumirEstrategiaLado(estrategiaAdversarioAoVivo)
  const podeControlarRitmo = fase !== 'encerrada' && fase !== 'entre-games' && fase !== 'entre-sets' && fase !== 'jogando' && Boolean(partidaId)

  return {
    // State
    fase, setFase,
    placar, simulando, simulacaoPausada, velocidadeRapida, ajustandoPlanoRapido,
    plano, modo, segundoSaque, confirmandoEntrada, abaRival, setAbaRival, abaJogador, setAbaJogador,
    faixa, setFaixa, alvo, setAlvo, intencaoAtiva, expandirPonto, setExpandirPonto,
    pointInsights,
    adversario, energiaJogadorAoVivo, fadigaJogadorAoVivo,
    energiaAdversarioAoVivo, fadigaAdversarioAoVivo,
    partidaId, superficie, faseTorneio, log, erroEntrada,
    flashPonto, alertaBreak,
    gameResult, ajustandoPlanoGame, setAjustandoPlanoGame, ajustandoPlanoSet, setAjustandoPlanoSet, contadorSet,
    jogadorPosjogo, jogadorAntesRef,
    // Tactical
    mentalidade, setMentalidade, abordagem, setAbordagem, instrucao, setInstrucao,
    setSegundoSaque, setVelocidadeRapida, setAjustandoPlanoRapido,
    // Derived
    nomeJogador, planoAtual, encaixeFisico, riscoTatico, planoExecutivo,
    surface, momentum, pontoCritico, podeControlarRitmo,
    leituraJogador, leituraRival,
    rankingJogador, rankingAdversario,
    historicoRival, titulosRival, historicoJogador, titulosJogador,
    corCardRival, scoutRival,
    metricsJogador, reportJogador, overallCardJogador,
    metricsAdversario, overallCardAdversario,
    destaqueMomento, destaqueMomentoCor,
    velocidadeRapidaAtual,
    resumoEstrategiaJogador, resumoEstrategiaAdversario,
    // Handlers
    handleIniciar, handleIntencao, handleProximoPonto, handleSimularGame, handleSimularSet,
    handleContinuarGame, handleContinuarSet, handleEscolherPlanoSet,
    handleAplicarPausaRapida, handleDesistir, handleContinuarPosJogo,
    trocarModoAcompanhamento, alternarPausaSimulacao,
    inferirEstilo,
    // Store
    jogador,
  }
}
