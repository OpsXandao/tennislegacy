import { useState, useEffect } from 'react'
import { Dumbbell, Zap, Brain, Target, Activity } from 'lucide-react'
import { motion, AnimatePresence } from 'motion/react'
import { useNavigate } from 'react-router'
import { NeonCard, PixelBar, NeonButton, PageHeader } from '../components'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'
import treinoData from '../../data/treino.json'

interface TreinoOpcao {
  id: string
  nome: string
  descricao: string
  custo_energia: number
}

const TRAINING_FOCUS = treinoData.foco as Record<string, { label: string; cor: string }[]>

function TrainingIcon({ id, size = 20 }: { id: string; size?: number }) {
  if (id === 'fisico')      return <Dumbbell size={size} className="text-neon-cyan" />
  if (id === 'psicologico') return <Brain size={size} className="text-neon-yellow" />
  return <Target size={size} className="text-neon-green" />
}

function fadigaAdvisory(fadiga: number): { texto: string; cor: string } | null {
  const aviso = treinoData.avisos_fadiga
    .slice()
    .sort((a, b) => b.min - a.min)
    .find((a) => fadiga >= a.min)
  return aviso ?? null
}

export function TrainingScreen() {
  const navigate = useNavigate()
  const { jogador, patchJogador, setSemana, ano, semana } = useGameStore()
  const [opcoes,       setOpcoes]       = useState<TreinoOpcao[]>([])
  const [loading,      setLoading]      = useState(false)
  const [treinando,    setTreinando]    = useState(false)
  const [melhorias,    setMelhorias]    = useState<Record<string, number> | null>(null)
  const [erro,         setErro]         = useState('')
  const [descansando,  setDescansando]  = useState(false)
  const [aviso,        setAviso]        = useState('')
  const [focado,       setFocado]       = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    api.treinamento.opcoes()
      .then((res) => setOpcoes(res.opcoes))
      .catch(() => setErro('Erro ao carregar opções de treino.'))
      .finally(() => setLoading(false))
  }, [])

  function _navegarWeekAdvance(
    res: any,
    motivo: 'treino' | 'descanso',
    melhoriasList?: Record<string, number>,
  ) {
    if (res.jogador_status) patchJogador(res.jogador_status)
    const toSemana = res.semana ?? semana + 1
    const toAno    = res.ano ?? ano
    setSemana(toSemana, toAno)
    const eventosTreino = melhoriasList && Object.keys(melhoriasList).length > 0
      ? Object.entries(melhoriasList).map(([attr, val]) => `📈 ${attr.toUpperCase()} +${val}`)
      : []
    const eventosLevelUp: string[] = res.level_up
      ? [`⭐ SUBIU DE NÍVEL! Nível ${res.nivel_novo}${res.pontos_skill_ganhos > 0 ? ` (+${res.pontos_skill_ganhos} pts de skill)` : ''}`]
      : []
    const eventosApi = (res.eventos ?? []).map((e: any) => typeof e === 'string' ? e : e?.texto ?? String(e))
    navigate('/week-advance', {
      replace: true,
      state: {
        fromSemana: semana,
        fromAno: ano,
        toSemana,
        toAno,
        campeoes: res.resumo_mundial?.campeoes ?? [],
        eventos: [...eventosLevelUp, ...eventosTreino, ...eventosApi],
        motivo,
      },
    })
  }

  async function handleTreinar(focoId: string) {
    if (treinando) return
    setErro('')
    setAviso('')
    setMelhorias(null)
    setTreinando(true)
    setFocado(focoId)
    try {
      const res = await api.treinamento.executar(focoId)
      if (res.ok) _navegarWeekAdvance(res, 'treino', res.melhorias)
    } catch (e: any) {
      setErro(e.message || 'Falha no treinamento.')
      setTreinando(false)
      setFocado(null)
    }
  }

  async function handleDescansar() {
    if (descansando) return
    setErro('')
    setAviso('')
    setMelhorias(null)
    setDescansando(true)
    try {
      const res = await api.treinamento.descanso()
      _navegarWeekAdvance(res, 'descanso')
    } catch (e: any) {
      setErro(e.message || 'Falha ao descansar.')
      setDescansando(false)
    }
  }

  const energia = jogador?.energia ?? 0
  const fadiga  = jogador?.fadiga ?? 0
  const advisory = fadigaAdvisory(fadiga)

  return (
    <div className="app-shell min-h-screen flex flex-col">
      <PageHeader title="ACADEMIA" color="green" backTo="/hub" />

      <div className="flex-1 p-4 space-y-5 overflow-y-auto pb-24">

        <NeonCard variant="cyan" hover={false}>
          <div className="grid grid-cols-2 gap-4">
            <PixelBar value={energia} variant="green" label="ENERGIA" showValue />
            <PixelBar value={fadiga}  variant="pink"  label="FADIGA"  showValue />
          </div>
          {advisory && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mt-3 flex items-center gap-2 border px-3 py-2"
              style={{
                borderColor: `${advisory.cor}55`,
                background: `${advisory.cor}0d`,
              }}
            >
              <Activity size={12} style={{ color: advisory.cor, flexShrink: 0 }} />
              <span
                className="text-[8px] leading-tight"
                style={{ fontFamily: 'var(--font-arcade)', color: advisory.cor }}
              >
                {advisory.texto}
              </span>
            </motion.div>
          )}
        </NeonCard>

        <AnimatePresence>
          {melhorias && Object.keys(melhorias).length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="bg-neon-green/20 border-2 border-neon-green p-3 text-center"
            >
              <div className="arcade-font text-[10px] text-neon-green mb-2 uppercase font-bold">
                EVOLUÇÃO CONCLUÍDA!
              </div>
              <div className="flex flex-wrap justify-center gap-2">
                {Object.entries(melhorias).map(([attr, valor]) => (
                  <span key={attr} className="arcade-font text-[9px] text-white bg-black/40 px-2 py-1">
                    {attr.toUpperCase()}: +{valor}
                  </span>
                ))}
              </div>
            </motion.div>
          )}
          {melhorias && Object.keys(melhorias).length === 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="arcade-font text-[10px] text-[#888] text-center"
            >
              Treino finalizado, mas nenhum atributo subiu desta vez.
            </motion.div>
          )}
          {erro && (
            <motion.div className="arcade-font text-[10px] text-neon-pink text-center border border-neon-pink p-2">
              {erro}
            </motion.div>
          )}
          {aviso && (
            <motion.div className="arcade-font text-[10px] text-neon-green text-center border border-neon-green p-2">
              {aviso}
            </motion.div>
          )}
        </AnimatePresence>

        {loading ? (
          <div className="text-center text-[10px] text-white/30 py-8" style={{ fontFamily: 'var(--font-arcade)' }}>
            CARREGANDO...
          </div>
        ) : (
          <div className="space-y-4">
            {opcoes.map((opcao) => {
              const focus   = TRAINING_FOCUS[opcao.id] ?? []
              const isBusy  = treinando || descansando
              const variant = opcao.id === 'psicologico' ? 'yellow' : opcao.id === 'fisico' ? 'cyan' : 'green'
              const energiaInsuficiente = energia < opcao.custo_energia

              return (
                <NeonCard
                  key={opcao.id}
                  variant={variant}
                  className={isBusy ? 'opacity-50 pointer-events-none' : ''}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-2">
                      <TrainingIcon id={opcao.id} />
                      <span className="pixel-font text-sm text-white">{opcao.nome.toUpperCase()}</span>
                    </div>
                    <div
                      className="flex items-center gap-1"
                      style={{ color: 'var(--neon-pink)' }}
                    >
                      <Zap size={12} fill="currentColor" />
                      <span className="arcade-font text-[10px]">-{opcao.custo_energia}</span>
                    </div>
                  </div>

                  <p className="arcade-font text-[9px] text-[#888] mb-3 leading-tight">
                    {opcao.descricao}
                  </p>

                  {focus.length > 0 && (
                    <div className="mb-4">
                      <div
                        className="text-[7px] text-white/30 mb-1.5 tracking-widest"
                        style={{ fontFamily: 'var(--font-arcade)' }}
                      >
                        FOCO DO TREINO
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {focus.map((f) => (
                          <span
                            key={f.label}
                            className="text-[8px] px-2 py-0.5 border"
                            style={{
                              fontFamily: 'var(--font-arcade)',
                              color: f.cor,
                              borderColor: `${f.cor}44`,
                              background: `${f.cor}0d`,
                            }}
                          >
                            {f.label}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {energiaInsuficiente && (
                    <div
                      className="text-[8px] text-neon-pink mb-2"
                      style={{ fontFamily: 'var(--font-arcade)' }}
                    >
                      ⚡ ENERGIA INSUFICIENTE
                    </div>
                  )}

                  <NeonButton
                    variant={variant}
                    className="w-full py-2 text-[10px]"
                    disabled={energiaInsuficiente || isBusy}
                    onClick={() => handleTreinar(opcao.id)}
                    blink={treinando && focado === opcao.id}
                  >
                    {treinando && focado === opcao.id ? 'TREINANDO...' : 'TREINAR AGORA'}
                  </NeonButton>
                </NeonCard>
              )
            })}
          </div>
        )}

        <NeonCard variant="pink" hover={false}>
          <div className="mb-2 arcade-font text-[10px] text-neon-pink uppercase">Recuperação</div>
          <p className="mb-4 arcade-font text-[9px] text-[#888] leading-tight">
            Pule a semana para recuperar energia e reduzir fadiga.
          </p>
          <NeonButton
            variant="pink"
            className="w-full py-2 text-[10px]"
            onClick={handleDescansar}
            blink={descansando}
          >
            {descansando ? 'DESCANSANDO...' : 'DESCANSAR E AVANÇAR'}
          </NeonButton>
        </NeonCard>
      </div>

      <AnimatePresence>
        {(treinando || descansando) && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/92 flex flex-col items-center justify-center gap-6"
          >
            <div className="relative">
              {focado === 'fisico' || descansando ? (
                <Dumbbell
                  className={descansando ? 'text-neon-pink' : 'text-neon-cyan'}
                  style={{ width: 64, height: 64 }}
                />
              ) : focado === 'psicologico' ? (
                <Brain className="text-neon-yellow" style={{ width: 64, height: 64 }} />
              ) : (
                <Target className="text-neon-green" style={{ width: 64, height: 64 }} />
              )}
              <motion.div
                animate={{ scale: [1, 1.6, 1], opacity: [0.4, 0.8, 0.4] }}
                transition={{ duration: 1.1, repeat: Infinity }}
                className="absolute inset-0 blur-3xl rounded-full"
                style={{
                  background: focado === 'psicologico'
                    ? 'rgba(255,230,0,0.18)'
                    : focado === 'fisico'
                    ? 'rgba(0,229,255,0.18)'
                    : descansando
                    ? 'rgba(255,61,100,0.15)'
                    : 'rgba(0,255,136,0.18)',
                }}
              />
            </div>

            <div>
              <div
                className="text-neon-green text-lg tracking-widest animate-pulse text-center"
                style={{
                  fontFamily: 'var(--font-pixel)',
                  color: focado === 'psicologico'
                    ? 'var(--neon-yellow)'
                    : focado === 'fisico'
                    ? 'var(--neon-cyan)'
                    : descansando
                    ? 'var(--neon-pink)'
                    : 'var(--neon-green)',
                }}
              >
                {treinando ? 'TREINANDO...' : 'RECUPERANDO...'}
              </div>

              {focado && TRAINING_FOCUS[focado] && (
                <div className="flex justify-center gap-2 mt-3">
                  {TRAINING_FOCUS[focado].map((f) => (
                    <motion.span
                      key={f.label}
                      animate={{ opacity: [0.4, 1, 0.4] }}
                      transition={{ duration: 1.3, repeat: Infinity, delay: Math.random() * 0.8 }}
                      className="text-[8px] px-2 py-0.5"
                      style={{
                        fontFamily: 'var(--font-arcade)',
                        color: f.cor,
                        border: `1px solid ${f.cor}44`,
                      }}
                    >
                      {f.label}
                    </motion.span>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
