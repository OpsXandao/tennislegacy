import { useEffect, useMemo, useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { useLocation, useNavigate } from 'react-router'
import { CalendarDays, ChevronRight, Trophy } from 'lucide-react'
import { PixelFlag } from '../components'
import { useGameStore } from '../../store/gameStore'
import type { CampeaoSemana, TorneioCalendario, WeekAdvanceStep } from '../../types'

interface RivalInfo {
  nome: string
  ranking: number
  h2h: { v: number; d: number }
}

interface WeekAdvanceLocationState {
  fromSemana: number
  fromAno: number
  toSemana: number
  toAno: number
  campeoes: CampeaoSemana[]
  eventos?: Array<string | { texto?: string; categoria?: string }>
  processamento?: WeekAdvanceStep[]
  torneiosDisponiveis?: TorneioCalendario[]
  motivo?: string
  rival_info?: RivalInfo | null
}

function contextLabel(motivo?: string): { titulo: string; sub: string } {
  if (motivo === 'treino')         return { titulo: 'SEMANA DE TREINO',   sub: 'PREPARAÇÃO CONCLUÍDA' }
  if (motivo === 'descanso')       return { titulo: 'RECUPERAÇÃO',         sub: 'ENERGIA RESTAURADA' }
  if (motivo === 'withdraw')       return { titulo: 'TORNEIO ENCERRADO',   sub: 'DESISTÊNCIA REGISTRADA' }
  if (motivo === 'tournament_end') return { titulo: 'FIM DE SEMANA',       sub: 'RESULTADOS DO CIRCUITO' }
  if (motivo === 'rest')           return { titulo: 'DESCANSO',            sub: 'SEMANA AVANÇADA' }
  return                                  { titulo: 'SEMANA AVANÇADA',     sub: 'CALENDÁRIO ATUALIZADO' }
}

function stepAccent(tom: WeekAdvanceStep['tom']): string {
  if (tom === 'positive') return '#00ff88'
  if (tom === 'warning')  return '#ffe600'
  if (tom === 'info')     return '#00e5ff'
  return '#c7d4d0'
}

function tourAccent(tour: string): string {
  return tour.toLowerCase().includes('wta') ? '#ff5f8f' : '#00ff88'
}

function defaultSteps(state: WeekAdvanceLocationState): WeekAdvanceStep[] {
  return [
    {
      id: 'advance_calendar',
      titulo: 'Calendário',
      resumo: `Semana ${state.fromSemana} encerrada. Avançando para a ${state.toSemana}.`,
      tom: 'info',
      detalhes: (state.eventos?.slice(0, 3) ?? []).map((e: any) =>
      typeof e === 'string' ? e : e?.texto ?? String(e)
    ),
    },
    {
      id: 'simulate_tournaments',
      titulo: 'Circuito Mundial',
      resumo: 'Resultados consolidados nos torneios do mundo.',
      tom: 'neutral',
      detalhes: state.campeoes.slice(0, 3).map((c) => `${c.torneio}: ${c.simples}`),
    },
    {
      id: 'init_next_week',
      titulo: 'Nova Semana',
      resumo: 'Agenda e compromissos prontos.',
      tom: 'positive',
      detalhes: state.torneiosDisponiveis?.slice(0, 3).map((t) => t.nome) ?? [],
    },
  ]
}

export function WeekAdvanceScreen() {
  const navigate    = useNavigate()
  const location    = useLocation()
  const { setSemana, setTorneio, setPartidaId, fetchJogador } = useGameStore()
  const state       = location.state as WeekAdvanceLocationState | null

  const [phase,             setPhase]             = useState(0)
  const [revealedSteps,     setRevealedSteps]     = useState(-1)
  const [revealedChampions, setRevealedChampions] = useState(-1)
  const [weekFlipped,       setWeekFlipped]       = useState(false)
  const [allowContinue,     setAllowContinue]     = useState(false)

  const campeoes           = useMemo(() => state?.campeoes ?? [], [state])
  const etapas             = useMemo(() => {
    if (!state) return []
    const raw = state.processamento?.length ? state.processamento : defaultSteps(state)
    return raw.map((etapa: any) => ({
      ...etapa,
      resumo: typeof etapa.resumo === 'string' ? etapa.resumo : etapa.resumo?.texto ?? String(etapa.resumo ?? ''),
      detalhes: (etapa.detalhes ?? []).map((d: any) => typeof d === 'string' ? d : d?.texto ?? String(d)),
    }))
  }, [state])
  const torneiosDisponiveis = useMemo(() => state?.torneiosDisponiveis ?? [], [state])
  const calendarStepIndex   = useMemo(() => {
    const idx = etapas.findIndex((e) => e.id === 'advance_calendar')
    return idx >= 0 ? idx : 0
  }, [etapas])

  useEffect(() => {
    if (!state) { navigate('/hub', { replace: true }); return }

    setTorneio(null)
    setPartidaId(null)

    const timers: number[] = []
    const push = (fn: () => void, ms: number) => timers.push(window.setTimeout(fn, ms))

    push(() => setWeekFlipped(true), 480)
    push(() => setPhase(1), 680)

    etapas.forEach((_, i) => {
      push(() => {
        setRevealedSteps(i)
        if (i === calendarStepIndex) setSemana(state.toSemana, state.toAno)
      }, 780 + i * 360)
    })

    const afterSteps = 780 + etapas.length * 360

    push(() => setPhase(2), afterSteps + 140)
    campeoes.forEach((_, i) =>
      push(() => setRevealedChampions(i), afterSteps + 280 + i * 240),
    )

    const afterChamps = afterSteps + 280 + Math.max(campeoes.length, 1) * 240

    push(() => setPhase(3), afterChamps + 140)
    push(() => {
      setPhase(4)
      setAllowContinue(true)
      fetchJogador().catch(() => {})
    }, afterChamps + 420)

    return () => timers.forEach(clearTimeout)
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  if (!state) return null

  const { titulo, sub } = contextLabel(state.motivo)

  return (
    <div
      className="min-h-screen text-white"
      style={{ background: 'linear-gradient(160deg, #050f0a 0%, #030a07 55%, #020608 100%)' }}
    >
      <motion.div
        className="fixed inset-0 pointer-events-none"
        animate={{ opacity: weekFlipped ? 1 : 0 }}
        transition={{ duration: 1.4 }}
        style={{
          background:
            'radial-gradient(ellipse at 50% 18%, rgba(0,255,136,0.07) 0%, transparent 52%)',
        }}
      />

      <div className="relative z-10 max-w-sm mx-auto px-5 pt-12 pb-28">

        <div className="text-center mb-14">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="text-[8px] tracking-[0.42em] text-white/18 mb-8"
            style={{ fontFamily: 'var(--font-arcade)' }}
          >
            {titulo}
          </motion.div>

          <div className="flex items-center justify-center gap-6">
            <motion.div
              animate={weekFlipped ? { opacity: 0.18, scale: 0.8 } : { opacity: 1, scale: 1 }}
              transition={{ duration: 0.48, delay: 0.42 }}
              className="text-center"
            >
              <div
                className="text-[7px] text-white/20 mb-1"
                style={{ fontFamily: 'var(--font-arcade)' }}
              >
                SEMANA
              </div>
              <div
                className="text-[58px] leading-none text-neon-yellow"
                style={{
                  fontFamily: 'var(--font-pixel)',
                  textShadow: '0 0 22px rgba(255,230,0,0.35)',
                }}
              >
                {state.fromSemana}
              </div>
            </motion.div>

            <motion.div
              animate={{ opacity: weekFlipped ? 1 : 0, x: weekFlipped ? 0 : -12 }}
              transition={{ duration: 0.32, delay: 0.52 }}
              className="text-neon-cyan/60"
            >
              <ChevronRight size={28} />
            </motion.div>

            <motion.div
              animate={weekFlipped ? { opacity: 1, scale: 1 } : { opacity: 0.14, scale: 0.8 }}
              transition={{ duration: 0.48, delay: 0.42 }}
              className="text-center"
            >
              <div
                className="text-[7px] text-neon-green/35 mb-1"
                style={{ fontFamily: 'var(--font-arcade)' }}
              >
                PRÓXIMA
              </div>
              <div
                className="text-[58px] leading-none"
                style={{
                  fontFamily: 'var(--font-pixel)',
                  color: weekFlipped ? 'var(--neon-green)' : '#0f2018',
                  textShadow: weekFlipped ? '0 0 30px rgba(0,255,136,0.58)' : 'none',
                  transition: 'color 0.44s ease, text-shadow 0.44s ease',
                }}
              >
                {state.toSemana}
              </div>
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.22 }}
            className="text-[7px] tracking-widest text-white/12 mt-7"
            style={{ fontFamily: 'var(--font-arcade)' }}
          >
            {sub} · {state.toAno}
          </motion.div>
        </div>

        <AnimatePresence>
          {phase >= 1 && (
            <motion.div
              key="steps"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-1 mb-12"
            >
              {etapas.map((etapa, i) => {
                const active  = i === revealedSteps
                const done    = i < revealedSteps || (allowContinue && i <= revealedSteps)
                const visible = active || done
                const color   = stepAccent(etapa.tom)

                return (
                  <motion.div
                    key={etapa.id}
                    initial={{ opacity: 0, x: -22 }}
                    animate={i <= revealedSteps ? { opacity: 1, x: 0 } : { opacity: 0, x: -22 }}
                    transition={{ duration: 0.28, ease: 'easeOut' }}
                    className="flex items-start gap-3 py-2.5 pl-4 border-l-2"
                    style={{ borderColor: visible ? color : '#162518' }}
                  >
                    <span
                      className="shrink-0 text-[10px] pt-0.5 w-3"
                      style={{ fontFamily: 'var(--font-arcade)', color }}
                    >
                      {done ? '✓' : active ? '·' : ''}
                    </span>

                    <div>
                      <div
                        className="text-[8px] tracking-wider mb-0.5"
                        style={{
                          fontFamily: 'var(--font-arcade)',
                          color: visible ? color : '#1e3328',
                        }}
                      >
                        {etapa.titulo.toUpperCase()}
                      </div>

                      {visible && (
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 0.1 }}
                        >
                          <div
                            className="text-[10px] text-white/45"
                            style={{ fontFamily: 'var(--font-pixel)' }}
                          >
                            {etapa.resumo}
                          </div>
                          {etapa.detalhes.length > 0 && (
                            <div className="mt-1 space-y-0.5">
                              {etapa.detalhes.slice(0, 2).map((d: any, i: number) => {
                                const texto = typeof d === 'string' ? d : d?.texto ?? String(d)
                                return (
                                  <div
                                    key={i}
                                    className="text-[8px] text-white/22"
                                    style={{ fontFamily: 'var(--font-arcade)' }}
                                  >
                                    › {texto}
                                  </div>
                                )
                              })}
                            </div>
                          )}
                        </motion.div>
                      )}
                    </div>
                  </motion.div>
                )
              })}
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {phase >= 2 && campeoes.length > 0 && (
            <motion.section
              key="champions"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mb-12"
            >
              <div className="flex items-center gap-2 mb-5">
                <Trophy size={11} className="text-neon-yellow/55" />
                <span
                  className="text-[8px] tracking-[0.3em] text-neon-yellow/40"
                  style={{ fontFamily: 'var(--font-arcade)' }}
                >
                  CAMPEÕES DA SEMANA
                </span>
                <div
                  className="flex-1 h-px"
                  style={{
                    background:
                      'linear-gradient(90deg, rgba(255,230,0,0.14), transparent)',
                  }}
                />
              </div>

              <div className="space-y-2">
                {campeoes.map((c, i) => {
                  const accent = tourAccent(c.tour)
                  return (
                    <motion.div
                      key={`${c.torneio}-${c.tour}`}
                      initial={{ opacity: 0, x: 30 }}
                      animate={
                        i <= revealedChampions
                          ? { opacity: 1, x: 0 }
                          : { opacity: 0, x: 30 }
                      }
                      transition={{ duration: 0.32, ease: 'easeOut' }}
                      style={{
                        borderLeft: `2px solid ${accent}`,
                        background: `${accent}09`,
                        paddingLeft: 14,
                        paddingRight: 12,
                        paddingTop: 10,
                        paddingBottom: 10,
                      }}
                    >
                      <div
                        className="text-[7px] text-white/22 mb-1"
                        style={{ fontFamily: 'var(--font-arcade)' }}
                      >
                        {c.torneio.toUpperCase()} · {c.tour.toUpperCase()}
                      </div>
                      <div
                        className="text-[15px] text-white leading-tight"
                        style={{ fontFamily: 'var(--font-pixel)' }}
                      >
                        {c.simples}
                      </div>
                      {c.duplas && (
                        <div
                          className="text-[9px] text-white/28 mt-0.5"
                          style={{ fontFamily: 'var(--font-arcade)' }}
                        >
                          Duplas · {c.duplas}
                        </div>
                      )}
                    </motion.div>
                  )
                })}
              </div>
            </motion.section>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {phase >= 3 && state.rival_info && (
            <motion.div
              key="rival"
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.36 }}
              className="mb-8 px-4 py-3"
              style={{
                background: 'rgba(255,46,99,0.07)',
                border: '1px solid rgba(255,46,99,0.3)',
              }}
            >
              <div
                className="text-[7px] tracking-[0.3em] mb-2"
                style={{ fontFamily: 'var(--font-arcade)', color: '#ff2e63' }}
              >
                ⚔ RIVAL NA SEMANA
              </div>
              <div
                className="text-[14px] text-white/90"
                style={{ fontFamily: 'var(--font-pixel)' }}
              >
                {state.rival_info.nome}
              </div>
              <div
                className="text-[8px] text-white/35 mt-1"
                style={{ fontFamily: 'var(--font-arcade)' }}
              >
                {state.rival_info.ranking > 0 && `RK #${state.rival_info.ranking} · `}
                H2H {state.rival_info.h2h.v}V {state.rival_info.h2h.d}D
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {phase >= 3 && torneiosDisponiveis.length > 0 && (
            <motion.section
              key="upcoming"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.38 }}
              className="mb-12"
            >
              <div className="flex items-center gap-2 mb-5">
                <CalendarDays size={11} className="text-neon-cyan/55" />
                <span
                  className="text-[8px] tracking-[0.3em] text-neon-cyan/40"
                  style={{ fontFamily: 'var(--font-arcade)' }}
                >
                  PRÓXIMA SEMANA
                </span>
                <div
                  className="flex-1 h-px"
                  style={{
                    background:
                      'linear-gradient(90deg, rgba(0,229,255,0.12), transparent)',
                  }}
                />
              </div>

              <div className="space-y-1">
                {torneiosDisponiveis.slice(0, 4).map((torneio) => (
                  <div
                    key={torneio.nome}
                    className="flex items-center gap-3 px-3 py-2.5"
                    style={{
                      background: 'rgba(0,229,255,0.04)',
                      borderBottom: '1px solid rgba(0,229,255,0.07)',
                    }}
                  >
                    {torneio.codigo_pais ? (
                      <PixelFlag countryCode={torneio.codigo_pais} size="sm" />
                    ) : null}
                    <div className="flex-1 min-w-0">
                      <div
                        className="text-[11px] text-white/75 truncate"
                        style={{ fontFamily: 'var(--font-pixel)' }}
                      >
                        {torneio.nome}
                      </div>
                      <div
                        className="text-[8px] text-white/22 mt-0.5"
                        style={{ fontFamily: 'var(--font-arcade)' }}
                      >
                        {torneio.tipo} · {torneio.superficie}
                      </div>
                    </div>
                    {torneio.horario_local && (
                      <div
                        className="text-[9px] text-neon-cyan/35 shrink-0"
                        style={{ fontFamily: 'var(--font-arcade)' }}
                      >
                        {torneio.horario_local}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </motion.section>
          )}
        </AnimatePresence>

        <div className="flex justify-center">
          {allowContinue ? (
            <motion.button
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.42 }}
              onClick={() => navigate('/hub', { replace: true })}
              className="relative border-2 border-neon-cyan px-14 py-4 text-[11px] text-neon-cyan"
              style={{
                fontFamily: 'var(--font-arcade)',
                background: 'rgba(0,229,255,0.05)',
              }}
            >
              <motion.span
                className="absolute inset-0 border-2 border-neon-cyan pointer-events-none"
                animate={{ opacity: [0.45, 0, 0.45] }}
                transition={{ duration: 1.7, repeat: Infinity }}
              />
              CONTINUAR
            </motion.button>
          ) : (
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1.1, repeat: Infinity, ease: 'linear' }}
              className="w-5 h-5 border border-neon-green/18 border-t-neon-green rounded-full"
            />
          )}
        </div>
      </div>
    </div>
  )
}
