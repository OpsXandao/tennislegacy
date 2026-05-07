import { useEffect, useState } from 'react'
import { X, Trophy, Users } from 'lucide-react'
import { motion, AnimatePresence } from 'motion/react'
import { api } from '../../../api/client'

interface BracketData {
  nome: string
  tipo: string
  fase_atual: string
  campeao_simples: string | null
  campeao_duplas: string | null
  rodadas: Record<string, Array<{ j1: string; j2: string }>>
  resultados: Record<string, Array<{ j1: string; j2: string; vencedor: string; placar: string }>>
  rodadas_duplas: Record<string, Array<{ j1: string; j2: string }>>
  resultados_duplas: Record<string, Array<{ j1: string; j2: string; vencedor: string; placar: string }>>
}

export function BracketModal({
  torneio,
  tour,
  onClose,
}: {
  torneio: string
  tour: 'atp' | 'wta'
  onClose: () => void
}) {
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<BracketData | null>(null)
  const [tab, setTab] = useState<'simples' | 'duplas'>('simples')

  useEffect(() => {
    api.mundo
      .bracket(torneio, tour)
      .then((d) => setData(d as BracketData))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [torneio, tour])

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[200] bg-black/95 flex flex-col"
      >
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <div>
            <div className="arcade-font text-[11px] text-[#ffe600]">{torneio.toUpperCase()}</div>
            <div className="pixel-font text-[8px] text-[#888] mt-0.5">
              {tour.toUpperCase()} · {data?.tipo || ''}
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 border border-white/20 text-white active:bg-white/10"
          >
            <X size={18} />
          </button>
        </div>

        {loading ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="pixel-font text-[#00ff88] text-xs animate-pulse">CARREGANDO...</div>
          </div>
        ) : !data ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="pixel-font text-[#888] text-xs">TORNEIO NÃO INICIADO</div>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {data.campeao_simples && (
              <div className="border-2 border-[#ffe600] bg-[#ffe600]/10 p-3 flex items-center gap-3">
                <Trophy size={18} className="text-[#ffe600] shrink-0" />
                <div>
                  <div className="pixel-font text-[8px] text-[#888]">CAMPEÃO SIMPLES</div>
                  <div className="arcade-font text-[11px] text-[#ffe600]">
                    {data.campeao_simples.toUpperCase()}
                  </div>
                </div>
              </div>
            )}
            {data.campeao_duplas && (
              <div className="border-2 border-[#00e5ff] bg-[#00e5ff]/10 p-3 flex items-center gap-3">
                <Users size={18} className="text-[#00e5ff] shrink-0" />
                <div>
                  <div className="pixel-font text-[8px] text-[#888]">CAMPEÃO DUPLAS</div>
                  <div className="arcade-font text-[11px] text-[#00e5ff]">
                    {data.campeao_duplas.toUpperCase()}
                  </div>
                </div>
              </div>
            )}

            <div className="flex items-center gap-2">
              <div className="pixel-font text-[8px] text-[#888]">FASE ATUAL:</div>
              <div className="arcade-font text-[9px] text-[#00ff88]">
                {data.fase_atual.toUpperCase()}
              </div>
            </div>

            <div className="flex gap-2">
              {(['simples', 'duplas'] as const).map((t) => (
                <button
                  key={t}
                  onClick={() => setTab(t)}
                  className={`flex-1 py-2 arcade-font text-[9px] border-2 transition-colors ${
                    tab === t
                      ? 'bg-[#00ff88] text-black border-[#00ff88]'
                      : 'border-white/20 text-white'
                  }`}
                >
                  {t.toUpperCase()}
                </button>
              ))}
            </div>

            {(() => {
              const resultados = tab === 'simples' ? data.resultados : data.resultados_duplas
              const rodadas = tab === 'simples' ? data.rodadas : data.rodadas_duplas
              const fases = [
                ...Object.keys(resultados),
                ...Object.keys(rodadas).filter((f) => !(f in resultados)),
              ]

              if (fases.length === 0) {
                return (
                  <div className="text-center py-8 pixel-font text-[8px] text-[#666]">
                    SEM DADOS DISPONÍVEIS
                  </div>
                )
              }

              return (
                <div className="space-y-4">
                  {fases.map((fase) => {
                    const res = resultados[fase] || []
                    const conf = rodadas[fase] || []
                    return (
                      <div key={fase}>
                        <div className="pixel-font text-[8px] text-[#ffe600] mb-2">
                          {fase.toUpperCase()}
                        </div>
                        <div className="space-y-1">
                          {res.map((r, i) => (
                            <div
                              key={i}
                              className="border border-white/10 bg-black/40 p-2 text-[8px]"
                            >
                              <span className={r.vencedor === r.j1 ? 'text-[#00ff88]' : 'text-white/50'}>
                                {r.j1}
                              </span>
                              <span className="text-[#888] mx-1">vs</span>
                              <span className={r.vencedor === r.j2 ? 'text-[#00ff88]' : 'text-white/50'}>
                                {r.j2}
                              </span>
                              {r.placar && (
                                <span className="text-[#ffe600] ml-2">{r.placar}</span>
                              )}
                            </div>
                          ))}
                          {conf
                            .filter((c) => !res.some((r) => r.j1 === c.j1 && r.j2 === c.j2))
                            .map((c, i) => (
                              <div
                                key={`p-${i}`}
                                className="border border-white/5 bg-black/20 p-2 text-[8px] text-white/40"
                              >
                                {c.j1} vs {c.j2}
                              </div>
                            ))}
                        </div>
                      </div>
                    )
                  })}
                </div>
              )
            })()}
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  )
}
