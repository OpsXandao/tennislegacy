import { useNavigate } from 'react-router'
import { api, ApiError } from '../../../api/client'
import { criarEventoLocalDePlacar } from './bootstrap'
import { estrategiaPonto, serializarPacoteTatico } from './model'
import type {
  Faixa,
  InstrucaoValor,
  MatchPointRuntime,
  MentalidadeValor,
  PlanoValor,
  SegundoSaqueModo,
  AbordagemValor,
} from './types'

interface UseMatchActionsArgs {
  confirmandoEntrada: boolean
  modo: string
  fase: string
  partidaId: string | null
  faixa: Faixa
  placar: { sets: [number, number] }
  ano: number
  fetchJogador: () => Promise<any>
  setSemana: (semana: number, ano: number) => void
  setTorneio: (torneio: any) => void
  setPartidaId: (id: string | null) => void
  setInternalPartidaId: (id: string | null) => void
  setSimulando: (valor: boolean) => void
  setErroEntrada: (valor: string) => void
  setConfirmandoEntrada: (valor: boolean | ((current: boolean) => boolean)) => void
  setFase: (fase: any) => void
  setIntencaoAtiva: (valor: string | null) => void
  setAlertaBreak: (valor: string) => void
  setGameResult: (valor: any) => void
  setAjustandoPlanoGame: (valor: boolean) => void
  setAjustandoPlanoSet: (valor: boolean) => void
  setMentalidade: (valor: MentalidadeValor) => void
  setAbordagem: (valor: AbordagemValor) => void
  setInstrucao: (valor: InstrucaoValor) => void
  setAjustandoPlanoRapido: (valor: boolean) => void
  setSimulacaoPausada: (valor: boolean) => void
  setModo: (valor: any) => void
  mentalidade: MentalidadeValor
  abordagem: AbordagemValor
  instrucao: InstrucaoValor
  segundoSaque: SegundoSaqueModo
  aplicar: (estado: any) => void
  applyAdversario: (adversario: any) => void
  reaproveitarPartidaAtiva: () => Promise<boolean>
  tentarRestaurarSessao: () => Promise<boolean>
  lastPlacar: React.MutableRefObject<any>
}

export function useMatchActions({
  confirmandoEntrada,
  modo,
  fase,
  partidaId,
  faixa,
  placar,
  ano,
  fetchJogador,
  setSemana,
  setTorneio,
  setPartidaId,
  setInternalPartidaId,
  setSimulando,
  setErroEntrada,
  setConfirmandoEntrada,
  setFase,
  setIntencaoAtiva,
  setAlertaBreak,
  setGameResult,
  setAjustandoPlanoGame,
  setAjustandoPlanoSet,
  setMentalidade,
  setAbordagem,
  setInstrucao,
  setAjustandoPlanoRapido,
  setSimulacaoPausada,
  setModo,
  mentalidade,
  abordagem,
  instrucao,
  segundoSaque,
  aplicar,
  applyAdversario,
  reaproveitarPartidaAtiva,
  tentarRestaurarSessao,
  lastPlacar,
}: UseMatchActionsArgs) {
  const navigate = useNavigate()

  async function aplicarEstrategiaAtual() {
    if (!partidaId) return
    const estrategia = serializarPacoteTatico(mentalidade, abordagem, instrucao, segundoSaque)
    await api.partida
      .estrategia(partidaId, estrategia)
      .catch((error) => console.error('Erro ao aplicar estratégia:', error))
  }

  async function handleIniciar() {
    if (!confirmandoEntrada) {
      setConfirmandoEntrada(true)
      setErroEntrada('')
      return
    }

    setSimulando(true)
    setErroEntrada('')
    try {
      if (await reaproveitarPartidaAtiva()) return

      const estrategia = serializarPacoteTatico(mentalidade, abordagem, instrucao, segundoSaque)
      if (modo === 'auto') {
        const response = await api.partida.iniciar('rapido')
        setInternalPartidaId(response.partida_id)
        setPartidaId(response.partida_id)
        if (response.adversario) applyAdversario(response.adversario)
        if (response.placar) aplicar(criarEventoLocalDePlacar(response.placar, 'setup'))
        await api.partida.estrategia(response.partida_id, estrategia).catch(() => {})
        const estado = await api.partida.simularPartida(response.partida_id)
        aplicar({ ...estado, tipo: 'fim' as any, descricao: '' } as any)
        return
      }

      const apiModo = modo === 'estrategista' ? 'estrategista' : 'rapido'
      const response = await api.partida.iniciar(apiModo)
      setInternalPartidaId(response.partida_id)
      setPartidaId(response.partida_id)
      if (response.adversario) applyAdversario(response.adversario)
      if (response.placar) aplicar(criarEventoLocalDePlacar(response.placar, 'setup'))
      await api.partida.estrategia(response.partida_id, estrategia).catch(() => {})
      setFase('aguardando')
    } catch (error) {
      if (error instanceof ApiError && error.status === 400) {
        const restaurou = await tentarRestaurarSessao()
        if (restaurou) {
          setSimulando(false)
          handleIniciar()
          return
        }
        navigate('/')
        return
      }
      if (await reaproveitarPartidaAtiva()) return
      setErroEntrada('Nao foi possivel iniciar a partida.')
      console.error(error)
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
        if (
          estado.tipo === 'game' ||
          estado.tipo === 'set' ||
          estado.tipo === 'fim' ||
          estado.encerrado
        ) {
          finalEstado = estado
          break
        }
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

  async function handleContinuarGame() {
    if (partidaId) await aplicarEstrategiaAtual()
    setAjustandoPlanoGame(false)
    setGameResult(null)
    setFase('aguardando')
  }

  async function handleContinuarSet() {
    setGameResult(null)
    setAjustandoPlanoSet(false)
    if (partidaId) {
      const estrategia = serializarPacoteTatico(mentalidade, abordagem, instrucao, segundoSaque)
      await api.partida
        .ajusteTatico(partidaId, estrategia, placar.sets[0] + placar.sets[1])
        .catch((error) => console.error('Ajuste tático falhou:', error))
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
    const estrategia = serializarPacoteTatico(m, a, i, segundoSaque)
    if (partidaId) {
      await api.partida
        .ajusteTatico(partidaId, estrategia, placar.sets[0] + placar.sets[1])
        .catch((error) => console.error('Ajuste tático falhou:', error))
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
    } catch (error) {
      console.error(error)
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
      if (torneioAtual) setTorneio(torneioAtual)
    } catch {
      // mantém saída padrão
    }
    setPartidaId(null)
    navigate('/tournament')
  }

  function trocarModoAcompanhamento(novoModo: any) {
    setModo(novoModo)
    if (novoModo !== 'detalhado') {
      setSimulacaoPausada(false)
      setAjustandoPlanoRapido(false)
    }
  }

  function alternarPausaSimulacao() {
    if (modo !== 'detalhado' || !partidaId || fase === 'encerrada' || fase === 'jogando') return
    setSimulacaoPausada((atual: boolean) => {
      const proximo = !atual
      setAjustandoPlanoRapido(proximo)
      return proximo
    })
    if (fase !== 'aguardando') setFase('aguardando')
  }

  return {
    handleIniciar,
    handleIntencao,
    handleProximoPonto,
    handleSimularGame,
    handleSimularSet,
    handleContinuarGame,
    handleContinuarSet,
    handleEscolherPlanoSet,
    handleAplicarPausaRapida,
    handleDesistir,
    handleContinuarPosJogo,
    trocarModoAcompanhamento,
    alternarPausaSimulacao,
  }
}
