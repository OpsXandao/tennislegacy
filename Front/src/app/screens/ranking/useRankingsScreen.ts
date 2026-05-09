import { useCallback, useEffect, useMemo, useState } from 'react'
import { ApiError, api } from '../../../api/client'
import type { RankingEntry } from '../../../types'
import {
  construirStats,
  filtrarRanking,
  FiltroTab,
  Modalidade,
  SUP_MAP,
  Tour,
} from './model'

export function useRankingsScreen(jogador: any) {
  const [tour, setTour] = useState<Tour>('atp')
  const [modalidade, setModalidade] = useState<Modalidade>('simples')
  const [ranking, setRanking] = useState<RankingEntry[]>([])
  const [totalJogadores, setTotalJogadores] = useState(0)
  const [loading, setLoading] = useState(false)
  const [semSessao, setSemSessao] = useState(false)
  const [filtroTab, setFiltroTab] = useState<FiltroTab>('nome')
  const [filtroValor, setFiltroValor] = useState('')

  const carregar = useCallback(async () => {
    setLoading(true)
    setSemSessao(false)

    try {
      if (tour === 'davis') {
        const response = await api.ranking.nacoes(5000)
        setRanking(
          response.ranking.map((nacao) => ({
            posicao: nacao.posicao,
            nome: nacao.nome,
            nacionalidade: nacao.codigo,
            pontos: nacao.pontos,
          }))
        )
        setTotalJogadores(response.total)
        return
      }

      const surfaceKey = SUP_MAP[modalidade]
      if (surfaceKey) {
        const response = await api.ranking.superficie(surfaceKey, tour === 'wta' ? 'wta' : 'atp', 500)
        setRanking(
          response.jogadores.map((jogadorSuperficie) => ({
            posicao: jogadorSuperficie.posicao,
            nome: jogadorSuperficie.nome,
            pontos: jogadorSuperficie.pontos_superficie,
            overall: jogadorSuperficie.overall,
            nacionalidade: jogadorSuperficie.nacionalidade,
          }))
        )
        setTotalJogadores(response.jogadores.length)
        return
      }

      const response =
        modalidade === 'simples'
          ? tour === 'atp'
            ? await api.ranking.atp(5000)
            : await api.ranking.wta(5000)
          : await api.ranking.duplas(tour, 5000)

      setRanking(response.ranking)
      setTotalJogadores(response.total)
    } catch (error) {
      setRanking([])
      setTotalJogadores(0)
      if (error instanceof ApiError && (error.status === 400 || error.status === 404)) {
        setSemSessao(true)
      }
    } finally {
      setLoading(false)
    }
  }, [modalidade, tour])

  useEffect(() => {
    carregar()
  }, [carregar])

  useEffect(() => {
    setFiltroValor('')
    setFiltroTab('nome')
  }, [tour, modalidade])

  const rankingFiltrado = useMemo(
    () => filtrarRanking(ranking, filtroTab, filtroValor),
    [ranking, filtroTab, filtroValor]
  )

  const stats = useMemo(
    () => construirStats(jogador, tour, modalidade, ranking),
    [jogador, modalidade, ranking, tour]
  )

  const filtroLabel = {
    nome: 'Nome',
    nacionalidade: 'Nacionalidade',
    idade: 'Idade mínima',
    pontos: 'Pontos mínimos',
  }[filtroTab]

  return {
    tour,
    setTour,
    modalidade,
    setModalidade,
    ranking,
    totalJogadores,
    loading,
    semSessao,
    filtroTab,
    setFiltroTab,
    filtroValor,
    setFiltroValor,
    rankingFiltrado,
    stats,
    filtroLabel,
  }
}
