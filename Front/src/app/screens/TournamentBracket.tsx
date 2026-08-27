import { useEffect, useState } from 'react'
import { motion } from 'motion/react'
import { useNavigate } from 'react-router'
import { ActionDock, NeonButton, PageHeader } from '../components'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'
import type { PartidaScout, TorneioState, WorldScheduleEvent } from '../../types'
import { FASE_ORDEM, type BracketSection, type Round } from './bracket/types'
import { nodesToRounds, splitRounds, isQualyPhase, faseLabelDisplay } from './bracket/utils'
import { BracketCanvas } from './bracket/BracketCanvas'

export function TournamentBracket() {
  const navigate = useNavigate()
  const { jogador, setTorneio, setPartidaId, semana, ano } = useGameStore()
  const nomeJogador = jogador?.nome ?? ''

  const [torneio, setLocal] = useState<TorneioState | null>(null)
  const [rounds, setRounds] = useState<Round[]>([])
  const [sections, setSections] = useState<BracketSection[]>([])
  const [activeSectionId, setActiveSectionId] = useState<'qualy' | 'main'>('main')
  const [loading, setLoading] = useState(true)
  const [temPartidaPendente, setTemPartidaPendente] = useState(false)
  const [avancar, setAvancar] = useState(false)
  const [simulandoRestante, setSimulandoRestante] = useState(false)
  const [campeaoFinal, setCampeaoFinal] = useState<string | null>(null)
  const [erroAcao, setErroAcao] = useState('')
  const [scoutData, setScoutData] = useState<PartidaScout | null>(null)
  const [loadingScout, setLoadingScout] = useState(false)
  const [confirmDesistir, setConfirmDesistir] = useState(false)
  const [avancando, setAvancando] = useState(false)
  const proximoEvento: WorldScheduleEvent | null = torneio?.proximo_evento_jogavel ?? null
  const jogadorPodeContinuar = Boolean(
    torneio?.jogador_ativo || torneio?.partida_disponivel || proximoEvento,
  )

  function limparEstadoTorneio() {
    setLocal(null)
    setTorneio(null)
    setRounds([])
    setSections([])
    setTemPartidaPendente(false)
  }

  useEffect(() => {
    api.torneio
      .estado()
      .then((t) => {
        if (!t) {
          limparEstadoTorneio()
          return
        }
        setLocal(t)
        setTorneio(t)
        const parsed = nodesToRounds(t.bracket, t.fase_atual, t.jogador_ativo, nomeJogador)
        const parsedSections = splitRounds(parsed, t.tipo)
        setRounds(parsed)
        setSections(parsedSections)
        setActiveSectionId(isQualyPhase(t.fase_atual) ? 'qualy' : 'main')
        setTemPartidaPendente(!!t.partida_disponivel)
      })
      .catch((err) => {
        console.error("Erro ao carregar estado do torneio:", err)
      })
      .finally(() => setLoading(false))
  }, [nomeJogador, setTorneio])

  async function recarregarTorneio() {
    const t = await api.torneio.estado()
    if (!t) {
      limparEstadoTorneio()
      return null
    }
    setLocal(t)
    setTorneio(t)
    const parsed = nodesToRounds(t.bracket, t.fase_atual, t.jogador_ativo, nomeJogador)
    const parsedSections = splitRounds(parsed, t.tipo)
    setRounds(parsed)
    setSections(parsedSections)
    setActiveSectionId(isQualyPhase(t.fase_atual) ? 'qualy' : 'main')
    setTemPartidaPendente(!!t.partida_disponivel)
    return t
  }

  async function handleAvancarMomento() {
    setAvancar(true)
    setErroAcao('')
    try {
      const r = await api.torneio.avancarProximoMomento()
      if (r.ok) {
        await recarregarTorneio()
        if (r.evento?.tipo === 'player_match') {
          setTemPartidaPendente(true)
        }
        return
      }
      await handleAvancarFase()
    } catch (err) {
      console.error("Erro ao avançar momento:", err)
      setErroAcao("Falha ao avançar o calendário do torneio.")
    } finally {
      setAvancar(false)
    }
  }

  async function handleAvancarFase() {
    setAvancar(true)
    try {
      await api.torneio.avancarFase()
      const t = await recarregarTorneio()
      if (!t) {
        setTorneio(null)
        setPartidaId(null)
        navigate('/hub')
        return
      }
    } catch (err) {
      console.error("Erro ao avançar fase:", err)
      setErroAcao("Falha ao avançar fase. Tente novamente.")
    } finally {
      setAvancar(false)
    }
  }

  async function handleAnalisarAdversario() {
    const nomeAdv = torneio?.info_partida?.adversario?.nome
    if (!nomeAdv) {
      handleJogar()
      return
    }
    setLoadingScout(true)
    try {
      const data = await api.partida.scout(nomeAdv)
      setScoutData(data)
    } catch (err) {
      console.error("Erro ao carregar scout do adversário:", err)
      handleJogar()
    } finally {
      setLoadingScout(false)
    }
  }

  async function handleJogar() {
    setScoutData(null)
    setErroAcao('')
    try {
      const ativa = await api.partida.ativa()
      if (ativa?.partida_id) {
        setPartidaId(ativa.partida_id)
      } else {
        setPartidaId(null)
      }
      navigate('/match')
    } catch (err) {
      console.error("Erro ao iniciar partida:", err)
      setPartidaId(null)
      navigate('/match')
    }
  }

  const getProximaFaseLabel = () => {
    if (!torneio || !torneio.bracket) return 'PROXIMA FASE'
    const atualKey = torneio.fase_atual.toLowerCase()
    const atualOrdem = FASE_ORDEM[atualKey] ?? 0

    const fasesNoBracket = Array.from(new Set(torneio.bracket.map((n) => n.fase.toLowerCase())))

    const proxima = fasesNoBracket
      .sort((a, b) => FASE_ORDEM[a] - FASE_ORDEM[b])
      .find((f) => FASE_ORDEM[f] > atualOrdem)

    if (proxima) {
      return `IR PARA ${faseLabelDisplay(proxima)}`
    }
    return 'AVANÇAR RODADA'
  }

  async function handleDesistir() {
    if (jogadorPodeContinuar) {
      try {
        const r = await api.torneio.desistir()
        if (typeof r.semana === 'number') {
          setTorneio(null)
          setPartidaId(null)
          navigate('/week-advance', {
            replace: true,
            state: {
              fromSemana: semana,
              fromAno: ano,
              toSemana: r.semana,
              toAno: r.ano ?? ano,
              campeoes: r.resumo_mundial?.campeoes ?? [],
              eventos: r.eventos ?? [],
              processamento: r.processamento ?? [],
              torneiosDisponiveis: r.torneios_disponiveis ?? [],
              motivo: 'withdraw',
            },
          })
          return
        }
      } catch (err) {
        console.error("Erro ao desistir do torneio:", err)
      }
    }
    setTorneio(null)
    navigate('/hub')
  }

  async function handleConcluirTorneio() {
    setAvancando(true)
    try {
      if (torneio?.fase_atual === 'finalizado' || campeaoFinal) {
        const r = await api.calendario.avancar()
        setTorneio(null)
        setPartidaId(null)
        navigate('/week-advance', {
          replace: true,
          state: {
            fromSemana: semana,
            fromAno: ano,
            toSemana: r.semana,
            toAno: r.ano ?? ano,
            campeoes: r.resumo_mundial?.campeoes ?? [],
            eventos: r.eventos ?? [],
            processamento: r.processamento ?? [],
            torneiosDisponiveis: r.torneios_disponiveis ?? [],
            rival_info: r.rival_info ?? null,
            motivo: 'tournament_end',
          },
        })
        return
      }
      setTorneio(null)
      setPartidaId(null)
      navigate('/hub')
    } catch (err) {
      console.error("Erro ao concluir torneio:", err)
      setTorneio(null)
      setPartidaId(null)
      navigate('/hub')
    } finally {
      setAvancando(false)
    }
  }

  async function handleSimularRestante() {
    setSimulandoRestante(true)
    let iterations = 0
    const MAX_ITERATIONS = 20
    try {
      let t = torneio
      while (t && t.fase_atual !== 'finalizado' && iterations < MAX_ITERATIONS) {
        iterations++
        await api.torneio.avancarFase()
        t = await api.torneio.estado()
        if (!t) break
        setLocal(t)
        setTorneio(t)
        const parsed = nodesToRounds(t.bracket, t.fase_atual, t.jogador_ativo, nomeJogador)
        const parsedSections = splitRounds(parsed, t.tipo)
        setRounds(parsed)
        setSections(parsedSections)
        setActiveSectionId(isQualyPhase(t.fase_atual) ? 'qualy' : 'main')
      }
      if (t?.campeao_simples) {
        setCampeaoFinal(t.campeao_simples)
      }
    } catch (err) {
      console.error("Erro ao simular restante do torneio:", err)
    } finally {
      setSimulandoRestante(false)
    }
  }

  return (
    <div className="app-shell min-h-screen overflow-x-clip pb-10">
      <PageHeader
        title={torneio?.nome || 'TOURNAMENT'}
        subtitle={torneio ? `${torneio.tipo} • ${torneio.superficie}` : 'CARREGANDO...'}
        color="green"
        backTo="/hub"
        right={
          torneio ? (
            <div
              className="border border-neon-yellow px-2 py-1 text-[7px] text-neon-yellow"
              style={{ fontFamily: 'var(--font-arcade)' }}
            >
              {torneio.fase_atual.toUpperCase()}
            </div>
          ) : undefined
        }
      />

      {loading && (
        <motion.div
          animate={{ opacity: [1, 0.3, 1] }}
          transition={{ duration: 1, repeat: Infinity }}
          className="text-center py-20 pixel-font text-sm text-neon-green"
        >
          CARREGANDO...
        </motion.div>
      )}

      {!loading && rounds.length === 0 && (
        <div className="text-center py-20 arcade-font text-sm text-[#888]">
          Nenhum torneio ativo.
        </div>
      )}

      {!loading && rounds.length > 0 && (
        <div className="mx-auto w-full max-w-7xl space-y-5">
          {sections.length > 1 && (
            <div className="flex gap-2 overflow-x-auto pb-1">
              {sections.map((section) => {
                const active = section.id === activeSectionId
                return (
                  <button
                    key={section.id}
                    type="button"
                    onClick={() => setActiveSectionId(section.id)}
                    className="min-w-[160px] border-2 px-4 py-2 text-left transition-all"
                    style={{
                      borderColor: active ? 'var(--neon-yellow)' : 'var(--neon-cyan)',
                      backgroundColor: active
                        ? 'color-mix(in srgb, var(--neon-yellow) 16%, var(--surface-card))'
                        : 'color-mix(in srgb, var(--neon-cyan) 8%, var(--surface-card))',
                      boxShadow: active ? 'var(--glow-gold-sm)' : 'none',
                    }}
                  >
                    <div
                      className="pixel-font text-xs"
                      style={{ color: active ? 'var(--neon-yellow)' : 'var(--neon-cyan)' }}
                    >
                      {section.title}
                    </div>
                    <div className="arcade-font text-[10px] app-muted">{section.subtitle}</div>
                  </button>
                )
              })}
            </div>
          )}

          {sections
            .filter((section) => section.id === activeSectionId)
            .map((section) => (
              <BracketCanvas key={section.title} section={section} />
            ))}
        </div>
      )}

      {!loading && (
        <ActionDock>
          {erroAcao && (
            <div className="mb-3 border border-neon-pink bg-[#22040d] px-3 py-2 arcade-font text-[10px] text-[#ff8da9]">
              {erroAcao.toUpperCase()}
            </div>
          )}
          {campeaoFinal && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-3 border-2 border-neon-yellow bg-neon-yellow/10 p-3 text-center shadow-[0_0_15px_rgba(255,230,0,0.3)]"
            >
              <div className="pixel-font text-[10px] text-neon-yellow mb-1">CAMPEÃO DO TORNEIO</div>
              <div className="arcade-font text-sm text-white font-bold">
                {campeaoFinal.toUpperCase()}
              </div>
            </motion.div>
          )}


          {proximoEvento && (
            <div className="mb-3 border-2 border-neon-green/60 bg-neon-green/5 p-3">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="pixel-font text-[10px] text-neon-green">PRÓXIMO MATCHDAY</div>
                  <div className="arcade-font text-[10px] text-white mt-1">
                    DIA {proximoEvento.dia} • {proximoEvento.hora} • {proximoEvento.fase.toUpperCase()}
                  </div>
                  <div className="arcade-font text-[9px] text-[#8aa] mt-1">
                    {proximoEvento.jogador1} vs {proximoEvento.jogador2}
                  </div>
                  <div className="arcade-font text-[8px] text-[#6f8790] mt-1">
                    {proximoEvento.quadra ?? 'Quadra'} • melhor de {proximoEvento.melhor_de ?? 3} • risco clima {Math.round((proximoEvento.risco_atraso_clima ?? 0) * 100)}%
                  </div>
                </div>
                <div className="arcade-font text-[8px] text-neon-yellow text-right">
                  {proximoEvento.presentation === 'ea_matchday' ? 'MATCHDAY' : 'WORLD SIM'}
                </div>
              </div>
            </div>
          )}

          {torneio?.entry_list_summary && (
            <div className="mb-3 border border-neon-cyan/40 bg-neon-cyan/5 p-3">
              <div className="pixel-font text-[9px] text-neon-cyan mb-2">ENTRY LIST</div>
              <div className="grid grid-cols-4 gap-2 text-center">
                <div>
                  <div className="pixel-font text-[10px] text-white">{torneio.entry_list_summary.main_draw ?? 0}</div>
                  <div className="arcade-font text-[7px] text-[#8aa]">MAIN</div>
                </div>
                <div>
                  <div className="pixel-font text-[10px] text-white">{torneio.entry_list_summary.qualifying ?? 0}</div>
                  <div className="arcade-font text-[7px] text-[#8aa]">QUALY</div>
                </div>
                <div>
                  <div className="pixel-font text-[10px] text-white">{torneio.entry_list_summary.wildcards ?? 0}</div>
                  <div className="arcade-font text-[7px] text-[#8aa]">WILD</div>
                </div>
                <div>
                  <div className="pixel-font text-[10px] text-white">#{torneio.entry_list_summary.cutoff_rank ?? '-'}</div>
                  <div className="arcade-font text-[7px] text-[#8aa]">CUT</div>
                </div>
              </div>
            </div>
          )}

          {scoutData && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-3 border-2 border-neon-cyan bg-neon-cyan/5 p-3"
            >
              <div className="flex justify-between items-center mb-2">
                <div className="pixel-font text-[10px] text-neon-cyan">ANÁLISE DE ADVERSÁRIO</div>
                <button
                  onClick={() => setScoutData(null)}
                  className="arcade-font text-[9px] text-[#888]"
                >
                  ✕ FECHAR
                </button>
              </div>
              <div className="flex gap-3 items-start mb-2">
                <div>
                  <div className="arcade-font text-[11px] text-white font-bold">
                    {scoutData.nome}
                  </div>
                  <div className="arcade-font text-[9px] text-[#888]">
                    #{scoutData.ranking} • OVR {scoutData.overall} • {scoutData.superficie_favorita}
                  </div>
                </div>
                <div className="ml-auto flex gap-1">
                  {scoutData.forma_recente.map((r: string, i: number) => (
                    <div
                      key={i}
                      className="w-5 h-5 flex items-center justify-center arcade-font text-[8px] font-bold border"
                      style={{
                        background: r === 'V' ? '#00ff8820' : '#ff005520',
                        borderColor: r === 'V' ? 'var(--neon-green)' : 'var(--neon-pink)',
                        color: r === 'V' ? 'var(--neon-green)' : 'var(--neon-pink)',
                      }}
                    >
                      {r}
                    </div>
                  ))}
                </div>
              </div>
              {Object.keys(scoutData.atributos || {}).length > 0 && (
                <div className="grid grid-cols-4 gap-1 mb-2">
                  {Object.entries(scoutData.atributos as Record<string, number>)
                    .slice(0, 8)
                    .map(([k, v]) => (
                      <div
                        key={k}
                        className="border border-neon-cyan/30 bg-black/30 px-1 py-1 text-center"
                      >
                        <div className="arcade-font text-[7px] text-[#8eb5c8]">
                          {k.slice(0, 4).toUpperCase()}
                        </div>
                        <div className="pixel-font text-[10px] text-neon-cyan">{v}</div>
                      </div>
                    ))}
                </div>
              )}
              <div className="flex justify-between items-center">
                <div className="arcade-font text-[9px] text-[#888]">
                  H2H:{' '}
                  <span className="text-neon-green">{scoutData.h2h.vitorias_jogador}V</span>{' '}
                  /{' '}
                  <span className="text-neon-pink">{scoutData.h2h.vitorias_adversario}D</span>
                </div>
                <NeonButton
                  variant="yellow"
                  className="text-[9px] px-3 py-1"
                  onClick={handleJogar}
                >
                  ▶ JOGAR AGORA
                </NeonButton>
              </div>
            </motion.div>
          )}

          {!torneio || !jogadorPodeContinuar ? (
            campeaoFinal || torneio?.fase_atual === 'finalizado' ? (
              <NeonButton variant="green" className="w-full" onClick={handleConcluirTorneio} disabled={avancando}>
                {avancando ? 'AVANÇANDO...' : 'AVANÇAR SEMANA'}
              </NeonButton>
            ) : (
              <div className="grid gap-3 grid-cols-2">
                <NeonButton
                  variant="yellow"
                  className="w-full"
                  onClick={handleSimularRestante}
                  blink={simulandoRestante}
                >
                  {simulandoRestante ? 'SIMULANDO...' : 'SIMULAR RESTANTE'}
                </NeonButton>
                <NeonButton
                  variant="pink"
                  className="w-full"
                  onClick={() => setConfirmDesistir(true)}
                >
                  SAIR
                </NeonButton>
              </div>
            )
          ) : (
            <div className="grid gap-3 md:grid-cols-2">
              {temPartidaPendente ? (
                <div className="grid grid-cols-2 gap-2">
                  <NeonButton
                    variant="cyan"
                    className="w-full text-[9px]"
                    onClick={handleAnalisarAdversario}
                    blink={loadingScout}
                  >
                    {loadingScout ? '...' : '🔍 ANALISAR'}
                  </NeonButton>
                  <NeonButton
                    variant="yellow"
                    className="w-full"
                    onClick={handleJogar}
                    critical
                  >
                    ▶ JOGAR
                  </NeonButton>
                </div>
              ) : (
                <NeonButton
                  variant="green"
                  className="w-full"
                  onClick={proximoEvento ? handleAvancarMomento : handleAvancarFase}
                  blink={avancar}
                >
                  {avancar ? 'AVANÇANDO...' : proximoEvento ? 'AVANÇAR ATÉ MATCHDAY' : getProximaFaseLabel()}
                </NeonButton>
              )}
              <NeonButton
                variant="pink"
                className="w-full"
                onClick={() => setConfirmDesistir(true)}
              >
                DESISTIR
              </NeonButton>
            </div>
          )}
        </ActionDock>
      )}

      {confirmDesistir && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-sm border-2 border-neon-pink bg-[#0d0006] p-5 shadow-[0_0_24px_rgba(255,0,85,0.25)]">
            <div className="arcade-font text-[10px] tracking-[0.2em] text-neon-pink mb-3">
              CONFIRMAR DESISTÊNCIA
            </div>
            <div className="pixel-font text-sm text-white mb-2">
              Tem certeza que deseja desistir?
            </div>
            <div className="arcade-font text-[10px] text-[#9b6677] leading-relaxed mb-5">
              Você perderá os pontos desta fase. O torneio continuará sem você.
            </div>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setConfirmDesistir(false)}
                className="min-h-[44px] border-2 border-[#555] px-4 py-3 arcade-font text-[10px] text-[#aaa]"
              >
                CANCELAR
              </button>
              <button
                type="button"
                onClick={() => {
                  setConfirmDesistir(false)
                  handleDesistir()
                }}
                className="min-h-[44px] border-2 border-neon-pink px-4 py-3 arcade-font text-[10px] text-[#ff7d9e]"
              >
                DESISTIR
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
