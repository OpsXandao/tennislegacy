import { useEffect, useRef, useState } from 'react'

import { HubRadioEngine } from './engine'
import { HUB_RADIO_LOCAL_PLAYLISTS } from './localPlaylists'
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
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [stationId, setStationId] = useState(loadInitialStationId)
  const [playing, setPlaying] = useState(false)
  const [volume, setVolume] = useState(loadInitialVolume)
  const [erro, setErro] = useState('')
  const [trackIndex, setTrackIndex] = useState(0)

  const stationBase =
    HUB_RADIO_STATIONS.find((item) => item.id === stationId) ?? HUB_RADIO_STATIONS[0]
  const station = {
    ...stationBase,
    tracks: HUB_RADIO_LOCAL_PLAYLISTS[stationBase.id] ?? stationBase.tracks,
  }
  const currentTrack = station.tracks[trackIndex] ?? null
  const sourceType = station.tracks.length > 0 ? 'playlist' : 'procedural'

  if (!engineRef.current && typeof window !== 'undefined') {
    engineRef.current = new HubRadioEngine()
  }
  if (!audioRef.current && typeof window !== 'undefined') {
    audioRef.current = new Audio()
    audioRef.current.preload = 'metadata'
  }

  useEffect(() => {
    if (typeof window === 'undefined') return
    window.localStorage.setItem(HUB_RADIO_STATION_KEY, stationId)
  }, [stationId])

  useEffect(() => {
    if (typeof window === 'undefined') return
    window.localStorage.setItem(HUB_RADIO_VOLUME_KEY, String(volume))
    engineRef.current?.setVolume(volume / 100)
    if (audioRef.current) {
      audioRef.current.volume = volume / 100
    }
  }, [volume])

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return
    const onEnded = () => {
      if (station.tracks.length <= 1) {
        void audio.play().catch(() => {})
        return
      }
      setTrackIndex((current) => {
        const next = (current + 1) % station.tracks.length
        return next
      })
    }
    audio.addEventListener('ended', onEnded)
    return () => {
      audio.removeEventListener('ended', onEnded)
      audio.pause()
      audio.src = ''
      engineRef.current?.stop()
    }
  }, [station.tracks.length])

  useEffect(() => {
    if (!audioRef.current || sourceType !== 'playlist' || !currentTrack) return
    audioRef.current.src = currentTrack.src
    audioRef.current.volume = volume / 100
    if (playing) {
      void audioRef.current.play().catch((error) => {
        setErro(error instanceof Error ? error.message : 'Falha ao tocar a faixa.')
        setPlaying(false)
      })
    }
  }, [currentTrack, playing, sourceType, volume])

  async function togglePlay() {
    try {
      if (playing) {
        engineRef.current?.stop()
        audioRef.current?.pause()
        setPlaying(false)
        return
      }
      if (sourceType === 'playlist' && currentTrack && audioRef.current) {
        engineRef.current?.stop()
        audioRef.current.src = currentTrack.src
        audioRef.current.volume = volume / 100
        await audioRef.current.play()
      } else {
        audioRef.current?.pause()
        await engineRef.current?.start(station, volume / 100)
      }
      setErro('')
      setPlaying(true)
    } catch (error) {
      setErro(error instanceof Error ? error.message : 'Falha ao iniciar a rádio.')
      setPlaying(false)
    }
  }

  async function trocarEstacao(nextId: string) {
    setStationId(nextId)
    setTrackIndex(0)
    if (playing && engineRef.current) {
      try {
        const nextStationBase = HUB_RADIO_STATIONS.find((item) => item.id === nextId) ?? HUB_RADIO_STATIONS[0]
        const nextTracks = HUB_RADIO_LOCAL_PLAYLISTS[nextStationBase.id] ?? nextStationBase.tracks
        if (nextTracks.length > 0 && audioRef.current) {
          engineRef.current.stop()
          audioRef.current.pause()
          audioRef.current.src = nextTracks[0].src
          audioRef.current.volume = volume / 100
          await audioRef.current.play()
        } else {
          audioRef.current?.pause()
          await engineRef.current.start({ ...nextStationBase, tracks: nextTracks }, volume / 100)
        }
      } catch (error) {
        setErro(error instanceof Error ? error.message : 'Falha ao trocar a estação.')
        setPlaying(false)
      }
    }
  }

  async function avancarFaixaOuEstacao() {
    if (sourceType === 'playlist' && station.tracks.length > 0) {
      const nextIndex = (trackIndex + 1) % station.tracks.length
      setTrackIndex(nextIndex)
      if (playing && audioRef.current) {
        try {
          audioRef.current.pause()
          audioRef.current.src = station.tracks[nextIndex].src
          audioRef.current.volume = volume / 100
          await audioRef.current.play()
        } catch (error) {
          setErro(error instanceof Error ? error.message : 'Falha ao trocar a faixa.')
          setPlaying(false)
        }
      }
      return
    }
    const idx = HUB_RADIO_STATIONS.findIndex((item) => item.id === station.id)
    const nextStation = HUB_RADIO_STATIONS[(idx + 1) % HUB_RADIO_STATIONS.length]
    await trocarEstacao(nextStation.id)
  }

  return {
    currentTrack,
    erro,
    playing,
    station,
    stations: HUB_RADIO_STATIONS,
    sourceType,
    volume,
    setVolume,
    togglePlay,
    trocarEstacao,
    avancarFaixaOuEstacao,
  }
}
