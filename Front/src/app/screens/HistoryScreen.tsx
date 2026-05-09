import { useState, useEffect } from 'react'
import { Trophy, Crown, Calendar } from 'lucide-react'
import { motion } from 'motion/react'
import { NeonCard, PageHeader } from '../components'
import { api } from '../../api/client'

export function HistoryScreen() {
  const [data, setData] = useState<{ recordes: any; meus_titulos: any[] } | null>(null)
  const [campeoes, setCampeoes] = useState<Record<string, any>>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.historico.goat(), api.historico.campeoes()])
      .then(([goat, champs]) => {
        setData(goat)
        setCampeoes(champs.campeoes || {})
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="app-shell min-h-screen flex flex-col">
      <PageHeader title="HALL DA FAMA" color="yellow" backTo="/player" />

      <div className="flex-1 p-4 space-y-6 overflow-y-auto pb-24">
        {loading ? (
          <div className="text-center py-20 pixel-font text-neon-yellow animate-pulse text-xs">CARREGANDO ARQUIVOS HISTÓRICOS...</div>
        ) : (
          <>
            {/* Recordes Mundiais (GOAT) */}
            <section className="space-y-4">
              <div className="flex items-center gap-2 mb-2">
                <Crown className="text-neon-yellow" size={20} />
                <h3 className="arcade-font text-xs text-neon-yellow tracking-widest uppercase">Recordes Mundiais</h3>
              </div>

              <div className="grid grid-cols-1 gap-4">
                <NeonCard variant="yellow" hover={false} className="bg-black/40">
                  <div className="arcade-font text-[10px] text-[#888] mb-3 uppercase">Mais Títulos na Carreira</div>
                  <div className="space-y-2">
                    {data?.recordes.mais_titulos?.length > 0 ? (
                      data.recordes.mais_titulos.map((r: any, i: number) => (
                        <div key={i} className="flex justify-between items-center border-b border-neon-yellow/10 pb-1">
                          <span className="arcade-font text-[10px] text-white">{i + 1}. {r.nome}</span>
                          <span className="pixel-font text-[10px] text-neon-yellow">{r.titulos}</span>
                        </div>
                      ))
                    ) : (
                      <div className="arcade-font text-[9px] text-[#444]">Nenhum registro encontrado.</div>
                    )}
                  </div>
                </NeonCard>

                <NeonCard variant="yellow" hover={false} className="bg-black/40">
                  <div className="arcade-font text-[10px] text-[#888] mb-3 uppercase">Semanas no Topo (#1)</div>
                  <div className="space-y-2">
                    {data?.recordes.mais_semanas_no_topo?.length > 0 ? (
                      data.recordes.mais_semanas_no_topo.map((r: any, i: number) => (
                        <div key={i} className="flex justify-between items-center border-b border-neon-yellow/10 pb-1">
                          <span className="arcade-font text-[10px] text-white">{i + 1}. {r.nome}</span>
                          <span className="pixel-font text-[10px] text-neon-yellow">{r.semanas}</span>
                        </div>
                      ))
                    ) : (
                      <div className="arcade-font text-[9px] text-[#444]">Nenhum registro encontrado.</div>
                    )}
                  </div>
                </NeonCard>
              </div>
            </section>

            {/* Galeria de Troféus do Jogador */}
            <section className="space-y-4">
              <div className="flex items-center gap-2 mb-2">
                <Trophy className="text-neon-green" size={20} />
                <h3 className="arcade-font text-xs text-neon-green tracking-widest uppercase">Minha Galeria</h3>
              </div>

              {data?.meus_titulos?.length === 0 ? (
                <div className="text-center py-12 border-2 border-dashed border-[#333] arcade-font text-[10px] text-[#444]">
                  VOCÊ AINDA NÃO CONQUISTOU TÍTULOS.
                </div>
              ) : (
                <div className="grid grid-cols-1 gap-3">
                  {data?.meus_titulos.map((t: any, i: number) => (
                    <motion.div 
                      key={i}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.05 }}
                    >
                      <NeonCard variant={t.tipo === 'Grand Slam' ? 'yellow' : 'green'} hover={false}>
                        <div className="flex justify-between items-center">
                          <div className="flex items-center gap-3">
                            <div className="text-2xl">{t.tipo === 'Grand Slam' ? '⭐' : '🏆'}</div>
                            <div>
                              <div className="arcade-font text-[10px] text-white">{t.torneio.toUpperCase()}</div>
                              <div className="arcade-font text-[8px] text-[#888] mt-1">{t.tipo} — {t.ano}</div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="pixel-font text-[10px] text-neon-yellow">VENCEU</div>
                            <div className="arcade-font text-[7px] text-[#888] mt-1">{t.adversario_final}</div>
                          </div>
                        </div>
                      </NeonCard>
                    </motion.div>
                  ))}
                </div>
              )}
            </section>

            <section className="space-y-4">
              <div className="flex items-center gap-2 mb-2">
                <Calendar className="text-neon-cyan" size={20} />
                <h3 className="arcade-font text-xs text-neon-cyan tracking-widest uppercase">Campeões por Ano</h3>
              </div>

              {Object.keys(campeoes).length === 0 ? (
                <div className="text-center py-12 border-2 border-dashed border-[#333] arcade-font text-[10px] text-[#444]">
                  SEM REGISTRO DE CAMPEÕES AINDA.
                </div>
              ) : (
                <div className="grid grid-cols-1 gap-3">
                  {Object.entries(campeoes)
                    .sort(([a], [b]) => Number(b) - Number(a))
                    .slice(0, 8)
                    .map(([ano, torneios], i) => (
                      <motion.div
                        key={ano}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.05 }}
                      >
                        <NeonCard variant="cyan" hover={false}>
                          <div className="mb-3 flex items-center justify-between">
                            <div className="arcade-font text-[10px] text-neon-cyan uppercase">{ano}</div>
                            <div className="text-[8px] text-[#666]">{Object.keys(torneios as Record<string, unknown>).length} torneios</div>
                          </div>
                          <div className="space-y-2">
                            {Object.entries(torneios as Record<string, any>).slice(0, 6).map(([torneio, campeao]) => (
                              <div key={torneio} className="flex justify-between items-center border-b border-neon-cyan/10 pb-1">
                                <span className="arcade-font text-[10px] text-white">{torneio}</span>
                                <span className="arcade-font text-[10px] text-neon-cyan">{String(campeao)}</span>
                              </div>
                            ))}
                          </div>
                        </NeonCard>
                      </motion.div>
                    ))}
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </div>
  )
}
