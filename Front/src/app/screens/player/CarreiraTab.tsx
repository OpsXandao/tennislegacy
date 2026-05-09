import { useNavigate } from 'react-router'
import { Trophy } from 'lucide-react'

interface Titulo {
  torneio: string
  ano: number | string
  tipo?: string
}

interface Props {
  carreira: {
    fase: string
    idade: number
    pico_carreira: number
    nivel: number
    xp: number
    xp_para_proximo: number
    titulos?: Titulo[]
  }
  meusTitulos: Titulo[]
}

export function CarreiraTab({ carreira, meusTitulos }: Props) {
  const navigate = useNavigate()

  const sumario = {
    GS: meusTitulos.filter((t) => t.tipo === 'Grand Slam').length,
    M1000: meusTitulos.filter((t) => t.tipo?.includes('1000')).length,
    Total: meusTitulos.length,
  }

  const idadePct = Math.min(99, Math.max(0, (carreira.idade - 16) / 24 * 100))
  const picoPct = Math.min(99, Math.max(1, (carreira.pico_carreira - 16) / 24 * 100))
  const xpPct = Math.min(100, (carreira.xp / Math.max(1, carreira.xp_para_proximo)) * 100)

  return (
    <div className="space-y-3">
      <div className="border-2 border-[#ffe600] bg-[#111] p-4">
        <div className="grid grid-cols-3 gap-3 text-center mb-4">
          <div>
            <div className="arcade-font text-[8px] text-[#888]">FASE</div>
            <div className="arcade-font text-[9px] text-[#ffe600] mt-1">{carreira.fase?.toUpperCase()}</div>
          </div>
          <div>
            <div className="arcade-font text-[8px] text-[#888]">IDADE</div>
            <div className="pixel-font text-xl text-white">{carreira.idade}</div>
          </div>
          <div>
            <div className="arcade-font text-[8px] text-[#888]">PICO</div>
            <div className="pixel-font text-xl text-[#00ff88]">{carreira.pico_carreira}a</div>
          </div>
        </div>
        <div>
          <div className="flex justify-between arcade-font text-[7px] text-[#333] mb-1">
            <span>16</span><span>40</span>
          </div>
          <div className="relative h-3 bg-[#222] border border-[#2a2a2a]">
            <div className="absolute top-0 bottom-0 w-0.5 bg-[#00ff88]" style={{ left: `${picoPct}%` }} />
            <div className="absolute top-0 bottom-0 w-1 bg-[#ffe600]" style={{ left: `${idadePct}%` }} />
          </div>
          <div className="flex justify-between arcade-font text-[7px] mt-1">
            <span className="text-[#ffe600]">▲ você ({carreira.idade}a)</span>
            <span className="text-[#00ff88]">| pico ({carreira.pico_carreira}a)</span>
          </div>
        </div>
      </div>

      <div className="border border-[#00ff88]/20 bg-[#111] p-3">
        <div className="flex justify-between arcade-font text-[8px] text-[#888] mb-2">
          <span>NÍVEL {carreira.nivel}</span>
          <span>{carreira.xp} / {carreira.xp_para_proximo} XP</span>
        </div>
        <div className="h-2 bg-[#222]">
          <div className="h-full bg-[#00ff88]" style={{ width: `${xpPct}%` }} />
        </div>
      </div>

      <div className="border-2 border-[#ffe600]/30 bg-[#111] p-3">
        <div className="arcade-font text-[9px] text-[#ffe600] mb-3">TÍTULOS ({sumario.Total})</div>
        <div className="grid grid-cols-3 gap-2 text-center mb-3">
          {[
            { label: 'TOTAL', count: sumario.Total, color: '#ffe600' },
            { label: 'SLAMS', count: sumario.GS, color: '#00ff88' },
            { label: 'MASTERS', count: sumario.M1000, color: '#00e5ff' },
          ].map((s) => (
            <div key={s.label} className="border border-[#222] py-2">
              <div className="pixel-font text-xl" style={{ color: s.color }}>{s.count}</div>
              <div className="arcade-font text-[7px] text-[#666] mt-1">{s.label}</div>
            </div>
          ))}
        </div>
        {(carreira.titulos || []).slice(-5).reverse().map((t, i) => (
          <div key={i} className="flex justify-between arcade-font text-[9px] py-1.5 border-t border-[#1a1a1a]">
            <div className="flex items-center gap-1 min-w-0">
              <Trophy size={10} className="text-[#ffe600] shrink-0" />
              <span className="text-white truncate">{t.torneio}</span>
            </div>
            <span className="text-[#555] shrink-0 ml-2">{t.ano}</span>
          </div>
        ))}
        {meusTitulos.length > 0 && (
          <button
            onClick={() => navigate('/history')}
            className="mt-3 w-full arcade-font text-[9px] text-[#ffe600] border border-[#ffe600]/20 py-2 hover:bg-[#ffe600]/5"
          >
            VER HISTÓRICO COMPLETO
          </button>
        )}
      </div>
    </div>
  )
}
