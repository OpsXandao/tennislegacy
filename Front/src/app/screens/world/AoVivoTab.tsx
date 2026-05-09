import { useEffect, useState } from 'react'
import { ChevronRight, Trophy } from 'lucide-react'
import { motion } from 'motion/react'
import { api } from '../../../api/client'
import type { TorneioAoVivo } from '../../../types'
import { BracketModal } from './BracketModal'

function TourSection({
  label,
  list,
  color,
  onSelect,
}: {
  label: string
  list: TorneioAoVivo[]
  color: string
  onSelect: (nome: string, tour: 'atp' | 'wta') => void
}) {
  if (list.length === 0) return null
  return (
    <div>
      <div className="arcade-font text-[9px] mb-2" style={{ color }}>
        ── {label} ──
      </div>
      <div className="space-y-2">
        {list.map((t) => (
          <motion.button
            key={t.nome}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            onClick={() => onSelect(t.nome, t.tour === 'ATP' ? 'atp' : 'wta')}
            className="w-full border-2 border-white/10 bg-[#1a1a2e] p-3 text-left active:scale-[0.98] transition-transform"
            style={{
              borderColor: t.finalizado ? 'var(--neon-yellow)' : color + '40',
              boxShadow: t.finalizado ? '0 0 10px rgba(255,230,0,0.2)' : undefined,
            }}
          >
            <div className="flex items-start justify-between gap-2">
              <div>
                <div className="arcade-font text-[10px]" style={{ color }}>
                  {t.nome}
                </div>
                <div className="pixel-font text-[8px] text-[#888] mt-0.5">{t.tipo}</div>
              </div>
              <div className="flex items-center gap-1 shrink-0">
                {t.finalizado ? (
                  <div className="border border-neon-yellow px-1.5 py-0.5 pixel-font text-[7px] text-neon-yellow">
                    FIM
                  </div>
                ) : (
                  <div className="border border-neon-green px-1.5 py-0.5 pixel-font text-[7px] text-neon-green animate-pulse">
                    AO VIVO
                  </div>
                )}
                <ChevronRight size={12} className="text-[#888]" />
              </div>
            </div>
            {t.campeao_simples ? (
              <div className="mt-2 flex items-center gap-1.5">
                <Trophy size={10} className="text-neon-yellow" />
                <span className="pixel-font text-[8px] text-neon-yellow">
                  {t.campeao_simples.toUpperCase()}
                </span>
              </div>
            ) : (
              <div className="mt-2 pixel-font text-[8px] text-[#888]">FASE: {t.fase_atual}</div>
            )}
          </motion.button>
        ))}
      </div>
    </div>
  )
}

export function AoVivoTab() {
  const [loading, setLoading] = useState(true)
  const [torneios, setTorneios] = useState<TorneioAoVivo[]>([])
  const [selected, setSelected] = useState<{ nome: string; tour: 'atp' | 'wta' } | null>(null)

  useEffect(() => {
    api.mundo
      .aoVivo()
      .then((r) => setTorneios(r.torneios))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="py-16 text-center pixel-font text-xs text-neon-green animate-pulse">
        CARREGANDO...
      </div>
    )
  }

  const atp = torneios.filter((t) => t.tour === 'ATP')
  const wta = torneios.filter((t) => t.tour === 'WTA')

  return (
    <>
      {selected && (
        <BracketModal
          torneio={selected.nome}
          tour={selected.tour}
          onClose={() => setSelected(null)}
        />
      )}
      {torneios.length === 0 ? (
        <div className="py-16 text-center border border-[#333] pixel-font text-[10px] text-[#666]">
          NENHUM TORNEIO EM ANDAMENTO
        </div>
      ) : (
        <div className="space-y-5">
          <TourSection label="ATP" list={atp} color="var(--neon-cyan)" onSelect={setSelected} />
          <TourSection label="WTA" list={wta} color="#ff6eb4" onSelect={setSelected} />
        </div>
      )}
    </>
  )
}
