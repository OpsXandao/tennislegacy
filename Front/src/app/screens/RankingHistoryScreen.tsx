import { useEffect, useRef, useState } from 'react'
import { TrendingUp } from 'lucide-react'
import { PageHeader } from '../components'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'

type Semana = { semana: number; ano: number; posicao: number; pontos: number }

const ACCENT = '#00ff88'
const W = 600
const H = 200
const PAD = { top: 16, right: 16, bottom: 28, left: 48 }

function Chart({ dados }: { dados: Semana[] }) {
  const svgRef = useRef<SVGSVGElement>(null)
  const [tooltip, setTooltip] = useState<{ x: number; y: number; s: Semana } | null>(null)

  if (dados.length < 2) {
    return (
      <div className="flex items-center justify-center h-[200px] text-[10px] text-[#00ff88]/40"
           style={{ fontFamily: 'var(--font-arcade)' }}>
        DADOS INSUFICIENTES
      </div>
    )
  }

  const innerW = W - PAD.left - PAD.right
  const innerH = H - PAD.top - PAD.bottom

  const maxPos = Math.max(...dados.map((d) => d.posicao))
  const minPos = Math.min(...dados.map((d) => d.posicao))
  const range = maxPos - minPos || 1

  const xs = dados.map((_, i) => PAD.left + (i / (dados.length - 1)) * innerW)
  // Posição invertida: rank 1 fica no topo (y pequeno), rank alto fica em baixo
  const ys = dados.map((d) => PAD.top + ((d.posicao - minPos) / range) * innerH)

  const polyline = xs.map((x, i) => `${x},${ys[i]}`).join(' ')
  const area = [
    `${xs[0]},${PAD.top + innerH}`,
    ...xs.map((x, i) => `${x},${ys[i]}`),
    `${xs[xs.length - 1]},${PAD.top + innerH}`,
  ].join(' ')

  // Ticks eixo Y (4 labels)
  const yTicks = [0, 0.33, 0.66, 1].map((t) => ({
    y: PAD.top + t * innerH,
    label: Math.round(minPos + t * range),
  }))
  // Ticks eixo X (até 6 labels)
  const step = Math.max(1, Math.floor(dados.length / 6))
  const xTicks = dados
    .map((d, i) => ({ i, d }))
    .filter(({ i }) => i % step === 0 || i === dados.length - 1)

  return (
    <div className="relative select-none">
      <svg
        ref={svgRef}
        viewBox={`0 0 ${W} ${H}`}
        className="w-full"
        style={{ maxHeight: 200 }}
        onMouseLeave={() => setTooltip(null)}
      >
        {/* Grid lines */}
        {yTicks.map((t) => (
          <line
            key={t.y}
            x1={PAD.left} y1={t.y}
            x2={W - PAD.right} y2={t.y}
            stroke="#ffffff08"
            strokeWidth="1"
          />
        ))}

        {/* Area fill */}
        <polygon points={area} fill={`${ACCENT}12`} />

        {/* Line */}
        <polyline
          points={polyline}
          fill="none"
          stroke={ACCENT}
          strokeWidth="1.5"
          strokeLinejoin="round"
          style={{ filter: `drop-shadow(0 0 3px ${ACCENT})` }}
        />

        {/* Y axis labels */}
        {yTicks.map((t) => (
          <text
            key={t.y}
            x={PAD.left - 6} y={t.y + 4}
            textAnchor="end"
            fill="#00ff8866"
            fontSize="9"
            fontFamily="var(--font-mono)"
          >
            #{t.label}
          </text>
        ))}

        {/* X axis labels */}
        {xTicks.map(({ i, d }) => (
          <text
            key={i}
            x={xs[i]} y={H - 4}
            textAnchor="middle"
            fill="#00ff8844"
            fontSize="8"
            fontFamily="var(--font-mono)"
          >
            {d.semana}
          </text>
        ))}

        {/* Dots (hover targets) */}
        {dados.map((d, i) => (
          <circle
            key={i}
            cx={xs[i]} cy={ys[i]}
            r="4"
            fill="transparent"
            onMouseEnter={() => setTooltip({ x: xs[i], y: ys[i], s: d })}
          />
        ))}

        {/* Active dot */}
        {tooltip && (
          <circle
            cx={tooltip.x} cy={tooltip.y}
            r="4"
            fill={ACCENT}
            style={{ filter: `drop-shadow(0 0 4px ${ACCENT})` }}
          />
        )}
      </svg>

      {/* Tooltip */}
      {tooltip && (
        <div
          className="absolute pointer-events-none border border-[#00ff88] bg-[#060f0a] px-2 py-1 text-[9px] text-[#00ff88]"
          style={{
            fontFamily: 'var(--font-arcade)',
            left: `${(tooltip.x / W) * 100}%`,
            top: `${(tooltip.y / H) * 100}%`,
            transform: 'translate(-50%, -120%)',
            whiteSpace: 'nowrap',
          }}
        >
          S{tooltip.s.semana} — #{tooltip.s.posicao} — {tooltip.s.pontos}pts
        </div>
      )}
    </div>
  )
}

export function RankingHistoryScreen() {
  const { jogador } = useGameStore()
  const [dados, setDados] = useState<Semana[]>([])
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState<string | null>(null)

  useEffect(() => {
    api.jogador
      .rankingHistorico()
      .then((r) => setDados(r.semanas ?? []))
      .catch((e) => setErro(e.message ?? 'Erro ao carregar histórico.'))
      .finally(() => setLoading(false))
  }, [])

  const melhor = dados.length ? Math.min(...dados.map((d) => d.posicao)) : null
  const atual = dados.length ? dados[dados.length - 1].posicao : jogador?.ranking ?? null

  return (
    <div className="app-shell min-h-screen font-mono pb-24">
      <PageHeader title="HISTÓRICO DE RANKING" color="green" backTo="/player">
        <p
          className="text-[9px] text-[#00ff88]/60 mt-1"
          style={{ fontFamily: 'var(--font-mono)' }}
        >
          PROGRESSÃO DE CARREIRA
        </p>
      </PageHeader>

      <div className="p-4 space-y-4">
        {/* Stats summary */}
        <div className="grid grid-cols-3 gap-3">
          {[
            { label: 'ATUAL', value: atual != null ? `#${atual}` : '—' },
            { label: 'MELHOR', value: melhor != null ? `#${melhor}` : '—' },
            { label: 'SEMANAS', value: dados.length },
          ].map(({ label, value }) => (
            <div
              key={label}
              className="border border-[#00ff88]/20 bg-[#060f0a] p-3 text-center"
            >
              <div
                className="text-[8px] text-[#00ff88]/50 mb-1"
                style={{ fontFamily: 'var(--font-arcade)' }}
              >
                {label}
              </div>
              <div
                className="text-lg text-[#00ff88]"
                style={{
                  fontFamily: 'var(--font-mono)',
                  textShadow: '0 0 8px #00ff8877',
                }}
              >
                {value}
              </div>
            </div>
          ))}
        </div>

        {/* Chart */}
        <div className="border border-[#00ff88]/20 bg-[#060f0a] p-3">
          <div
            className="text-[9px] text-[#00ff88]/60 mb-3 flex items-center gap-2"
            style={{ fontFamily: 'var(--font-arcade)' }}
          >
            <TrendingUp size={11} className="text-[#00ff88]" />
            POSIÇÃO POR SEMANA (eixo Y invertido: 1 = topo)
          </div>

          {loading && (
            <div
              className="text-center py-12 text-[10px] text-[#00ff88]/40"
              style={{ fontFamily: 'var(--font-arcade)' }}
            >
              CARREGANDO...
            </div>
          )}

          {erro && (
            <div
              className="text-center py-8 text-[10px] text-[#ff0055]"
              style={{ fontFamily: 'var(--font-arcade)' }}
            >
              {erro}
            </div>
          )}

          {!loading && !erro && <Chart dados={dados} />}
        </div>

        {/* Table */}
        {!loading && !erro && dados.length > 0 && (
          <div className="border border-[#00ff88]/20 bg-[#060f0a]">
            <div className="grid grid-cols-4 px-3 py-2 text-[8px] text-[#00ff88]/40 border-b border-[#00ff88]/10"
                 style={{ fontFamily: 'var(--font-arcade)' }}>
              <span>ANO</span>
              <span>SEMANA</span>
              <span className="text-right">POSIÇÃO</span>
              <span className="text-right">PONTOS</span>
            </div>
            <div className="max-h-64 overflow-y-auto">
              {[...dados].reverse().map((d, i) => (
                <div
                  key={i}
                  className="grid grid-cols-4 px-3 py-2 text-[10px] border-b border-[#ffffff05]"
                  style={{
                    fontFamily: 'var(--font-mono)',
                    color: d.posicao === melhor ? ACCENT : '#aaa',
                    textShadow: d.posicao === melhor ? `0 0 6px ${ACCENT}` : 'none',
                  }}
                >
                  <span>{d.ano}</span>
                  <span>{d.semana}</span>
                  <span className="text-right">#{d.posicao}</span>
                  <span className="text-right">{d.pontos}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
