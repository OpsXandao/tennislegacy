import { useEffect, useState } from 'react'
import { Trophy } from 'lucide-react'
import { api } from '../../../api/client'
import type { RaceToFinals } from '../../../types'

export function RaceTab() {
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<RaceToFinals | null>(null)

  useEffect(() => {
    api.mundo
      .raceToFinals()
      .then(setData)
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

  if (!data) {
    return (
      <div className="py-16 text-center pixel-font text-[10px] text-[#666]">
        DADOS INDISPONÍVEIS
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="border border-[#ffe600]/30 bg-[#ffe600]/5 p-3 flex items-center gap-3">
        <Trophy size={20} className="text-[#ffe600] shrink-0" />
        <div>
          <div className="arcade-font text-[10px] text-[#ffe600]">{data.tour} FINALS RACE</div>
          <div className="pixel-font text-[8px] text-[#888] mt-0.5">
            TOP 8 SE CLASSIFICAM · YTD POINTS
          </div>
        </div>
      </div>

      {data.posicao_jogador !== null && (
        <div
          className="border-2 p-3"
          style={{
            borderColor: data.posicao_jogador <= 8 ? '#00ff88' : '#888',
            backgroundColor: data.posicao_jogador <= 8 ? '#00ff8810' : 'transparent',
          }}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="pixel-font text-[8px] text-[#888]">SUA POSIÇÃO NA RACE</div>
              <div
                className="arcade-font text-xl mt-0.5"
                style={{ color: data.posicao_jogador <= 8 ? '#00ff88' : '#fff' }}
              >
                #{data.posicao_jogador}
              </div>
            </div>
            <div className="text-right">
              <div className="pixel-font text-[8px] text-[#888]">PONTOS YTD</div>
              <div className="arcade-font text-xl text-[#00e5ff] mt-0.5">
                {data.pontos_jogador.toLocaleString()}
              </div>
            </div>
          </div>
          {data.posicao_jogador <= 8 ? (
            <div className="mt-2 pixel-font text-[8px] text-[#00ff88]">
              ✓ CLASSIFICADO PARA AS FINALS
            </div>
          ) : data.faltam_para_classificar > 0 ? (
            <div className="mt-2 pixel-font text-[8px] text-[#888]">
              FALTAM {data.faltam_para_classificar.toLocaleString()} PTS PARA CLASSIFICAR
            </div>
          ) : null}
        </div>
      )}

      <div>
        <div className="pixel-font text-[8px] text-[#888] mb-2">TOP 8 YTD</div>
        <div className="space-y-1">
          {data.top8.map((entry) => (
            <div
              key={entry.nome}
              className="flex items-center gap-3 border p-2.5 transition-colors"
              style={{
                borderColor: entry.e_jogador ? '#00ff88' : entry.posicao <= 8 ? '#ffe60040' : '#ffffff15',
                backgroundColor: entry.e_jogador ? '#00ff8808' : 'transparent',
              }}
            >
              <div
                className="arcade-font text-[11px] w-6 text-center shrink-0"
                style={{
                  color: entry.posicao === 1 ? '#ffe600' : entry.posicao <= 4 ? '#00ff88' : '#888',
                }}
              >
                {entry.posicao}
              </div>
              <div className="flex-1 min-w-0">
                <div
                  className="arcade-font text-[9px] truncate"
                  style={{ color: entry.e_jogador ? '#00ff88' : '#fff' }}
                >
                  {entry.nome}
                  {entry.e_jogador && (
                    <span className="text-[7px] text-[#00ff88] ml-1">◄ VOCÊ</span>
                  )}
                </div>
                <div className="pixel-font text-[7px] text-[#888] mt-0.5">
                  {entry.nacionalidade}
                </div>
              </div>
              <div
                className="arcade-font text-[10px] shrink-0"
                style={{ color: entry.e_jogador ? '#00ff88' : '#00e5ff' }}
              >
                {entry.pontos_ytd.toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
