import { useEffect, useState } from 'react'
import { Trophy } from 'lucide-react'
import { api } from '../../../api/client'

type TituloJogador = { torneio: string; tipo: string; categoria: string; semana: number; ano: number; modalidade: string }
type CampeaoNpc = { torneio: string; campeao: string | null; ano: number; semana: number; tipo: string }

function tourAccent(tipo: string) {
  if (tipo.includes('Grand Slam')) return '#ffe600'
  if (tipo.includes('1000') || tipo.includes('Masters')) return '#ff5f8f'
  if (tipo.includes('500')) return '#00e5ff'
  return '#00ff88'
}

function badgeTipo(tipo: string) {
  if (tipo.includes('Grand Slam')) return 'GS'
  if (tipo.includes('1000')) return '1000'
  if (tipo.includes('500')) return '500'
  if (tipo.includes('Finals')) return 'FINALS'
  return '250'
}

export function CampeoesTab() {
  const [data, setData] = useState<{ ano: number; titulos_jogador: TituloJogador[]; campeoes_npc: CampeaoNpc[] } | null>(null)
  const [erro, setErro] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.historico.campeoesTemporada()
      .then(setData)
      .catch(() => setErro('Erro ao carregar campeões.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex justify-center py-12">
      <div className="w-5 h-5 border border-neon-yellow/20 border-t-neon-yellow rounded-full animate-spin" />
    </div>
  )

  if (erro) return <p className="arcade-font text-[9px] text-neon-pink text-center py-8">{erro}</p>
  if (!data) return null

  const meusTotal = data.titulos_jogador.length
  const npcTotal = data.campeoes_npc.length

  return (
    <div className="space-y-6">
      {/* Meus títulos */}
      <section>
        <div className="flex items-center gap-2 mb-3">
          <Trophy size={11} className="text-neon-yellow/70" />
          <span className="arcade-font text-[8px] tracking-[0.3em] text-neon-yellow/60">
            MEUS TÍTULOS — {data.ano}
          </span>
          <div className="flex-1 h-px" style={{ background: 'linear-gradient(90deg, rgba(255,230,0,0.2), transparent)' }} />
          <span className="arcade-font text-[8px] text-neon-yellow">{meusTotal}</span>
        </div>

        {meusTotal === 0 ? (
          <p className="arcade-font text-[8px] text-white/25 text-center py-4">SEM TÍTULOS AINDA</p>
        ) : (
          <div className="space-y-1">
            {data.titulos_jogador.map((t, i) => {
              const accent = tourAccent(t.tipo)
              return (
                <div
                  key={i}
                  className="flex items-center gap-3 px-3 py-2.5"
                  style={{ borderLeft: `2px solid ${accent}`, background: `${accent}08` }}
                >
                  <span
                    className="arcade-font text-[7px] px-1.5 py-0.5 shrink-0"
                    style={{ border: `1px solid ${accent}50`, color: accent }}
                  >
                    {badgeTipo(t.tipo)}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="pixel-font text-[12px] text-white truncate">{t.torneio}</div>
                    <div className="arcade-font text-[7px] text-white/30 mt-0.5">
                      SEM. {t.semana} · {t.modalidade.toUpperCase()}
                    </div>
                  </div>
                  <Trophy size={10} style={{ color: accent, opacity: 0.7 }} />
                </div>
              )
            })}
          </div>
        )}
      </section>

      {/* Campeões do circuito */}
      <section>
        <div className="flex items-center gap-2 mb-3">
          <span className="arcade-font text-[8px] tracking-[0.3em] text-white/30">
            CIRCUITO — {data.ano}
          </span>
          <div className="flex-1 h-px" style={{ background: 'linear-gradient(90deg, rgba(255,255,255,0.08), transparent)' }} />
          <span className="arcade-font text-[8px] text-white/30">{npcTotal}</span>
        </div>

        {npcTotal === 0 ? (
          <p className="arcade-font text-[8px] text-white/20 text-center py-4">NENHUM TORNEIO FINALIZADO</p>
        ) : (
          <div className="space-y-1">
            {data.campeoes_npc.map((c, i) => {
              const accent = tourAccent(c.tipo)
              return (
                <div
                  key={i}
                  className="flex items-center gap-3 px-3 py-2"
                  style={{ borderLeft: `1px solid ${accent}30` }}
                >
                  <span
                    className="arcade-font text-[7px] px-1 py-0.5 shrink-0 text-white/30"
                    style={{ border: '1px solid rgba(255,255,255,0.1)' }}
                  >
                    {badgeTipo(c.tipo)}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="pixel-font text-[11px] text-white/60 truncate">{c.torneio}</div>
                    <div
                      className="arcade-font text-[8px] truncate mt-0.5"
                      style={{ color: accent, opacity: 0.9 }}
                    >
                      {c.campeao ?? '—'}
                    </div>
                  </div>
                  <span className="arcade-font text-[7px] text-white/20 shrink-0">S{c.semana}</span>
                </div>
              )
            })}
          </div>
        )}
      </section>
    </div>
  )
}
