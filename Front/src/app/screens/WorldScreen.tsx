import { useEffect, useState } from 'react'
import { Globe, CalendarDays, X, Trophy, Users, ChevronRight } from 'lucide-react'
import { motion, AnimatePresence } from 'motion/react'
import { api } from '../../api/client'
import { PageHeader, PixelFlag } from '../components'
import type { MundoTorneio, TorneioAoVivo, RaceToFinals } from '../../types'
import worldMapPixel from '../../assets/maps/world-map-pixel.png'

// ── Bracket modal ─────────────────────────────────────────────────────────────

interface BracketData {
  nome: string
  tipo: string
  fase_atual: string
  campeao_simples: string | null
  campeao_duplas: string | null
  rodadas: Record<string, Array<{ j1: string; j2: string }>>
  resultados: Record<string, Array<{ j1: string; j2: string; vencedor: string; placar: string }>>
  rodadas_duplas: Record<string, Array<{ j1: string; j2: string }>>
  resultados_duplas: Record<string, Array<{ j1: string; j2: string; vencedor: string; placar: string }>>
}

function BracketModal({
  torneio,
  tour,
  onClose,
}: {
  torneio: string
  tour: 'atp' | 'wta'
  onClose: () => void
}) {
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<BracketData | null>(null)
  const [tab, setTab] = useState<'simples' | 'duplas'>('simples')

  useEffect(() => {
    api.mundo
      .bracket(torneio, tour)
      .then((d) => setData(d as BracketData))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [torneio, tour])

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[200] bg-black/95 flex flex-col"
      >
        {/* header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <div>
            <div className="arcade-font text-[11px] text-[#ffe600]">{torneio.toUpperCase()}</div>
            <div className="pixel-font text-[8px] text-[#888] mt-0.5">
              {tour.toUpperCase()} · {data?.tipo || ''}
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 border border-white/20 text-white active:bg-white/10"
          >
            <X size={18} />
          </button>
        </div>

        {loading ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="pixel-font text-[#00ff88] text-xs animate-pulse">CARREGANDO...</div>
          </div>
        ) : !data ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="pixel-font text-[#888] text-xs">TORNEIO NÃO INICIADO</div>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {/* campeão */}
            {data.campeao_simples && (
              <div className="border-2 border-[#ffe600] bg-[#ffe600]/10 p-3 flex items-center gap-3">
                <Trophy size={18} className="text-[#ffe600] shrink-0" />
                <div>
                  <div className="pixel-font text-[8px] text-[#888]">CAMPEÃO SIMPLES</div>
                  <div className="arcade-font text-[11px] text-[#ffe600]">
                    {data.campeao_simples.toUpperCase()}
                  </div>
                </div>
              </div>
            )}
            {data.campeao_duplas && (
              <div className="border-2 border-[#00e5ff] bg-[#00e5ff]/10 p-3 flex items-center gap-3">
                <Users size={18} className="text-[#00e5ff] shrink-0" />
                <div>
                  <div className="pixel-font text-[8px] text-[#888]">CAMPEÃO DUPLAS</div>
                  <div className="arcade-font text-[11px] text-[#00e5ff]">
                    {data.campeao_duplas.toUpperCase()}
                  </div>
                </div>
              </div>
            )}

            {/* fase atual */}
            <div className="flex items-center gap-2">
              <div className="pixel-font text-[8px] text-[#888]">FASE ATUAL:</div>
              <div className="arcade-font text-[9px] text-[#00ff88]">
                {data.fase_atual.toUpperCase()}
              </div>
            </div>

            {/* tabs simples / duplas */}
            <div className="flex gap-2">
              {(['simples', 'duplas'] as const).map((t) => (
                <button
                  key={t}
                  onClick={() => setTab(t)}
                  className={`flex-1 py-2 arcade-font text-[9px] border-2 transition-colors ${
                    tab === t
                      ? 'bg-[#00ff88] text-black border-[#00ff88]'
                      : 'border-white/20 text-white'
                  }`}
                >
                  {t.toUpperCase()}
                </button>
              ))}
            </div>

            {/* resultados */}
            {(() => {
              const resultados =
                tab === 'simples' ? data.resultados : data.resultados_duplas
              const rodadas = tab === 'simples' ? data.rodadas : data.rodadas_duplas
              const fases = [
                ...Object.keys(resultados),
                ...Object.keys(rodadas).filter((f) => !(f in resultados)),
              ]

              if (fases.length === 0) {
                return (
                  <div className="text-center py-8 pixel-font text-[8px] text-[#666]">
                    SEM DADOS DISPONÍVEIS
                  </div>
                )
              }

              return (
                <div className="space-y-4">
                  {fases.map((fase) => {
                    const res = resultados[fase] || []
                    const conf = rodadas[fase] || []
                    return (
                      <div key={fase}>
                        <div className="pixel-font text-[8px] text-[#ffe600] mb-2">
                          {fase.toUpperCase()}
                        </div>
                        <div className="space-y-1">
                          {res.map((r, i) => (
                            <div
                              key={i}
                              className="border border-white/10 bg-black/40 p-2 text-[8px]"
                            >
                              <span
                                className={
                                  r.vencedor === r.j1 ? 'text-[#00ff88]' : 'text-white/50'
                                }
                              >
                                {r.j1}
                              </span>
                              <span className="text-[#888] mx-1">vs</span>
                              <span
                                className={
                                  r.vencedor === r.j2 ? 'text-[#00ff88]' : 'text-white/50'
                                }
                              >
                                {r.j2}
                              </span>
                              {r.placar && (
                                <span className="text-[#ffe600] ml-2">{r.placar}</span>
                              )}
                            </div>
                          ))}
                          {conf
                            .filter((c) => !res.some((r) => r.j1 === c.j1 && r.j2 === c.j2))
                            .map((c, i) => (
                              <div
                                key={`p-${i}`}
                                className="border border-white/5 bg-black/20 p-2 text-[8px] text-white/40"
                              >
                                {c.j1} vs {c.j2}
                              </div>
                            ))}
                        </div>
                      </div>
                    )
                  })}
                </div>
              )
            })()}
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  )
}

// ── Tournament detail modal (calendar tab) ────────────────────────────────────

function TournamentDetailModal({
  nome,
  tour,
  onClose,
}: {
  nome: string
  tour: string
  onClose: () => void
}) {
  const [loading, setLoading] = useState(true)
  const [estado, setEstado] = useState<any>(null)

  useEffect(() => {
    api.mundo
      .torneio(nome, tour)
      .then(setEstado)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [nome, tour])

  if (loading) {
    return (
      <div className="fixed inset-0 z-[100] bg-black/90 flex items-center justify-center p-6">
        <div className="pixel-font text-[#00ff88] text-xs animate-pulse">CARREGANDO...</div>
      </div>
    )
  }

  if (!estado) return null

  const data = estado.tournament_data || {}

  return (
    <div className="fixed inset-0 z-[100] bg-black/95 flex flex-col p-4 overflow-y-auto">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          {data.codigo_pais && <PixelFlag countryCode={data.codigo_pais} size="md" />}
          <div className="arcade-font text-xs text-[#ffe600]">{nome.toUpperCase()}</div>
        </div>
        <button
          onClick={onClose}
          className="p-2 border-2 border-white/20 text-white active:bg-white/10"
        >
          <X size={20} />
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-4">
        {[
          { label: 'LOCAL', value: `${data.local || '-'}, ${data.pais_sede || '-'}` },
          { label: 'CATEGORIA', value: data.tipo || '-' },
          { label: 'SUPERFÍCIE', value: data.quadra || '-', color: '#00ff88' },
          { label: 'PRÊMIO', value: data.premiacao ? `$${Number(data.premiacao).toLocaleString()}` : '-', color: '#ffe600' },
        ].map(({ label, value, color }) => (
          <div key={label} className="border border-white/10 bg-black/40 p-3">
            <div className="pixel-font text-[7px] text-[#888]">{label}</div>
            <div
              className="arcade-font text-[9px] mt-1"
              style={{ color: color || '#fff' }}
            >
              {String(value).toUpperCase()}
            </div>
          </div>
        ))}
      </div>

      <div className="space-y-2">
        {[
          { icon: Trophy, label: 'CAMPEÃO SIMPLES', value: estado.campeao_simples || data.ultimo_campeao || '---', color: '#ffe600' },
          { icon: Users, label: 'CAMPEÃO DUPLAS', value: estado.campeao_duplas || data.ultimo_campeao_duplas || '---', color: '#00e5ff' },
        ].map(({ icon: Icon, label, value, color }) => (
          <div key={label} className="flex items-center justify-between border border-white/10 bg-black/40 p-3">
            <div className="flex items-center gap-2">
              <Icon size={14} style={{ color }} />
              <div className="pixel-font text-[8px] text-[#888]">{label}</div>
            </div>
            <div className="arcade-font text-[9px]" style={{ color }}>
              {String(value).toUpperCase()}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ── AO VIVO tab ───────────────────────────────────────────────────────────────

function AoVivoTab() {
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
      <div className="py-16 text-center pixel-font text-xs text-[#00ff88] animate-pulse">
        CARREGANDO...
      </div>
    )
  }

  const atp = torneios.filter((t) => t.tour === 'ATP')
  const wta = torneios.filter((t) => t.tour === 'WTA')

  function TourSection({ label, list, color }: { label: string; list: TorneioAoVivo[]; color: string }) {
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
              onClick={() =>
                setSelected({ nome: t.nome, tour: t.tour === 'ATP' ? 'atp' : 'wta' })
              }
              className="w-full border-2 border-white/10 bg-[#1a1a2e] p-3 text-left active:scale-[0.98] transition-transform"
              style={{
                borderColor: t.finalizado ? '#ffe600' : color + '40',
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
                    <div className="border border-[#ffe600] px-1.5 py-0.5 pixel-font text-[7px] text-[#ffe600]">
                      FIM
                    </div>
                  ) : (
                    <div className="border border-[#00ff88] px-1.5 py-0.5 pixel-font text-[7px] text-[#00ff88] animate-pulse">
                      AO VIVO
                    </div>
                  )}
                  <ChevronRight size={12} className="text-[#888]" />
                </div>
              </div>

              {t.campeao_simples ? (
                <div className="mt-2 flex items-center gap-1.5">
                  <Trophy size={10} className="text-[#ffe600]" />
                  <span className="pixel-font text-[8px] text-[#ffe600]">
                    {t.campeao_simples.toUpperCase()}
                  </span>
                </div>
              ) : (
                <div className="mt-2 pixel-font text-[8px] text-[#888]">
                  FASE: {t.fase_atual}
                </div>
              )}
            </motion.button>
          ))}
        </div>
      </div>
    )
  }

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
          <TourSection label="ATP" list={atp} color="#00e5ff" />
          <TourSection label="WTA" list={wta} color="#ff6eb4" />
        </div>
      )}
    </>
  )
}

// ── RACE TO FINALS tab ────────────────────────────────────────────────────────

function RaceTab() {
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
      {/* header info */}
      <div className="border border-[#ffe600]/30 bg-[#ffe600]/5 p-3 flex items-center gap-3">
        <Trophy size={20} className="text-[#ffe600] shrink-0" />
        <div>
          <div className="arcade-font text-[10px] text-[#ffe600]">
            {data.tour} FINALS RACE
          </div>
          <div className="pixel-font text-[8px] text-[#888] mt-0.5">
            TOP 8 SE CLASSIFICAM · YTD POINTS
          </div>
        </div>
      </div>

      {/* player status */}
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

      {/* top 8 */}
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
                  color:
                    entry.posicao === 1
                      ? '#ffe600'
                      : entry.posicao <= 4
                      ? '#00ff88'
                      : '#888',
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

// ── PRÓXIMOS tab ──────────────────────────────────────────────────────────────

function ProximosTab() {
  const [loading, setLoading] = useState(true)
  const [semanaAtual, setSemanaAtual] = useState(1)
  const [torneios, setTorneios] = useState<MundoTorneio[]>([])
  const [noticias, setNoticias] = useState<string[]>([])
  const [selected, setSelected] = useState<{ nome: string; tour: string } | null>(null)

  useEffect(() => {
    Promise.all([api.mundo.proximos(), api.mundo.noticias()])
      .then(([res, news]) => {
        setSemanaAtual(res.semana_atual)
        setTorneios(res.torneios)
        setNoticias(news.noticias || [])
      })
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

  return (
    <>
      {selected && (
        <TournamentDetailModal
          nome={selected.nome}
          tour={selected.tour}
          onClose={() => setSelected(null)}
        />
      )}

      <div className="space-y-5">
        {/* world map */}
        <div className="overflow-hidden border-2 border-[#00e5ff]/40 bg-[#0b1020]">
          <img
            src={worldMapPixel}
            alt="Mapa mundi"
            className="h-auto w-full opacity-90"
            style={{ imageRendering: 'pixelated' }}
          />
        </div>

        {/* tournament list */}
        <div>
          <div className="pixel-font text-[8px] text-[#888] mb-2">
            PRÓXIMAS 4 SEMANAS · SEMANA ATUAL {semanaAtual}
          </div>
          <div className="space-y-2">
            {torneios.map((t, i) => (
              <motion.div
                key={`${t.semana}-${t.nome}`}
                initial={{ opacity: 0, x: -16 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.03 }}
                onClick={() =>
                  setSelected({
                    nome: t.nome,
                    tour: String(t.tipo || '').toUpperCase().includes('WTA') ? 'wta' : 'atp',
                  })
                }
                className="border-2 border-[#00e5ff]/30 bg-[#1a1a2e] p-3 cursor-pointer active:scale-[0.98] transition-transform"
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <div className="arcade-font text-[10px] text-[#00e5ff]">{t.nome}</div>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      {t.codigo_pais && <PixelFlag countryCode={t.codigo_pais} size="sm" />}
                      <div className="pixel-font text-[7px] text-[#888]">
                        {t.local}, {t.pais}
                      </div>
                    </div>
                  </div>
                  <div
                    className={`border px-2 py-1 pixel-font text-[7px] shrink-0 ${
                      t.semana === semanaAtual
                        ? 'border-[#ffe600] text-[#ffe600]'
                        : 'border-[#00ff88] text-[#00ff88]'
                    }`}
                  >
                    {t.semana === semanaAtual ? 'AGORA' : `SEM ${t.semana}`}
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { label: 'TIPO', value: t.tipo, color: '#fff' },
                    { label: 'SUPERFÍCIE', value: t.superficie, color: '#00ff88' },
                    { label: 'PRÊMIO', value: t.premiacao || '-', color: '#ffe600' },
                  ].map(({ label, value, color }) => (
                    <div key={label}>
                      <div className="pixel-font text-[7px] text-[#666]">{label}</div>
                      <div
                        className="pixel-font text-[8px] uppercase mt-0.5"
                        style={{ color }}
                      >
                        {value}
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            ))}
            {torneios.length === 0 && (
              <div className="border border-[#333] p-6 text-center pixel-font text-[10px] text-[#666]">
                NENHUM TORNEIO ENCONTRADO
              </div>
            )}
          </div>
        </div>

        {/* news */}
        {noticias.length > 0 && (
          <div>
            <div className="pixel-font text-[8px] text-[#888] mb-2">NOTÍCIAS DO CIRCUITO</div>
            <div className="space-y-2">
              {noticias.map((n, i) => (
                <div
                  key={i}
                  className="border border-[#00ff88]/20 bg-black/30 p-3 pixel-font text-[8px] text-[#ddd]"
                >
                  {n}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </>
  )
}

// ── Main ──────────────────────────────────────────────────────────────────────

const TABS = [
  { id: 'proximos', label: 'PRÓXIMOS' },
  { id: 'ao-vivo', label: 'AO VIVO' },
  { id: 'race', label: 'RACE' },
] as const

type TabId = (typeof TABS)[number]['id']

export function WorldScreen() {
  const [activeTab, setActiveTab] = useState<TabId>('ao-vivo')

  return (
    <div className="app-shell min-h-screen font-mono pb-24">
      <PageHeader title="WORLD TOUR" subtitle="CIRCUITO MUNDIAL" color="yellow" backTo="/hub" />

      <div className="p-4 space-y-4">
        {/* tab bar */}
        <div className="flex gap-1">
          {TABS.map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`flex-1 py-2 arcade-font text-[8px] border-2 transition-colors ${
                activeTab === t.id
                  ? 'bg-[#ffe600] text-black border-[#ffe600]'
                  : 'border-white/20 text-[#888]'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* tab content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.15 }}
          >
            {activeTab === 'proximos' && <ProximosTab />}
            {activeTab === 'ao-vivo' && <AoVivoTab />}
            {activeTab === 'race' && <RaceTab />}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  )
}
