import { useNavigate } from 'react-router'
import type { RankingDetalhado } from '../../../types'

const FASE_LABEL: Record<string, string> = {
  campeao: 'CAMPEÃO', final: 'FINAL', semifinal: 'SEMIFINAL', semis: 'SEMIFINAL',
  quartas: 'QUARTAS', qf: 'QUARTAS', oitavas: 'OITAVAS', r16: 'OITAVAS',
  r32: 'R32', r64: 'R64', r128: 'R128', qualy_1: 'QUALY', qualy_2: 'QUALY',
}

function faseLabel(f: string) {
  return FASE_LABEL[f?.toLowerCase()] ?? f?.toUpperCase() ?? '?'
}

interface Props {
  rankingDet: RankingDetalhado
}

export function RankingTab({ rankingDet }: Props) {
  const navigate = useNavigate()

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div className="border-2 border-[#00ff88] bg-[#111] p-3 text-center">
          <div className="arcade-font text-[8px] text-[#888] mb-1">SIMPLES</div>
          <div className="pixel-font text-2xl text-[#00ff88]">
            {rankingDet.posicao_simples ? `#${rankingDet.posicao_simples}` : 'N/A'}
          </div>
          <div className="arcade-font text-[9px] text-[#666] mt-1">
            {rankingDet.pontos_simples.toLocaleString('pt-BR')} pts
          </div>
        </div>
        <div className="border-2 border-[#00e5ff] bg-[#111] p-3 text-center">
          <div className="arcade-font text-[8px] text-[#888] mb-1">DUPLAS</div>
          <div className="pixel-font text-2xl text-[#00e5ff]">
            {rankingDet.posicao_duplas ? `#${rankingDet.posicao_duplas}` : 'N/A'}
          </div>
          <div className="arcade-font text-[9px] text-[#666] mt-1">
            {rankingDet.pontos_duplas.toLocaleString('pt-BR')} pts
          </div>
        </div>
      </div>

      {rankingDet.pontos_ytd > 0 && (
        <div className="border border-[#ffe600]/40 bg-[#ffe600]/5 p-3 text-center">
          <div className="arcade-font text-[8px] text-[#888]">RACE TO FINALS (YTD)</div>
          <div className="pixel-font text-xl text-[#ffe600] mt-1">
            {rankingDet.pontos_ytd.toLocaleString('pt-BR')} pts
          </div>
        </div>
      )}

      {rankingDet.resultados_simples.length > 0 && (
        <div className="border border-[#333] bg-[#111]">
          <div className="border-b border-[#333] px-3 py-2 arcade-font text-[9px] text-[#00ff88]">
            RESULTADOS SIMPLES (BEST-18)
          </div>
          <div className="divide-y divide-[#1a1a1a]">
            {rankingDet.resultados_simples.map((r, i) => (
              <div key={i} className="flex items-center justify-between px-3 py-2">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="text-[8px] text-[#333] w-4 shrink-0">{i + 1}</span>
                  {r.obrigatorio && <span className="text-[#ffe600] text-[8px] shrink-0">●</span>}
                  <span className="arcade-font text-[9px] text-white truncate">{r.nome}</span>
                </div>
                <div className="flex items-center gap-3 shrink-0 ml-2">
                  <span className="arcade-font text-[8px] text-[#666]">{faseLabel(r.fase)}</span>
                  <span className="pixel-font text-[10px] text-[#00ff88] w-10 text-right">{r.pontos}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {rankingDet.resultados_duplas.length > 0 && (
        <div className="border border-[#333] bg-[#111]">
          <div className="border-b border-[#333] px-3 py-2 arcade-font text-[9px] text-[#00e5ff]">
            RESULTADOS DUPLAS
          </div>
          <div className="divide-y divide-[#1a1a1a]">
            {rankingDet.resultados_duplas.map((r, i) => (
              <div key={i} className="flex items-center justify-between px-3 py-2">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="text-[8px] text-[#333] w-4 shrink-0">{i + 1}</span>
                  <span className="arcade-font text-[9px] text-white truncate">{r.nome}</span>
                </div>
                <div className="flex items-center gap-3 shrink-0 ml-2">
                  <span className="arcade-font text-[8px] text-[#666]">{faseLabel(r.fase)}</span>
                  <span className="pixel-font text-[10px] text-[#00e5ff] w-10 text-right">{r.pontos}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="arcade-font text-[8px] text-[#333] text-center">
        ● = torneio obrigatório (Grand Slam / Masters 1000)
      </div>

      <button
        type="button"
        onClick={() => navigate('/ranking-historico')}
        className="w-full border border-[#00ff88]/30 bg-[#060f0a] py-2 arcade-font text-[9px] text-[#00ff88]/60 hover:text-[#00ff88] hover:border-[#00ff88]/60 transition-colors"
      >
        VER HISTÓRICO DE POSIÇÕES →
      </button>
    </div>
  )
}
