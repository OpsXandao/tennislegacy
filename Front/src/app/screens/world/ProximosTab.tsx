import { useEffect, useState } from 'react'
import { motion } from 'motion/react'
import { api } from '../../../api/client'
import { PixelFlag } from '../../components'
import type { MundoTorneio } from '../../../types'
import { TournamentDetailModal } from './TournamentDetailModal'
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
              <motion.div
                key={`${t.semana}-${t.nome}`}
                initial={{ opacity: 0, x: -16 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.03 }}
                onClick={() =>
                  setSelected({
                    nome: t.nome,
                    tour: String(t.tipo || '').toUpperCase().includes('WTA') ? 'wta' : 'atp',
                  })
                }
                className="border-2 border-[#00e5ff]/30 bg-[#1a1a2e] p-3 cursor-pointer active:scale-[0.98] transition-transform"
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <div className="arcade-font text-[10px] text-[#00e5ff]">{t.nome}</div>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      {t.codigo_pais && <PixelFlag countryCode={t.codigo_pais} size="sm" />}
                      <div className="pixel-font text-[7px] text-[#888]">
                        {t.local}, {t.pais}
                      </div>
                    </div>
                  </div>
                  <div
                    className={`border px-2 py-1 pixel-font text-[7px] shrink-0 ${
                      t.semana === semanaAtual
                        ? 'border-[#ffe600] text-[#ffe600]'
                        : 'border-[#00ff88] text-[#00ff88]'
                    }`}
                  >
                    {t.semana === semanaAtual ? 'AGORA' : `SEM ${t.semana}`}
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { label: 'TIPO', value: t.tipo, color: '#fff' },
                    { label: 'SUPERFÍCIE', value: t.superficie, color: '#00ff88' },
                    { label: 'PRÊMIO', value: t.premiacao || '-', color: '#ffe600' },
                  ].map(({ label, value, color }) => (
                    <div key={label}>
                      <div className="pixel-font text-[7px] text-[#666]">{label}</div>
                      <div className="pixel-font text-[8px] uppercase mt-0.5" style={{ color }}>
                        {value}
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
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
