import { useEffect, useState } from 'react'
import { api } from '../../../api/client'
import type { MundoTorneio } from '../../../types'
import { TournamentDetailModal } from './TournamentDetailModal'
import { UpcomingTournamentCard } from './UpcomingTournamentCard'
import worldMapPixel from '../../../assets/maps/world-map-pixel.png'

export function ProximosTab() {
  const [loading, setLoading] = useState(true)
  const [semanaAtual, setSemanaAtual] = useState(1)
  const [torneios, setTorneios] = useState<MundoTorneio[]>([])
  const [noticias, setNoticias] = useState<string[]>([])
  const [selected, setSelected] = useState<{ nome: string; tour: string } | null>(null)

  useEffect(() => {
    Promise.all([api.mundo.proximos(), api.mundo.noticias()])
      .then(([res, news]) => {
        setSemanaAtual(res.semana_atual)
        setTorneios(res.torneios)
        setNoticias(news.noticias || [])
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="py-16 text-center pixel-font text-xs text-[#00ff88] animate-pulse">
        CARREGANDO...
      </div>
    )
  }

  return (
    <>
      {selected && (
        <TournamentDetailModal
          nome={selected.nome}
          tour={selected.tour}
          onClose={() => setSelected(null)}
        />
      )}

      <div className="space-y-5">
        <div className="overflow-hidden border-2 border-[#00e5ff]/40 bg-[#0b1020]">
          <img
            src={worldMapPixel}
            alt="Mapa mundi"
            className="h-auto w-full opacity-90"
            style={{ imageRendering: 'pixelated' }}
          />
        </div>

        <div>
          <div className="pixel-font text-[8px] text-[#888] mb-2">
            PRÓXIMAS 4 SEMANAS · SEMANA ATUAL {semanaAtual}
          </div>
          <div className="space-y-2">
            {torneios.map((t, i) => (
              <UpcomingTournamentCard
                key={`${t.semana}-${t.nome}`}
                torneio={t}
                semanaAtual={semanaAtual}
                index={i}
                onSelect={(nome, tour) => setSelected({ nome, tour: tour as 'atp' | 'wta' })}
              />
            ))}
            {torneios.length === 0 && (
              <div className="border border-[#333] p-6 text-center pixel-font text-[10px] text-[#666]">
                NENHUM TORNEIO ENCONTRADO
              </div>
            )}
          </div>
        </div>

        {noticias.length > 0 && (
          <div>
            <div className="pixel-font text-[8px] text-[#888] mb-2">NOTÍCIAS DO CIRCUITO</div>
            <div className="space-y-2">
              {noticias.map((n, i) => (
                <div
                  key={i}
                  className="border border-[#00ff88]/20 bg-black/30 p-3 pixel-font text-[8px] text-[#ddd]"
                >
                  {n}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </>
  )
}
