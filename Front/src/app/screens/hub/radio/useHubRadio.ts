import { useEffect, useRef, useState } from 'react'

import { HubRadioEngine } from './engine'
import { HUB_RADIO_STATIONS } from './stations'

const HUB_RADIO_STATION_KEY = 'tennislegacy.hubRadio.station'
const HUB_RADIO_VOLUME_KEY = 'tennislegacy.hubRadio.volume'

function loadInitialStationId() {
  if (typeof window === 'undefined') return HUB_RADIO_STATIONS[0].id
  return window.localStorage.getItem(HUB_RADIO_STATION_KEY) ?? HUB_RADIO_STATIONS[0].id
}

function loadInitialVolume() {
  if (typeof window === 'undefined') return 45
  const raw = Number(window.localStorage.getItem(HUB_RADIO_VOLUME_KEY) ?? '45')
  return Number.isFinite(raw) ? Math.max(0, Math.min(100, raw)) : 45
}

export function useHubRadio() {
  const engineRef = useRef<HubRadioEngine | null>(null)
  const [stationId, setStationId] = useState(loadInitialStationId)
  const [playing, setPlaying] = useState(false)
  const [volume, setVolume] = useState(loadInitialVolume)
  const [erro, setErro] = useState('')

  const station =
    HUB_RADIO_STATIONS.find((item) => item.id === stationId) ?? HUB_RADIO_STATIONS[0]

  if (!engineRef.current && typeof window !== 'undefined') {
    engineRef.current = new HubRadioEngine()
  }

  useEffect(() => {
    if (typeof window === 'undefined') return
    window.localStorage.setItem(HUB_RADIO_STATION_KEY, stationId)
  }, [stationId])

  useEffect(() => {
    if (typeof window === 'undefined') return
    window.localStorage.setItem(HUB_RADIO_VOLUME_KEY, String(volume))
    engineRef.current?.setVolume(volume / 100)
  }, [volume])

  useEffect(() => {
    return () => {
      engineRef.current?.stop()
    }
  }, [])

  async function togglePlay() {
    if (!engineRef.current) return
    try {
      if (playing) {
        engineRef.current.stop()
        setPlaying(false)
        return
      }
      await engineRef.current.start(station, volume / 100)
      setErro('')
      setPlaying(true)
    } catch (error) {
      setErro(error instanceof Error ? error.message : 'Falha ao iniciar a rádio.')
      setPlaying(false)
    }
  }

  async function trocarEstacao(nextId: string) {
    setStationId(nextId)
    if (playing && engineRef.current) {
      try {
        const nextStation = HUB_RADIO_STATIONS.find((item) => item.id === nextId) ?? HUB_RADIO_STATIONS[0]
        await engineRef.current.start(nextStation, volume / 100)
      } catch (error) {
        setErro(error instanceof Error ? error.message : 'Falha ao trocar a estação.')
        setPlaying(false)
      }
    }
  }

  function avancarEstacao() {
    const idx = HUB_RADIO_STATIONS.findIndex((item) => item.id === station.id)
    const nextStation = HUB_RADIO_STATIONS[(idx + 1) % HUB_RADIO_STATIONS.length]
    void trocarEstacao(nextStation.id)
  }

  return {
    erro,
    playing,
    station,
    stations: HUB_RADIO_STATIONS,
    volume,
    setVolume,
    togglePlay,
    trocarEstacao,
    avancarEstacao,
  }
}
