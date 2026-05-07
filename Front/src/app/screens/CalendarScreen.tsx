import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router'
import { Trophy, X } from 'lucide-react'
import { motion, AnimatePresence } from 'motion/react'
import { ActionDock, NeonButton, PageHeader, ScreenSection, PixelFlag } from '../components'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'
import type { TorneioCalendario, CampeaoSemana } from '../../types'
import { TournamentEntryModal } from '../components/TournamentEntryModal'

type TierVisual = 'grandslam' | 'masters' | 'atp500' | 'atp250'

function toTier(tipo: string): TierVisual {
  const t = tipo.toLowerCase()
  if (t.includes('grand slam')) return 'grandslam'
  if (t.includes('1000')) return 'masters'
  if (t.includes('500')) return 'atp500'
  return 'atp250'
}

function normalizeSurface(surface: string): 'hard' | 'clay' | 'grass' {
  const raw = surface.toLowerCase()
  if (raw.includes('saibro')) return 'clay'
  if (raw.includes('grama')) return 'grass'
  return 'hard'
}

function tierConfig(tier: TierVisual) {
  if (tier === 'grandslam') {
    return { color: '#ffe600', glow: '0 0 12px rgba(255,230,0,0.45)', label: 'GRAND SLAM', badge: '👑' }
  }
  if (tier === 'masters') {
    return { color: '#00ff88', glow: '0 0 12px rgba(0,255,136,0.35)', label: 'MASTERS 1000', badge: '⭐' }
  }
  if (tier === 'atp500') {
    return { color: '#00e5ff', glow: '0 0 12px rgba(0,229,255,0.35)', label: 'ATP / WTA 500', badge: '⚡' }
  }
  return { color: '#ff7b00', glow: '0 0 12px rgba(255,123,0,0.35)', label: 'ATP / WTA 250', badge: '🎾' }
}

const surfaceColors = {
  hard: '#1e3a8a',
  clay: '#991b1b',
  grass: '#166534',
}

function surfaceTexture(surface: 'hard' | 'clay' | 'grass') {
  if (surface === 'clay') return 'repeating-linear-gradient(45deg, #7f1d1d 0px, #7f1d1d 2px, #991b1b 2px, #991b1b 4px)'
  if (surface === 'grass') return 'repeating-linear-gradient(0deg, #14532d 0px, #14532d 1px, #166534 1px, #166534 2px)'
  return 'repeating-conic-gradient(#1e3a8a 0% 25%, #172554 0% 50%)'
}

export function CalendarScreen() {
  const navigate = useNavigate()
  const { semana: semanaAtual, ano } = useGameStore()
  const [selectedWeek, setSelectedWeek] = useState(semanaAtual)
  const [torneiosSemana, setTorneiosSemana] = useState<TorneioCalendario[]>([])
  const [semanasTorneio, setSemanasTorneio] = useState<Set<number>>(new Set())
  const [loading, setLoading] = useState(true)
  const [torneioParaInscrever, setTorneioParaInscrever] = useState<TorneioCalendario | null>(null)
  const [inscrevendo, setInscrevendo] = useState(false)
  const [erroInscricao, setErroInscricao] = useState('')
  const [convocacao, setConvocacao] = useState<{ convocado: boolean; mensagem: string; torneio?: TorneioCalendario } | null>(null)
  const [campeoesSemana, setCampeoesSemana] = useState<CampeaoSemana[]>([])
  const setTorneio = useGameStore((s) => s.setTorneio)
  const scrollRef = useRef<HTMLDivElement>(null)
  const setSemana = useGameStore((s) => s.setSemana)

  async function checarConvocacao() {
    try {
      const r = await api.torneio.checarConvocacao()
      setConvocacao(r)
    } catch {
      setConvocacao(null)
    }
  }

  useEffect(() => {
    api.calendario
      .atual()
      .then((r) => {
        setSemana(r.semana, r.ano)
        setSelectedWeek(r.semana)
        setTorneiosSemana(r.torneios)
        setSemanasTorneio((prev) => {
          const next = new Set(prev)
          r.torneios.forEach((t) => next.add(t.semana))
          return next
        })
        if (r.semana === r.semana) checarConvocacao()
      })
      .catch(() => {})
  }, [setSemana])

  useEffect(() => {
    setErroInscricao('')
    if (selectedWeek === semanaAtual) {
      checarConvocacao()
    } else {
      setConvocacao(null)
    }
  }, [selectedWeek, semanaAtual])

  useEffect(() => {
    setLoading(true)
    api.calendario
      .semana(selectedWeek)
      .then((r) => {
        setTorneiosSemana(r.torneios)
        if (r.torneios.length > 0) {
          setSemanasTorneio((prev) => {
            const next = new Set(prev)
            r.torneios.forEach((t) => next.add(t.semana))
            return next
          })
        }
      })
      .catch(() => setTorneiosSemana([]))
      .finally(() => setLoading(false))
  }, [selectedWeek])

  useEffect(() => {
    if (!scrollRef.current) return
    const el = scrollRef.current.querySelector(`[data-week="${selectedWeek}"]`)
    el?.scrollIntoView({ inline: 'center', behavior: 'smooth' })
  }, [selectedWeek])

  async function handleConfirmarInscricao(modalidade: string, parceiro?: string) {
    if (!torneioParaInscrever && !convocacao?.torneio) return
    setInscrevendo(true)
    const targetNome = torneioParaInscrever?.nome || convocacao?.torneio?.nome
    setTorneioParaInscrever(null)
    try {
      const r = await api.torneio.criar(modalidade as any, parceiro, targetNome)
      if (r.ok) {
        setTorneio(r.torneio)
        if (r.torneio.destino_click_hub) {
          navigate(r.torneio.destino_click_hub)
        } else if ((r.torneio as any).davis) {
          navigate('/davis')
        } else {
          navigate('/tournament')
        }
      }
    } catch {
      setErroInscricao('Erro ao entrar no torneio. Tente novamente.')
    } finally {
      setInscrevendo(false)
    }
  }

  async function handleDescansar() {
    try {
      const r = await api.calendario.avancar()
      setSemana(r.semana, r.ano ?? ano)
      setSelectedWeek(r.semana)
      const campeoes = r.resumo_mundial?.campeoes ?? []
      if (campeoes.length > 0) {
        setCampeoesSemana(campeoes)
      }
    } catch {
      // silencioso
    }
  }

  function handleFecharCampeoes() {
    setCampeoesSemana([])
  }

  return (
    <div className="app-shell min-h-screen font-mono pb-24">
      <AnimatePresence>
        {campeoesSemana.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 p-4 backdrop-blur-sm"
          >
            <motion.div
              initial={{ scale: 0.9, y: 20, opacity: 0 }}
              animate={{ scale: 1, y: 0, opacity: 1 }}
              exit={{ scale: 0.9, y: 20, opacity: 0 }}
              className="app-panel relative w-full max-w-md border-2 border-[#ffe600] shadow-[0_0_30px_rgba(255,230,0,0.3)]"
            >
              <div className="flex items-center justify-between border-b border-[#ffe600]/30 px-4 py-3">
                <div className="flex items-center gap-2">
                  <Trophy size={16} className="text-[#ffe600]" />
                  <span className="pixel-font text-sm text-[#ffe600]">CAMPEÕES DA SEMANA</span>
                </div>
                <button onClick={handleFecharCampeoes} className="text-[#ffe600] hover:scale-110 transition-transform">
                  <X size={20} />
                </button>
              </div>

              <div className="max-h-[60vh] overflow-y-auto p-4 space-y-2 [scrollbar-width:thin]">
                {['ATP', 'WTA'].map((tour) => {
                  const lista = campeoesSemana.filter((c) => c.tour === tour)
                  if (lista.length === 0) return null
                  return (
                    <div key={tour}>
                      <div className="arcade-font text-[9px] text-[#888] mb-2 tracking-widest">{tour}</div>
                      {lista.map((c) => (
                        <div key={c.torneio} className="mb-2 border border-[#333] bg-[#111] p-3">
                          <div className="arcade-font text-[8px] text-[#888] truncate mb-1">{c.torneio.toUpperCase()}</div>
                          <div className="flex items-center gap-1">
                            <Trophy size={10} className="text-[#ffe600] shrink-0" />
                            <span className="arcade-font text-[11px] text-white font-bold truncate">{c.simples.toUpperCase()}</span>
                          </div>
                          {c.duplas && (
                            <div className="mt-1 arcade-font text-[9px] text-[#00e5ff] truncate">
                              DUPLAS: {c.duplas.toUpperCase()}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )
                })}
              </div>

              <div className="p-4 border-t border-[#ffe600]/30">
                <NeonButton variant="yellow" className="w-full" onClick={handleFecharCampeoes}>
                  AVANÇAR SEMANA
                </NeonButton>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {torneioParaInscrever && (
        <TournamentEntryModal
          torneio={torneioParaInscrever}
          onClose={() => setTorneioParaInscrever(null)}
          onConfirm={handleConfirmarInscricao}
        />
      )}
      <PageHeader
        title="CIRCUITO MUNDIAL"
        subtitle={`TEMPORADA ${ano} • SEMANA ${selectedWeek}`}
        color="yellow"
        backTo="/hub"
      />

      <div className="p-4 space-y-6">

      <ScreenSection title="SELETOR DE SEMANA" subtitle="Navegue pelas 52 semanas da temporada" variant="yellow">
        <div ref={scrollRef} className="flex gap-2 overflow-x-auto pb-2 [scrollbar-width:thin]">
          {Array.from({ length: 52 }, (_, i) => i + 1).map((week) => {
            const hasTorneio = semanasTorneio.has(week)
            const isAtual = week === semanaAtual
            return (
              <button
                key={week}
                data-week={week}
                onClick={() => setSelectedWeek(week)}
                className={`flex h-14 w-14 shrink-0 flex-col items-center justify-center border-2 transition-all ${
                  week === selectedWeek
                    ? 'border-[#00ff88] bg-[#00ff88] text-black'
                    : hasTorneio
                    ? 'border-[#00ff88]/50 bg-[#1a1a2e] text-[#00ff88]'
                    : 'border-[#333] bg-transparent text-[#888]'
                } ${isAtual && week !== selectedWeek ? 'ring-1 ring-[#ffe600]' : ''}`}
              >
                <div className="pixel-font text-[10px]">{week}</div>
                {hasTorneio && <div className="mt-1 text-sm">●</div>}
              </button>
            )
          })}
        </div>
      </ScreenSection>

      <div className="grid grid-cols-3 gap-2">
        {loading && (
          <motion.div
            animate={{ opacity: [1, 0.3, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
            className="col-span-3 py-12 text-center pixel-font text-sm text-[#00ff88]"
          >
            CARREGANDO...
          </motion.div>
        )}

        {!loading && convocacao?.torneio && (
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="col-span-3 border-2 border-[#ffe600] bg-[#ffe600]/10 p-4 shadow-[0_0_15px_rgba(255,230,0,0.2)]"
          >
            <div className="mb-3 flex items-start justify-between">
              <div className="flex items-center gap-2">
                <Trophy size={16} className="text-[#ffe600]" />
                <span className="text-[10px] text-white" style={{ fontFamily: 'var(--font-arcade)' }}>CONVOCAÇÃO - COPA DAVIS</span>
              </div>
              <span className="text-[10px] font-bold text-[#ffe600]">ESPECIAL</span>
            </div>

            <div className="mb-1 text-xs text-white" style={{ fontFamily: 'var(--font-arcade)' }}>{convocacao.torneio.nome.toUpperCase()}</div>
            <p className="mb-4 text-[9px] text-[#00e5ff] uppercase">{convocacao.mensagem}</p>

            <NeonButton 
              variant="yellow" 
              className="w-full" 
              onClick={() => handleConfirmarInscricao('simples', undefined)}
              disabled={!convocacao.convocado || inscrevendo}
            >
              {convocacao.convocado ? 'REPRESENTAR SUA NAÇÃO' : 'NÃO CONVOCADO'}
            </NeonButton>
          </motion.div>
        )}

        {!loading && torneiosSemana.length === 0 && !convocacao?.torneio && (
          <div className="col-span-3 border-2 border-[#00ff88] bg-[#1a1a2e] p-6 text-center" style={{ boxShadow: 'var(--glow-green)' }}>
            <div className="mb-3 text-4xl">💤</div>
            <div className="text-sm text-[#888]">SEMANA DE DESCANSO</div>
            <div className="mt-2 text-xs text-[#666]">Nenhum torneio esta semana</div>
          </div>
        )}

        {!loading &&
          torneiosSemana.map((tournament, i) => {
            const tier = toTier(tournament.tipo)
            const config = tierConfig(tier)
            const surface = normalizeSurface(tournament.superficie)
            const sColor = surfaceColors[surface]
            const isPastOrFuture = selectedWeek !== semanaAtual

            return (
              <motion.div
                key={tournament.nome}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08 }}
                onClick={() => !isPastOrFuture && setTorneioParaInscrever(tournament)}
                className={`relative flex flex-col h-28 overflow-hidden border-2 transition-transform ${isPastOrFuture ? 'cursor-default opacity-60' : 'cursor-pointer active:scale-95'}`}
                style={{ borderColor: config.color, boxShadow: isPastOrFuture ? 'none' : config.glow }}
              >
                {/* Surface background - prominent */}
                <div
                  className="absolute inset-0 opacity-70"
                  style={{
                    backgroundColor: sColor,
                    backgroundImage: surfaceTexture(surface),
                    backgroundSize: '12px 12px',
                    imageRendering: 'pixelated',
                  }}
                />

                {/* Readability overlay */}
                <div className="absolute inset-0 bg-gradient-to-b from-black/65 via-black/25 to-black/80" />

                <div className="relative flex-1 p-2 flex flex-col justify-between">
                  {/* Top: competition type label + flag */}
                  <div className="flex items-start justify-between gap-1">
                    <div
                      className="text-[7px] font-bold tracking-widest leading-none"
                      style={{
                        color: config.color,
                        fontFamily: 'var(--font-arcade)',
                        textShadow: `0 0 8px ${config.color}`,
                      }}
                    >
                      {config.badge} {config.label}
                    </div>
                    {tournament.codigo_pais && (
                      <PixelFlag countryCode={tournament.codigo_pais} size="xl" />
                    )}
                  </div>

                  {/* Bottom: tournament name */}
                  <div>
                    <div
                      className="text-[10px] leading-tight text-white font-bold line-clamp-2"
                      style={{ fontFamily: 'var(--font-arcade)', textShadow: '1px 1px 3px black' }}
                    >
                      {tournament.nome.toUpperCase()}
                    </div>
                    <div className="text-[7px] text-[#00e5ff] uppercase truncate mt-0.5">{tournament.local}</div>
                  </div>
                </div>

                {/* Tier color bar */}
                <div className="relative h-1.5" style={{ backgroundColor: config.color }} />
              </motion.div>
            )
          })}

        {erroInscricao && <div className="col-span-3 text-center text-xs text-[#ff0055]">{erroInscricao}</div>}
      </div>

      </div>

      <ActionDock>
        <div className="mx-auto w-full max-w-6xl">
          <NeonButton variant="pink" className="w-full" onClick={handleDescansar}>
            {torneiosSemana.length > 0 ? 'DESCANSAR (PULAR SEMANA)' : 'PULAR SEMANA'}
          </NeonButton>
        </div>
      </ActionDock>
    </div>
  )
}
