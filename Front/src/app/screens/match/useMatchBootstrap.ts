import { useEffect } from 'react'
import { api, ApiError } from '../../../api/client'
import type { AdversarioInfo as ApiAdversarioInfo, PlacarState } from '../../../types'
import { extrairAdversarioInfoPartida, modoAcompanhamentoDaApi } from './bootstrap'
import type { MatchPointRuntime, ModoAcomp } from './types'

interface UseMatchBootstrapArgs {
  saveAtivo: string | null
  jogador: any
  nomeJogador: string
  fase: string
  setJogador: (jogador: any) => void
  setPartidaId: (id: string | null) => void
  setInternalPartidaId: (id: string | null) => void
  setModo: (modo: ModoAcomp) => void
  setPlacar: (placar: PlacarState) => void
  setFase: (fase: any) => void
  setSuperficie: (superficie: string) => void
  setFaseTorneio: (fase: string) => void
  lastPlacar: React.MutableRefObject<PlacarState>
  applyAdversario: (adversario: ApiAdversarioInfo) => void
  aplicar: (estado: MatchPointRuntime | PlacarState) => void
}

export function useMatchBootstrap({
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
}: UseMatchBootstrapArgs) {
  async function tentarRestaurarSessao(): Promise<boolean> {
    if (!saveAtivo) return false
    try {
      const response = await api.saves.carregar(saveAtivo)
      if (response.ok) {
        setJogador(response.jogador)
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
      } else if (!ativa.encerrado) {
        setFase('aguardando')
      }
      // se encerrado sem placar, deixa o fluxo normal de boot decidir
      return true
    } catch {
      return false
    }
  }

  useEffect(() => {
    let ativo = true

    api.partida.ativa()
      .then((response) => {
        if (!ativo) return
        if (!response?.partida_id) {
          setFase('setup')
          return
        }
        setInternalPartidaId(response.partida_id)
        setPartidaId(response.partida_id)
        setModo(modoAcompanhamentoDaApi(response.config.modo))
        if (response.adversario) applyAdversario(response.adversario)
        if (response.placar) {
          setPlacar(response.placar)
          lastPlacar.current = response.placar
        }
        setFase('aguardando')
      })
      .catch(async (error) => {
        if (error instanceof ApiError && error.status === 400 && saveAtivo) {
          try {
            const response = await api.saves.carregar(saveAtivo)
            if (response.ok) setJogador(response.jogador)
          } catch {
            // ignora
          }
        }
      })

    return () => {
      ativo = false
    }
  }, [
    applyAdversario,
    lastPlacar,
    saveAtivo,
    setFase,
    setInternalPartidaId,
    setJogador,
    setModo,
    setPartidaId,
    setPlacar,
  ])

  useEffect(() => {
    if (fase !== 'setup') return

    api.torneio
      .estado()
      .then((torneio) => {
        if (!torneio) return
        setSuperficie(torneio.superficie ?? '')
        setFaseTorneio(String(torneio.fase_atual ?? ''))
        const adversario = extrairAdversarioInfoPartida(torneio, nomeJogador)
        if (adversario) applyAdversario(adversario)
      })
      .catch((error) => console.error('Erro ao carregar estado do torneio:', error))

    api.partida
      .preview()
      .then((response) => {
        if (response?.adversario) applyAdversario(response.adversario)
      })
      .catch((error) => console.error('Erro ao carregar preview da partida:', error))
  }, [applyAdversario, fase, nomeJogador, setFaseTorneio, setSuperficie])

  return {
    tentarRestaurarSessao,
    reaproveitarPartidaAtiva,
  }
}
