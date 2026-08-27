import { useEffect, useState } from 'react'
import { Trophy } from 'lucide-react'
import { api } from '../../../api/client'
import type { RaceToFinals } from '../../../types'

export function RaceTab() {
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<RaceToFinals | null>(null)
  const [erro, setErro] = useState(false)

  useEffect(() => {
    api.mundo
      .raceToFinals()
      .then(setData)
      .catch(() => setErro(true))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="py-16 text-center pixel-font text-xs text-neon-green animate-pulse">
        CARREGANDO...
      </div>
    )
  }

  if (erro) {
    return (
      <div className="py-16 text-center pixel-font text-[10px] text-neon-pink">
        Erro ao carregar feed
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
      <div className="border border-neon-yellow/30 bg-neon-yellow/5 p-3 flex items-center gap-3">
        <Trophy size={20} className="text-neon-yellow shrink-0" />
        <div>
          <div className="arcade-font text-[10px] text-neon-yellow">{data.tour} FINALS RACE</div>
          <div className="pixel-font text-[8px] text-[#888] mt-0.5">
            TOP 8 SE CLASSIFICAM · YTD POINTS
          </div>
        </div>
      </div>

      {data.posicao_jogador !== null && (
        <div
          className="border-2 p-3"
          style={{
            borderColor: data.posicao_jogador <= 8 ? 'var(--neon-green)' : '#888',
            backgroundColor: data.posicao_jogador <= 8 ? '#00ff8810' : 'transparent',
          }}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="pixel-font text-[8px] text-[#888]">SUA POSIÇÃO NA RACE</div>
              <div
                className="arcade-font text-xl mt-0.5"
                style={{ color: data.posicao_jogador <= 8 ? 'var(--neon-green)' : '#fff' }}
              >
                #{data.posicao_jogador}
              </div>
            </div>
            <div className="text-right">
              <div className="pixel-font text-[8px] text-[#888]">PONTOS YTD</div>
              <div className="arcade-font text-xl text-neon-cyan mt-0.5">
                {data.pontos_jogador.toLocaleString()}
              </div>
            </div>
          </div>
          {data.posicao_jogador <= 8 ? (
            <div className="mt-2 pixel-font text-[8px] text-neon-green">
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
                borderColor: entry.e_jogador ? 'var(--neon-green)' : entry.posicao <= 8 ? '#ffe60040' : '#ffffff15',
                backgroundColor: entry.e_jogador ? '#00ff8808' : 'transparent',
              }}
            >
              <div
                className="arcade-font text-[11px] w-6 text-center shrink-0"
                style={{
                  color: entry.posicao === 1 ? 'var(--neon-yellow)' : entry.posicao <= 4 ? 'var(--neon-green)' : '#888',
                }}
              >
                {entry.posicao}
              </div>
              <div className="flex-1 min-w-0">
                <div
                  className="arcade-font text-[9px] truncate"
                  style={{ color: entry.e_jogador ? 'var(--neon-green)' : '#fff' }}
                >
                  {entry.nome}
                  {entry.e_jogador && (
                    <span className="text-[7px] text-neon-green ml-1">◄ VOCÊ</span>
                  )}
                </div>
                <div className="pixel-font text-[7px] text-[#888] mt-0.5">
                  {entry.nacionalidade}
                </div>
              </div>
              <div
                className="arcade-font text-[10px] shrink-0"
                style={{ color: entry.e_jogador ? 'var(--neon-green)' : 'var(--neon-cyan)' }}
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
