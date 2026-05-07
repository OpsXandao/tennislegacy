import { useEffect, useState } from 'react'
import { api } from '../../../api/client'

export function FormaTab() {
  const [forma, setForma] = useState<('V' | 'D')[]>([])
  const [partidas, setPartidas] = useState<{
    adversario: string
    resultado: string | null
    torneio: string | null
    semana: number | null
    ano: number | null
    venceu: boolean
  }[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.jogador
      .formaRecente()
      .then((r) => {
        setForma(r.forma)
        setPartidas(r.partidas)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="text-center py-12 arcade-font text-[10px] text-[#444]">CARREGANDO...</div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 justify-center py-4">
        {forma.length === 0 ? (
          <span className="arcade-font text-[10px] text-[#444]">SEM PARTIDAS RECENTES</span>
        ) : (
          forma.map((r, i) => (
            <div
              key={i}
              className="w-10 h-10 flex items-center justify-center border-2 arcade-font text-[11px]"
              style={{
                borderColor: r === 'V' ? '#00ff88' : '#ff0055',
                color: r === 'V' ? '#00ff88' : '#ff0055',
                background: r === 'V' ? '#00ff8815' : '#ff005515',
                boxShadow: r === 'V' ? '0 0 8px #00ff8844' : '0 0 8px #ff005544',
              }}
            >
              {r}
            </div>
          ))
        )}
      </div>

      {partidas.length > 0 && (
        <div className="border border-[#333] bg-[#111]">
          <div className="border-b border-[#333] px-3 py-2 arcade-font text-[9px] text-[#888]">
            ÚLTIMAS PARTIDAS
          </div>
          {partidas.map((p, i) => (
            <div
              key={i}
              className={`flex items-center justify-between px-3 py-3 border-b border-[#1a1a1a] border-l-4 ${
                p.venceu ? 'border-l-[#00ff88]' : 'border-l-[#ff0055]'
              }`}
            >
              <div className="min-w-0">
                <div className="arcade-font text-[10px] text-white truncate max-w-[200px]">
                  {p.adversario}
                </div>
                <div className="arcade-font text-[8px] text-[#555] mt-0.5">
                  {p.torneio ?? ''} {p.semana ? `S${p.semana}` : ''}
                </div>
              </div>
              <div
                className="pixel-font text-[11px] font-bold shrink-0 ml-2"
                style={{ color: p.venceu ? '#00ff88' : '#ff0055' }}
              >
                {p.resultado ?? (p.venceu ? 'V' : 'D')}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
