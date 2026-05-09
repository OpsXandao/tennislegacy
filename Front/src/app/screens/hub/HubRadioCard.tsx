import { Pause, Play, Radio, SkipForward, Volume2 } from 'lucide-react'

import type { HubRadioStation } from './radio/stations'

interface HubRadioCardProps {
  erro: string
  playing: boolean
  station: HubRadioStation
  stations: HubRadioStation[]
  volume: number
  setVolume: (value: number) => void
  togglePlay: () => void
  trocarEstacao: (id: string) => void
  avancarEstacao: () => void
}

export function HubRadioCard({
  erro,
  playing,
  station,
  stations,
  volume,
  setVolume,
  togglePlay,
  trocarEstacao,
  avancarEstacao,
}: HubRadioCardProps) {
  return (
    <section
      className="mx-4 mt-4 border-2 p-4"
      style={{
        borderColor: `${station.color}88`,
        background: `linear-gradient(135deg, ${station.color}12 0%, rgba(3,8,10,0.96) 72%)`,
        boxShadow: `0 0 18px ${station.color}22`,
      }}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Radio size={14} style={{ color: station.color }} />
            <span className="text-[9px]" style={{ fontFamily: 'var(--font-pixel)', color: station.color }}>
              HUB RADIO
            </span>
          </div>
          <div className="mt-2 text-[14px] text-white" style={{ fontFamily: 'var(--font-pixel)' }}>
            {station.nome}
          </div>
          <div className="mt-1 text-[9px] uppercase text-white/55" style={{ fontFamily: 'var(--font-arcade)' }}>
            {station.tagline} • {station.bpm} BPM
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={togglePlay}
            className="flex h-10 w-10 items-center justify-center border-2"
            style={{ borderColor: station.color, color: station.color }}
            aria-label={playing ? 'Pausar rádio' : 'Tocar rádio'}
          >
            {playing ? <Pause size={16} /> : <Play size={16} fill={station.color} />}
          </button>
          <button
            type="button"
            onClick={avancarEstacao}
            className="flex h-10 w-10 items-center justify-center border-2 border-white/25 text-white/75"
            aria-label="Próxima estação"
          >
            <SkipForward size={16} />
          </button>
        </div>
      </div>

      <div className="mt-4 flex gap-2 overflow-x-auto pb-1">
        {stations.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => trocarEstacao(item.id)}
            className="border px-2 py-1 text-left"
            style={{
              borderColor: item.id === station.id ? item.color : '#33514b',
              background: item.id === station.id ? `${item.color}18` : 'transparent',
            }}
          >
            <div className="text-[8px]" style={{ fontFamily: 'var(--font-pixel)', color: item.id === station.id ? item.color : '#7ca699' }}>
              {item.nome}
            </div>
            <div className="text-[8px] text-white/35" style={{ fontFamily: 'var(--font-arcade)' }}>
              {item.bpm} BPM
            </div>
          </button>
        ))}
      </div>

      <div className="mt-4 flex items-center gap-3">
        <Volume2 size={14} style={{ color: station.color }} />
        <input
          type="range"
          min={0}
          max={100}
          step={1}
          value={volume}
          onChange={(event) => setVolume(Number(event.target.value))}
          className="w-full accent-neon-green"
        />
        <span className="w-10 text-right text-[9px] text-white/65" style={{ fontFamily: 'var(--font-pixel)' }}>
          {volume}%
        </span>
      </div>

      {erro ? (
        <div className="mt-3 text-[9px] text-[#ff7d9e]" style={{ fontFamily: 'var(--font-arcade)' }}>
          {erro}
        </div>
      ) : (
        <div className="mt-3 text-[9px] text-white/45" style={{ fontFamily: 'var(--font-arcade)' }}>
          {playing ? 'TRANSMISSÃO AO VIVO NO HUB' : 'APERTE PLAY PARA LIGAR A ESTAÇÃO'}
        </div>
      )}
    </section>
  )
}
