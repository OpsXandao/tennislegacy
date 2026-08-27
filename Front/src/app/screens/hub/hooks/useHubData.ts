import { useEffect, useState } from 'react'
import { api } from '../../../../api/client'
import { useGameStore } from '../../../../store/gameStore'
import { MATCH_AUTOSAVE_KEY } from '../../match/constants'
import { gerarEventosCarreira } from '../../match/matchNarrative'
import type { CareerEvent } from '../../match/matchNarrative'

const PREV_RANK_KEY = 'tennislegacy.ranking.prev'

export function useHubData() {
  const { jogador, semana, fetchJogador } = useGameStore()
  const [unreadEmails, setUnreadEmails] = useState(0)
  const [loadError, setLoadError] = useState(false)
  const [trofeus, setTrofeus] = useState<any[]>([])
  const [careerEvents, setCareerEvents] = useState<CareerEvent[]>([])
  const [lastSaveTime, setLastSaveTime] = useState<string | null>(null)
  const [mostrarPromptAutoSave, setMostrarPromptAutoSave] = useState(false)

  useEffect(() => {
    fetchJogador().catch(() => { setLoadError(true) })
    api.email.unreadCount().then(res => setUnreadEmails(res.unread_count || 0)).catch(() => { console.warn('useHubData: falha ao carregar unreadEmails') })
    api.historico.goat().then(res => {
      if (res.meus_titulos) setTrofeus(res.meus_titulos.slice(-3).reverse())
    }).catch(() => { console.warn('useHubData: falha ao carregar trofeus (goat)') })

    if (typeof window !== 'undefined' && window.localStorage.getItem(MATCH_AUTOSAVE_KEY) === null) {
      setMostrarPromptAutoSave(true)
    }
    const stored = localStorage.getItem('tennislegacy.lastSave')
    if (stored) setLastSaveTime(stored)

    Promise.all([
      api.jogador.rivalidades().catch(() => ({ rivalidades: [] })),
      api.jogador.historicoPartidas().catch(() => ({ historico: [] })),
    ]).then(([rivRes, histRes]) => {
      const currentRank = jogador?.ranking ?? 0
      const prevRank = parseInt(localStorage.getItem(PREV_RANK_KEY) ?? String(currentRank), 10)
      if (currentRank > 0) localStorage.setItem(PREV_RANK_KEY, String(currentRank))
      const events = gerarEventosCarreira({
        historico: histRes.historico ?? [],
        rivalidades: rivRes.rivalidades ?? [],
        ranking: currentRank,
        rankingAnterior: prevRank,
        nivel: jogador?.nivel ?? 1,
        semana: semana ?? 1,
        nomeJogador: jogador?.nome ?? '',
      })
      setCareerEvents(events)
    })
  }, [semana, jogador?.ranking, jogador?.nivel, jogador?.nome])

  return {
    unreadEmails,
    loadError,
    trofeus,
    careerEvents,
    lastSaveTime,
    setLastSaveTime,
    mostrarPromptAutoSave,
    setMostrarPromptAutoSave,
    setLoadError,
  }
}
