import { motion } from 'motion/react'
import { Clock3, MapPinned } from 'lucide-react'
import { PixelFlag } from '../../components'
import type { MundoTorneio } from '../../../types'

interface UpcomingTournamentCardProps {
  torneio: MundoTorneio
  semanaAtual: number
  index: number
  onSelect: (nome: string, tour: string) => void
}

export function UpcomingTournamentCard({
  torneio,
  semanaAtual,
  index,
  onSelect,
}: UpcomingTournamentCardProps) {
  const tour = String(torneio.tipo || '').toUpperCase().includes('WTA') ? 'wta' : 'atp'

  return (
    <motion.div
      initial={{ opacity: 0, x: -16 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.03 }}
      onClick={() => onSelect(torneio.nome, tour)}
      className="border-2 border-[#00e5ff]/30 bg-[#1a1a2e] p-3 cursor-pointer active:scale-[0.98] transition-transform"
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <div>
          <div className="arcade-font text-[10px] text-[#00e5ff]">{torneio.nome}</div>
          <div className="flex items-center gap-1.5 mt-0.5">
            {torneio.codigo_pais && <PixelFlag countryCode={torneio.codigo_pais} size="sm" />}
            <div className="pixel-font text-[7px] text-[#888]">
              {torneio.local}, {torneio.pais}
            </div>
          </div>
        </div>
        <div
          className={`border px-2 py-1 pixel-font text-[7px] shrink-0 ${
            torneio.semana === semanaAtual
              ? 'border-[#ffe600] text-[#ffe600]'
              : 'border-[#00ff88] text-[#00ff88]'
          }`}
        >
          {torneio.semana === semanaAtual ? 'AGORA' : `SEM ${torneio.semana}`}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 mb-3">
        {[
          { label: 'TIPO', value: torneio.tipo, color: '#fff' },
          { label: 'SUPERFÍCIE', value: torneio.superficie, color: '#00ff88' },
          { label: 'PRÊMIO', value: torneio.premiacao || '-', color: '#ffe600' },
        ].map(({ label, value, color }) => (
          <div key={label}>
            <div className="pixel-font text-[7px] text-[#666]">{label}</div>
            <div className="pixel-font text-[8px] uppercase mt-0.5" style={{ color }}>
              {value}
            </div>
          </div>
        ))}
      </div>

      <div className="grid gap-2 sm:grid-cols-2">
        <div className="border border-[#1f3d49] bg-black/20 px-2 py-2">
          <div className="flex items-center gap-1 text-[#00e5ff] mb-1">
            <Clock3 size={10} />
            <span className="pixel-font text-[7px]">HORÁRIO</span>
          </div>
          <div className="arcade-font text-[9px] text-white">
            {torneio.horario_local ?? '13:00'} • {torneio.sessao_label ?? 'Sessão principal'}
          </div>
        </div>
        <div className="border border-[#3f3520] bg-black/20 px-2 py-2">
          <div className="flex items-center gap-1 text-[#ffe600] mb-1">
            <MapPinned size={10} />
            <span className="pixel-font text-[7px]">QUADRA</span>
          </div>
          <div className="arcade-font text-[9px] text-white truncate">
            {torneio.quadra_nome ?? 'Quadra Central'}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
