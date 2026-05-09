import { useState, useEffect } from 'react'
import { api } from '../../../api/client'
import { useGameStore } from '../../../store/gameStore'
import type { MembroEquipe, RankingDetalhado, Transaction, MatchHistoryEntry } from '../../../types'

export interface PlayerData {
  atributos: Record<string, number>
  overall: number
  equipe: {
    treinador: MembroEquipe | null
    fisio: MembroEquipe | null
    psicologo: MembroEquipe | null
    empresario: MembroEquipe | null
  } | null
  emails: any[]
  meusTitulos: any[]
  rankingDet: RankingDetalhado | null
  historico: MatchHistoryEntry[]
  financeiro: {
    saldo: number
    transacoes: Transaction[]
    resumo_categorias: Record<string, number>
  } | null
  carreira: any | null
}

export function usePlayerData() {
  const { setJogador } = useGameStore()
  const [data, setData] = useState<PlayerData>({
    atributos: {},
    overall: 0,
    equipe: null,
    emails: [],
    meusTitulos: [],
    rankingDet: null,
    historico: [],
    financeiro: null,
    carreira: null,
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  const carregar = async () => {
    setLoading(true)
    setError(false)
    try {
      const [j, a, e, em, hist, rk, hp, fin, car] = await Promise.all([
        api.jogador.get(),
        api.jogador.atributos(),
        api.staff.equipe(),
        api.email.inbox(),
        api.historico.goat(),
        api.jogador.rankingDetalhado(),
        api.jogador.historicoPartidas(),
        api.jogador.financeiro(),
        api.jogador.carreira(),
      ])

      setJogador(j)
      setData({
        atributos: a.atributos,
        overall: a.overall,
        equipe: e,
        emails: em.emails,
        meusTitulos: hist.meus_titulos || [],
        rankingDet: rk,
        historico: hp.historico || [],
        financeiro: fin,
        carreira: car,
      })

      api.email.marcarLidos().catch(() => {})
    } catch (err) {
      console.error('Erro ao carregar dados do jogador:', err)
      setError(true)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { carregar() }, [])

  return { data, loading, error, recarregar: carregar }
}
