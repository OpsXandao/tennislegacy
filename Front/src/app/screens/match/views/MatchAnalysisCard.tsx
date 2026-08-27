import { useNavigate } from 'react-router'
import { CircularGauge } from '../components'
import { alpha, formatarNacionalidade } from '../uiUtils'

interface MatchAnalysisItem { texto?: string; categoria?: string }

function renderText(value: string | MatchAnalysisItem): string {
  return typeof value === 'string' ? value : value?.texto ?? String(value ?? '')
}

interface MatchAnalysisCardProps {
  title: string
  accentColor: string
  nome: string
  nacionalidade?: string | null
  ranking: number | null
  overall: number
  infoExtra?: string
  leitura: string
  aba: 'registros' | 'historia'
  setAba: (aba: 'registros' | 'historia') => void
  historico: Array<string | MatchAnalysisItem>
  titulos: Array<string | MatchAnalysisItem>
  historicoTextColor: string
  energia: number
  fadiga: number
  dossieRoute?: string
  children: React.ReactNode
}

export function MatchAnalysisCard({
  title,
  accentColor,
  nome,
  nacionalidade,
  ranking,
  overall,
  infoExtra,
  leitura,
  aba,
  setAba,
  historico,
  titulos,
  historicoTextColor,
  energia,
  fadiga,
  dossieRoute,
  children,
}: MatchAnalysisCardProps) {
  const navigate = useNavigate()

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 mb-1">
        <div className="w-1 h-4" style={{ background: accentColor }} />
        <span className="arcade-font text-[12px] tracking-widest" style={{ color: accentColor }}>
          {title}
        </span>
      </div>

      <div
        className="app-panel match-card border-2 p-4 relative overflow-hidden"
        style={{ borderColor: alpha(accentColor, '66') }}
      >
        <div className="absolute top-0 right-0 p-2 opacity-5">
          <div className="text-6xl">🎾</div>
        </div>

        <div className="flex justify-between items-start mb-4">
          <div>
            <div className="arcade-font text-xl text-white mb-1">{nome}</div>
            {nacionalidade && (
              <div className="arcade-font text-[10px] mb-1" style={{ color: alpha(accentColor, 'cc') }}>
                {formatarNacionalidade(nacionalidade)}
              </div>
            )}
            <div className="arcade-font text-[11px] text-[#888]">
              {infoExtra ?? (ranking ? `#${ranking} MUNDIAL` : 'SEM RANKING')}
            </div>
          </div>
          <div className="text-right">
            <div className="arcade-font text-[10px]" style={{ color: accentColor }}>
              OVR {overall}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-[0.9fr_1.1fr] gap-3 mb-4">
          <div
            className="match-card-soft p-3 border"
            style={{ background: alpha(accentColor, '0d'), borderColor: alpha(accentColor, '33') }}
          >
            <div
              className="arcade-font text-[10px] tracking-widest mb-1 uppercase"
              style={{ color: alpha(accentColor, 'cc') }}
            >
              Leitura
            </div>
            <div className="arcade-font text-[12px] text-white leading-relaxed">{leitura}</div>
          </div>

          <div
            className="match-card-soft p-3 border"
            style={{ background: alpha(accentColor, '0d'), borderColor: alpha(accentColor, '33') }}
          >
            <div className="mb-2 flex items-center justify-between gap-2">
              <div
                className="arcade-font text-[10px] tracking-widest uppercase"
                style={{ color: alpha(accentColor, 'cc') }}
              >
                {aba === 'registros' ? 'Últimos Registros' : 'História'}
              </div>
              <div className="flex gap-1">
                <button
                  onClick={() => setAba('registros')}
                  className="border px-2 py-1 arcade-font text-[8px]"
                  style={{
                    borderColor: aba === 'registros' ? accentColor : alpha(accentColor, '55'),
                    color: aba === 'registros' ? '#050505' : historicoTextColor,
                    background: aba === 'registros' ? accentColor : 'transparent',
                  }}
                >
                  REGISTROS
                </button>
                <button
                  onClick={() => setAba('historia')}
                  className="border px-2 py-1 arcade-font text-[8px]"
                  style={{
                    borderColor: aba === 'historia' ? 'var(--neon-yellow)' : '#6c5f2b',
                    color: aba === 'historia' ? '#1b1803' : '#ffe27a',
                    background: aba === 'historia' ? 'var(--neon-yellow)' : 'transparent',
                  }}
                >
                  TÍTULOS
                </button>
              </div>
            </div>

            {aba === 'registros' ? (
              historico.length > 0 ? (
                <div className="space-y-1.5">
                  {historico.map((item, idx) => {
                    const texto = renderText(item)
                    return (
                      <div key={idx} className="arcade-font text-[10px] leading-relaxed" style={{ color: historicoTextColor }}>
                        {texto}
                      </div>
                    )
                  })}
                </div>
              ) : (
                <div className="arcade-font text-[10px] leading-relaxed" style={{ color: alpha(accentColor, 'aa') }}>
                  Sem histórico recente salvo.
                </div>
              )
            ) : titulos.length > 0 ? (
              <div className="space-y-1.5">
                {titulos.map((item, idx) => {
                  const texto = renderText(item)
                  return (
                    <div key={idx} className="arcade-font text-[10px] text-[#fff0a6] leading-relaxed">
                      {texto}
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="arcade-font text-[10px] text-[#c9bc7c] leading-relaxed">
                Nenhum título registrado.
              </div>
            )}

            {dossieRoute && (
              <button
                onClick={() => navigate(dossieRoute)}
                className="mt-3 arcade-font text-[9px] uppercase underline underline-offset-4"
                style={{ color: accentColor }}
              >
                Ver dossiê completo
              </button>
            )}
          </div>
        </div>

        <div className="flex items-center justify-end gap-6 mb-4">
          <CircularGauge label="ENERGIA" value={energia} color={accentColor} />
          <CircularGauge label="FADIGA" value={fadiga} color="var(--neon-yellow)" track="#26131b" />
        </div>

        {children}
      </div>
    </div>
  )
}
