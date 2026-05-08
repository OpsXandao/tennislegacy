import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router'
import { api } from '../../../api/client'
import { useGameStore } from '../../../store/gameStore'
import type { CampeaoSemana, TorneioCalendario } from '../../../types'
import type { CalendarCallup } from './types'

export function useCalendarScreen() {
  const navigate = useNavigate()
  const { semana: semanaAtual, ano } = useGameStore()
  const setTorneio = useGameStore((state) => state.setTorneio)
  const setSemana = useGameStore((state) => state.setSemana)
  const scrollRef = useRef<HTMLDivElement>(null)

  const [selectedWeek, setSelectedWeek] = useState(semanaAtual)
  const [torneiosSemana, setTorneiosSemana] = useState<TorneioCalendario[]>([])
  const [semanasTorneio, setSemanasTorneio] = useState<Set<number>>(new Set())
  const [loading, setLoading] = useState(true)
  const [torneioParaInscrever, setTorneioParaInscrever] = useState<TorneioCalendario | null>(null)
  const [inscrevendo, setInscrevendo] = useState(false)
  const [erroInscricao, setErroInscricao] = useState('')
  const [convocacao, setConvocacao] = useState<CalendarCallup | null>(null)
  const [campeoesSemana, setCampeoesSemana] = useState<CampeaoSemana[]>([])

  async function checarConvocacao() {
    try {
      const response = await api.torneio.checarConvocacao()
      setConvocacao(response)
    } catch {
      setConvocacao(null)
    }
  }

  useEffect(() => {
    api.calendario
      .atual()
      .then((response) => {
        setSemana(response.semana, response.ano)
        setSelectedWeek(response.semana)
        setTorneiosSemana(response.torneios)
        setSemanasTorneio((current) => {
          const next = new Set(current)
          response.torneios.forEach((torneio) => next.add(torneio.semana))
          return next
        })
        checarConvocacao()
      })
      .catch(() => {})
  }, [setSemana])

  useEffect(() => {
    setErroInscricao('')
    if (selectedWeek === semanaAtual) {
      checarConvocacao()
      return
    }
    setConvocacao(null)
  }, [selectedWeek, semanaAtual])

  useEffect(() => {
    setLoading(true)
    api.calendario
      .semana(selectedWeek)
      .then((response) => {
        setTorneiosSemana(response.torneios)
        if (response.torneios.length === 0) return
        setSemanasTorneio((current) => {
          const next = new Set(current)
          response.torneios.forEach((torneio) => next.add(torneio.semana))
          return next
        })
      })
      .catch(() => setTorneiosSemana([]))
      .finally(() => setLoading(false))
  }, [selectedWeek])

  useEffect(() => {
    if (!scrollRef.current) return
    const selectedButton = scrollRef.current.querySelector(`[data-week="${selectedWeek}"]`)
    selectedButton?.scrollIntoView({ inline: 'center', behavior: 'smooth' })
  }, [selectedWeek])

  async function handleConfirmarInscricao(modalidade: string, parceiro?: string) {
    if (!torneioParaInscrever && !convocacao?.torneio) return

    setInscrevendo(true)
    const targetNome = torneioParaInscrever?.nome || convocacao?.torneio?.nome
    setTorneioParaInscrever(null)

    try {
      const response = await api.torneio.criar(modalidade as any, parceiro, targetNome)
      if (!response.ok) return

      setTorneio(response.torneio)
      if (response.torneio.destino_click_hub) {
        navigate(response.torneio.destino_click_hub)
      } else if ((response.torneio as { davis?: boolean }).davis) {
        navigate('/davis')
      } else {
        navigate('/tournament')
      }
    } catch {
      setErroInscricao('Erro ao entrar no torneio. Tente novamente.')
    } finally {
      setInscrevendo(false)
    }
  }

  async function handleRecusarConvocacao() {
    if (inscrevendo) return
    setInscrevendo(true)
    try {
      const response = await api.torneio.recusarConvocacao()
      if (response.ok) {
        setConvocacao(null)
      }
    } catch {
      setErroInscricao('Erro ao recusar convocação.')
    } finally {
      setInscrevendo(false)
    }
  }

  async function handleDescansar() {
    try {
      const response = await api.calendario.avancar()
      setSemana(response.semana, response.ano ?? ano)
      setSelectedWeek(response.semana)
      const campeoes = response.resumo_mundial?.campeoes ?? []
      if (campeoes.length > 0) {
        setCampeoesSemana(campeoes)
      }
    } catch {
      // silencioso
    }
  }

  return {
    ano,
    semanaAtual,
    selectedWeek,
    setSelectedWeek,
    torneiosSemana,
    semanasTorneio,
    loading,
    torneioParaInscrever,
    setTorneioParaInscrever,
    inscrevendo,
    erroInscricao,
    convocacao,
    campeoesSemana,
    scrollRef,
    handleConfirmarInscricao,
    handleRecusarConvocacao,
    handleDescansar,
    handleFecharCampeoes: () => setCampeoesSemana([]),
  }
}
