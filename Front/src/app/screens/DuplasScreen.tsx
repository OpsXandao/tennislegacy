import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router'
import { Search, TrendingUp, Star, UserCheck, Users, X } from 'lucide-react'
import { motion, AnimatePresence } from 'motion/react'
import { ActionDock, ArcadeTab, NeonButton, NeonCard, PixelFlag, PageHeader, ScreenSection } from '../components'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'
import { getOverallTierLabel } from '../utils/playerRatings'
import type { RankingEntry } from '../../types'

function OvrBadge({ ovr }: { ovr: number }) {
  const color = ovr >= 85 ? 'var(--neon-yellow)' : ovr >= 75 ? 'var(--neon-cyan)' : ovr >= 65 ? 'var(--neon-green)' : '#7a8fa0'
  return (
    <div className="flex flex-col items-center justify-center border-2 w-10 h-10 shrink-0" style={{ borderColor: color }}>
      <span className="arcade-font text-[7px] text-[#6e8fa5]">OVR</span>
      <span className="pixel-font text-[12px] leading-none" style={{ color }}>{ovr}</span>
    </div>
  )
}

function DuplasBadge({ duplas }: { duplas?: number }) {
  if (!duplas || duplas < 70) return null
  return (
    <span className="border border-neon-yellow/40 px-1.5 py-0.5 arcade-font text-[7px] text-neon-yellow">
      DUP {duplas}
    </span>
  )
}

const TABS = ['SUGESTOES', 'BUSCAR', 'RANKING']

interface Parceiro {
  nome: string
  nacionalidade: string
  overall: number
  duplas?: number
  posicao?: number
  estilo_jogo?: string
  ranking_duplas?: number | null
  ranking_simples?: number | null
  ranking_combinado?: number
  perfil_parceria?: { status: string; partidas: number; vitorias: number; win_rate: number; skill_duplas: number }
  disponibilidade?: { status: string; motivo: string; score: number }
  formato_duplas?: { sets: string; no_ad: boolean; match_tiebreak: boolean; terceiro_set: string }
  vinculo?: { partidas: number; vitorias: number } | null
}

// ... rest of interfaces

function getChemistryInfo(parceiro: Parceiro): { label: string; color: string; percent: number } {
  const partidas = parceiro.vinculo?.partidas ?? 0
  if (partidas >= 20) return { label: 'TELEPÁTICA', color: 'var(--neon-gold)', percent: 100 }
  if (partidas >= 10) return { label: 'SINCRONIZADA', color: 'var(--neon-cyan)', percent: 75 }
  if (partidas >= 5) return { label: 'ENTROSADA', color: 'var(--neon-green)', percent: 50 }
  if (partidas >= 1) return { label: 'FAMILIAR', color: 'var(--neon-yellow)', percent: 25 }
  return { label: 'PROFISSIONAL', color: '#666', percent: 5 }
}

function TacticalSynergy({ estilo1, estilo2 }: { estilo1?: string; estilo2?: string }) {
  if (!estilo1 || !estilo2) return null
  
  let label = ''
  if ((estilo1.includes('Baseline') && estilo2.includes('Serve & Voleio')) || (estilo2.includes('Baseline') && estilo1.includes('Serve & Voleio'))) {
    label = 'DUO CLÁSSICO (FUNDO + REDE)'
  } else if (estilo1.includes('Agressivo') && estilo2.includes('Agressivo')) {
    label = 'POWERHOUSE (ATAQUE TOTAL)'
  } else if (estilo1.includes('Baseline') && estilo2.includes('Baseline')) {
    label = 'THE WALL (CONSISTÊNCIA)'
  }
  
  if (!label) return null
  
  return (
    <div className="mt-2 flex items-center gap-1.5 border border-neon-cyan/20 bg-neon-cyan/5 px-2 py-1">
      <TrendingUp size={10} className="text-neon-cyan" />
      <span className="arcade-font text-[7px] text-neon-cyan tracking-wider">{label}</span>
    </div>
  )
}

function availabilityColor(status?: string) {
  if (status === 'alta' || status === 'aberta') return 'var(--neon-green)'
  if (status === 'media') return 'var(--neon-yellow)'
  if (status === 'baixa' || status === 'duvida') return 'var(--neon-pink)'
  if (status === 'indisponivel') return '#777'
  return '#888'
}

function ParceiroCarta({
  parceiro,
  meuEstilo,
  onConvidar,
  convidando,
}: {
  parceiro: Parceiro
  meuEstilo?: string
  onConvidar: (nome: string) => void
  convidando: string | null
}) {
  const chem = getChemistryInfo(parceiro)
  const temHistorico = parceiro.vinculo && parceiro.vinculo.partidas > 0
  const destaqueDuplas = Number(parceiro.duplas ?? 0) >= 88
  const tier = getOverallTierLabel(parceiro.overall, parceiro.posicao)

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={`border-2 p-3 bg-[#1a1a2e] relative overflow-hidden ${
        destaqueDuplas
          ? 'border-[#f6c453]'
          : temHistorico
          ? 'border-neon-yellow/80'
          : 'border-neon-cyan/30'
      }`}
      style={{
        boxShadow: destaqueDuplas
          ? '0 0 14px rgba(246,196,83,0.22)'
          : temHistorico
          ? '0 0 10px rgba(255,230,0,0.15)'
          : '0 0 6px rgba(0,229,255,0.1)',
      }}
    >
      {/* Chemistry Progress Bar (Top edge) */}
      {temHistorico && (
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-[#111]">
          <motion.div 
            initial={{ width: 0 }} 
            animate={{ width: `${chem.percent}%` }} 
            className="h-full" 
            style={{ background: chem.color }} 
          />
        </div>
      )}

      <div className="flex items-center gap-3">
        <OvrBadge ovr={parceiro.overall} />

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <PixelFlag countryCode={parceiro.nacionalidade} size="sm" />
            <span
              className="text-[11px] text-white truncate"
              style={{ fontFamily: 'var(--font-arcade)' }}
            >
              {parceiro.nome}
            </span>
            {temHistorico && (
              <span 
                className="text-[6px] px-1 border border-current arcade-font" 
                style={{ color: chem.color }}
              >
                {chem.label}
              </span>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-2 text-[8px] text-[#888]">
            {parceiro.posicao && <span>D#{parceiro.posicao}</span>}
            {parceiro.ranking_simples && <span>S#{parceiro.ranking_simples}</span>}
            <span className="text-[#8ca8b9]">{tier}</span>
            {typeof parceiro.ranking_combinado === 'number' && (
              <span className="text-neon-cyan">COMB {parceiro.ranking_combinado}</span>
            )}
            {parceiro.vinculo && parceiro.vinculo.partidas > 0 && (
              <span className="text-[#888]">
                {parceiro.vinculo.vitorias}V/{parceiro.vinculo.partidas - parceiro.vinculo.vitorias}L
              </span>
            )}
          </div>

          <div className="mt-1 flex flex-wrap gap-1.5">
            {parceiro.disponibilidade && (
              <span
                className="border px-1.5 py-0.5 arcade-font text-[7px]"
                style={{ color: availabilityColor(parceiro.disponibilidade.status), borderColor: availabilityColor(parceiro.disponibilidade.status) }}
              >
                {parceiro.disponibilidade.status.toUpperCase()}
              </span>
            )}
            {parceiro.perfil_parceria && (
              <span className="border border-neon-cyan/40 px-1.5 py-0.5 arcade-font text-[7px] text-neon-cyan">
                {parceiro.perfil_parceria.status.toUpperCase()} • SKILL {parceiro.perfil_parceria.skill_duplas}
              </span>
            )}
            {parceiro.formato_duplas && (
              <span className="border border-neon-yellow/40 px-1.5 py-0.5 arcade-font text-[7px] text-neon-yellow">
                {parceiro.formato_duplas.no_ad ? 'NO-AD' : 'DEUCE'} • {parceiro.formato_duplas.match_tiebreak ? 'MTB' : '3º SET'}
              </span>
            )}
          </div>
          
          <TacticalSynergy estilo1={meuEstilo} estilo2={parceiro.estilo_jogo} />
          
          <div className="mt-1">
            <DuplasBadge duplas={parceiro.duplas} />
          </div>
        </div>

        <button
          onClick={() => onConvidar(parceiro.nome)}
          disabled={convidando === parceiro.nome}
          className="border-2 border-neon-green bg-black px-3 py-1.5 text-[8px] text-neon-green shrink-0 transition-all enabled:hover:bg-neon-green enabled:hover:text-black disabled:opacity-40"
          style={{ fontFamily: 'var(--font-arcade)' }}
        >
          {convidando === parceiro.nome ? '...' : 'CONVIDAR'}
        </button>
      </div>
    </motion.div>
  )
}

export function DuplasScreen() {
  const navigate = useNavigate()
  const { jogador } = useGameStore()

  const [activeTab, setActiveTab] = useState(0)
  const [sugestoes, setSugestoes] = useState<Parceiro[]>([])
  const [buscaResultados, setBuscaResultados] = useState<Parceiro[]>([])
  const [ranking, setRanking] = useState<RankingEntry[]>([])
  const [loadingSug, setLoadingSug] = useState(true)
  const [loadingBusca, setLoadingBusca] = useState(false)
  const [loadingRk, setLoadingRk] = useState(false)
  const [rankingTotal, setRankingTotal] = useState(0)
  const [convidando, setConvidando] = useState<string | null>(null)
  const [mensagem, setMensagem] = useState<{ texto: string; ok: boolean } | null>(null)
  const [query, setQuery] = useState('')
  const [rankLoaded, setRankLoaded] = useState(false)

  const tour = jogador?.tour ?? 'atp'

  useEffect(() => {
    api.duplas
      .sugestoes()
      .then((r) => setSugestoes(r.parceiros))
      .finally(() => setLoadingSug(false))
  }, [])

  useEffect(() => {
    if (activeTab === 2 && !rankLoaded) {
      setLoadingRk(true)
      api.ranking
        .duplas(tour, 50)
        .then((r) => {
          setRanking(r.ranking)
          setRankingTotal(r.total)
        })
        .finally(() => {
          setLoadingRk(false)
          setRankLoaded(true)
        })
    }
  }, [activeTab, rankLoaded, tour])

  async function handleBuscar() {
    if (!query.trim()) return
    setLoadingBusca(true)
    setBuscaResultados([])
    try {
      const r = await api.duplas.buscar({ nome: query.trim() })
      setBuscaResultados(r.parceiros)
    } finally {
      setLoadingBusca(false)
    }
  }

  async function handleConvidar(nome: string) {
    setConvidando(nome)
    setMensagem(null)
    try {
      const r = await api.duplas.convidar(nome, tour === 'wta' ? 'WTA 250' : 'ATP 250')
      setMensagem({ texto: r.mensagem, ok: r.ok })
    } catch (e: any) {
      setMensagem({ texto: e.message, ok: false })
    } finally {
      setConvidando(null)
    }
  }

  const historico = sugestoes.filter((p) => p.vinculo && p.vinculo.partidas > 0)
  const novos = sugestoes.filter((p) => !p.vinculo || p.vinculo.partidas === 0)

  return (
    <div className="app-shell min-h-screen font-mono pb-24">
      <PageHeader title="HUB DE DUPLAS" color="cyan" backTo="/hub">
        <ArcadeTab tabs={TABS} activeTab={activeTab} onChange={setActiveTab} color="cyan" />
      </PageHeader>

      <AnimatePresence>
        {mensagem && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className={`mx-4 mt-4 border-2 p-3 text-center text-[10px] flex items-center justify-between gap-2 ${
              mensagem.ok
                ? 'border-neon-green bg-neon-green/10 text-neon-green'
                : 'border-neon-pink bg-neon-pink/10 text-neon-pink'
            }`}
            style={{ fontFamily: 'var(--font-arcade)' }}
          >
            <span>{mensagem.texto.toUpperCase()}</span>
            <button onClick={() => setMensagem(null)}>
              <X size={14} />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="p-4">
        {activeTab === 0 && (
          <ScreenSection title="PARCEIROS DISPONIVEIS" subtitle="Sugestoes do backend e historico de parceria" variant="cyan">
          <div className="space-y-4">
            {loadingSug ? (
              <div className="py-16 text-center pixel-font text-sm text-neon-cyan animate-pulse">
                CARREGANDO...
              </div>
            ) : (
              <>
                {historico.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <Star size={12} className="text-neon-yellow" fill="var(--neon-yellow)" />
                      <span
                        className="text-[9px] text-neon-yellow"
                        style={{ fontFamily: 'var(--font-arcade)' }}
                      >
                        PARCEIROS ANTERIORES
                      </span>
                    </div>
                    <div className="space-y-2">
                      {historico.map((p) => (
                        <ParceiroCarta
                          key={p.nome}
                          parceiro={p}
                          meuEstilo={jogador?.estilo_jogo}
                          onConvidar={handleConvidar}
                          convidando={convidando}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {novos.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <Users size={12} className="text-neon-cyan" />
                      <span
                        className="text-[9px] text-neon-cyan"
                        style={{ fontFamily: 'var(--font-arcade)' }}
                      >
                        NOVOS CANDIDATOS
                      </span>
                    </div>
                    <div className="space-y-2">
                      {novos.map((p) => (
                        <ParceiroCarta
                          key={p.nome}
                          parceiro={p}
                          meuEstilo={jogador?.estilo_jogo}
                          onConvidar={handleConvidar}
                          convidando={convidando}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {sugestoes.length === 0 && (
                  <NeonCard variant="cyan" hover={false}>
                    <div className="py-6 text-center">
                      <UserCheck size={32} className="mx-auto mb-3 text-neon-cyan opacity-40" />
                      <div
                        className="text-[10px] text-[#888]"
                        style={{ fontFamily: 'var(--font-arcade)' }}
                      >
                        NENHUM PARCEIRO DISPONIVEL
                      </div>
                    </div>
                  </NeonCard>
                )}
              </>
            )}
          </div>
          </ScreenSection>
        )}

        {activeTab === 1 && (
          <ScreenSection title="BUSCAR PARCEIRO" subtitle="Consulta manual por nome" variant="green">
          <div className="space-y-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleBuscar()}
                placeholder="Nome do jogador..."
                className="flex-1 border-2 border-neon-cyan bg-black px-3 py-2 text-[11px] text-white outline-none placeholder:text-[#444]"
                style={{ fontFamily: 'var(--font-arcade)' }}
              />
              <button
                onClick={handleBuscar}
                disabled={loadingBusca}
                className="border-2 border-neon-cyan bg-black px-4 text-neon-cyan transition-all hover:bg-neon-cyan hover:text-black disabled:opacity-40"
              >
                <Search size={16} />
              </button>
            </div>

            {loadingBusca && (
              <div className="py-8 text-center pixel-font text-sm text-neon-cyan animate-pulse">
                BUSCANDO...
              </div>
            )}

            <div className="space-y-2">
              {buscaResultados.map((p) => (
                <ParceiroCarta
                  key={p.nome}
                  parceiro={p}
                  meuEstilo={jogador?.estilo_jogo}
                  onConvidar={handleConvidar}
                  convidando={convidando}
                />
              ))}
              {!loadingBusca && buscaResultados.length === 0 && query && (
                <div
                  className="border border-[#333] p-6 text-center text-[10px] text-[#666]"
                  style={{ fontFamily: 'var(--font-arcade)' }}
                >
                  NENHUM RESULTADO PARA "{query.toUpperCase()}"
                </div>
              )}
            </div>
          </div>
          </ScreenSection>
        )}

        {activeTab === 2 && (
          <ScreenSection title={`RANKING DUPLAS ${tour.toUpperCase()}`} subtitle="Top 50 sincronizado com a API" variant="yellow">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp size={14} className="text-neon-green" />
              <span
                className="text-[9px] text-neon-green"
                style={{ fontFamily: 'var(--font-arcade)' }}
              >
                RANKING DUPLAS {tour.toUpperCase()} {rankingTotal > 0 ? `• ${rankingTotal} JOGADORES` : ''}
              </span>
            </div>

            {loadingRk ? (
              <div className="py-16 text-center pixel-font text-sm text-neon-green animate-pulse">
                CARREGANDO...
              </div>
            ) : (
              <div className="space-y-1">
                {ranking.map((entry, i) => {
                  const isMeu =
                    entry.nome.toLowerCase() === (jogador?.nome ?? '').toLowerCase()
                  return (
                    <motion.div
                      key={entry.nome}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.02 }}
                      className={`flex items-center gap-3 border px-3 py-2 ${
                        isMeu
                          ? 'border-neon-yellow bg-neon-yellow/10'
                          : 'border-[#1a1a2e] bg-[#1a1a2e]'
                      }`}
                    >
                      <span
                        className={`w-6 text-[10px] text-right ${
                          i < 3 ? 'text-neon-yellow' : 'text-[#666]'
                        }`}
                        style={{ fontFamily: 'var(--font-arcade)' }}
                      >
                        {entry.posicao}
                      </span>
                      <PixelFlag countryCode={entry.nacionalidade} size="sm" />
                      <span
                        className={`flex-1 text-[10px] truncate ${
                          isMeu ? 'text-neon-yellow' : 'text-white'
                        }`}
                        style={{ fontFamily: 'var(--font-arcade)' }}
                      >
                        {entry.nome}
                      </span>
                      <span className="text-[9px] text-neon-green" style={{ fontFamily: 'var(--font-arcade)' }}>
                        {(entry.pontos ?? 0).toLocaleString()}
                      </span>
                    </motion.div>
                  )
                })}
                {ranking.length === 0 && (
                  <div
                    className="border border-[#333] p-6 text-center text-[10px] text-[#666]"
                    style={{ fontFamily: 'var(--font-arcade)' }}
                  >
                    NENHUMA ENTRADA NO RANKING DE DUPLAS
                  </div>
                )}
              </div>
            )}
          </div>
          </ScreenSection>
        )}
      </div>

      <ActionDock>
        <NeonButton
          variant="cyan"
          className="w-full"
          onClick={() => navigate('/calendar')}
        >
          IR PARA CALENDARIO E INSCREVER EM DUPLAS
        </NeonButton>
      </ActionDock>
    </div>
  )
}
