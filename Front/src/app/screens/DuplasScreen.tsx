import { useState, useEffect } from 'react'
import { Search, TrendingUp, Star, UserCheck, Users, X } from 'lucide-react'
import { motion, AnimatePresence } from 'motion/react'
import { ActionDock, ArcadeTab, NeonButton, NeonCard, PixelFlag, PageHeader, ScreenSection } from '../components'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'
import { getOverallTierLabel } from '../utils/playerRatings'

const TABS = ['SUGESTOES', 'BUSCAR', 'RANKING']

interface Parceiro {
  nome: string
  nacionalidade: string
  overall: number
  duplas?: number
  posicao?: number
  vinculo?: { partidas: number; vitorias: number } | null
}

interface RankingEntry {
  posicao: number
  nome: string
  nacionalidade: string
  pontos: number
}

function calcSinergia(vinculo?: Parceiro['vinculo']): string {
  if (!vinculo || vinculo.partidas === 0) return ''
  const wr = vinculo.partidas > 0 ? vinculo.vitorias / vinculo.partidas : 0
  if (wr >= 0.6 && vinculo.partidas >= 5) return 'PARCERIA ELITE'
  if (vinculo.partidas >= 5) return 'PARCERIA SOLIDA'
  if (vinculo.partidas >= 1) return 'JA JOGARAM'
  return ''
}

function OvrBadge({ ovr }: { ovr: number }) {
  const color = ovr >= 80 ? '#ffe600' : ovr >= 65 ? '#00ff88' : '#00e5ff'
  return (
    <div
      className="flex items-center justify-center w-10 h-10 border-2 text-sm font-bold shrink-0"
      style={{ borderColor: color, color, fontFamily: 'var(--font-arcade)' }}
    >
      {ovr}
    </div>
  )
}

function DuplasBadge({ duplas }: { duplas?: number }) {
  if (!duplas || duplas < 80) return null
  return (
    <div
      className="border px-1.5 py-0.5 text-[7px]"
      style={{
        borderColor: '#f6c453',
        color: '#f6c453',
        background: 'rgba(246, 196, 83, 0.1)',
        fontFamily: 'var(--font-arcade)',
      }}
    >
      DUPLAS PRO {duplas}
    </div>
  )
}

function ParceiroCarta({
  parceiro,
  onConvidar,
  convidando,
}: {
  parceiro: Parceiro
  onConvidar: (nome: string) => void
  convidando: string | null
}) {
  const sinergia = calcSinergia(parceiro.vinculo)
  const temHistorico = parceiro.vinculo && parceiro.vinculo.partidas > 0
  const destaqueDuplas = Number(parceiro.duplas ?? 0) >= 88
  const tier = getOverallTierLabel(parceiro.overall, parceiro.posicao)

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={`border-2 p-3 bg-[#1a1a2e] ${
        destaqueDuplas
          ? 'border-[#f6c453]'
          : temHistorico
          ? 'border-[#ffe600]/80'
          : 'border-[#00e5ff]/30'
      }`}
      style={{
        boxShadow: destaqueDuplas
          ? '0 0 14px rgba(246,196,83,0.22)'
          : temHistorico
          ? '0 0 10px rgba(255,230,0,0.15)'
          : '0 0 6px rgba(0,229,255,0.1)',
        background: destaqueDuplas
          ? 'linear-gradient(180deg, rgba(246,196,83,0.12) 0%, #1a1a2e 100%)'
          : undefined,
      }}
    >
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
            {temHistorico && <Star size={10} className="text-[#ffe600] shrink-0" fill="#ffe600" />}
          </div>

          <div className="flex items-center gap-2 text-[8px] text-[#888]">
            {parceiro.posicao && <span>#{parceiro.posicao}</span>}
            <span className="text-[#8ca8b9]">{tier}</span>
            {sinergia && (
              <span
                className="px-1.5 py-0.5 border text-[7px]"
                style={{
                  borderColor: '#ffe600',
                  color: '#ffe600',
                  fontFamily: 'var(--font-arcade)',
                }}
              >
                {sinergia}
              </span>
            )}
            {parceiro.vinculo && parceiro.vinculo.partidas > 0 && (
              <span className="text-[#888]">
                {parceiro.vinculo.vitorias}W/{parceiro.vinculo.partidas - parceiro.vinculo.vitorias}L
              </span>
            )}
          </div>
          <div className="mt-1">
            <DuplasBadge duplas={parceiro.duplas} />
          </div>
        </div>

        <button
          onClick={() => onConvidar(parceiro.nome)}
          disabled={convidando === parceiro.nome}
          className="border-2 border-[#00ff88] bg-black px-3 py-1.5 text-[8px] text-[#00ff88] shrink-0 transition-all enabled:hover:bg-[#00ff88] enabled:hover:text-black disabled:opacity-40"
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
      const r = await api.duplas.convidar(nome, 'ATP 250')
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
                ? 'border-[#00ff88] bg-[#00ff88]/10 text-[#00ff88]'
                : 'border-[#ff0055] bg-[#ff0055]/10 text-[#ff0055]'
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
              <div className="py-16 text-center pixel-font text-sm text-[#00e5ff] animate-pulse">
                CARREGANDO...
              </div>
            ) : (
              <>
                {historico.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <Star size={12} className="text-[#ffe600]" fill="#ffe600" />
                      <span
                        className="text-[9px] text-[#ffe600]"
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
                      <Users size={12} className="text-[#00e5ff]" />
                      <span
                        className="text-[9px] text-[#00e5ff]"
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
                      <UserCheck size={32} className="mx-auto mb-3 text-[#00e5ff] opacity-40" />
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
                className="flex-1 border-2 border-[#00e5ff] bg-black px-3 py-2 text-[11px] text-white outline-none placeholder:text-[#444]"
                style={{ fontFamily: 'var(--font-arcade)' }}
              />
              <button
                onClick={handleBuscar}
                disabled={loadingBusca}
                className="border-2 border-[#00e5ff] bg-black px-4 text-[#00e5ff] transition-all hover:bg-[#00e5ff] hover:text-black disabled:opacity-40"
              >
                <Search size={16} />
              </button>
            </div>

            {loadingBusca && (
              <div className="py-8 text-center pixel-font text-sm text-[#00e5ff] animate-pulse">
                BUSCANDO...
              </div>
            )}

            <div className="space-y-2">
              {buscaResultados.map((p) => (
                <ParceiroCarta
                  key={p.nome}
                  parceiro={p}
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
              <TrendingUp size={14} className="text-[#00ff88]" />
              <span
                className="text-[9px] text-[#00ff88]"
                style={{ fontFamily: 'var(--font-arcade)' }}
              >
                RANKING DUPLAS {tour.toUpperCase()} {rankingTotal > 0 ? `• ${rankingTotal} JOGADORES` : ''}
              </span>
            </div>

            {loadingRk ? (
              <div className="py-16 text-center pixel-font text-sm text-[#00ff88] animate-pulse">
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
                          ? 'border-[#ffe600] bg-[#ffe600]/10'
                          : 'border-[#1a1a2e] bg-[#1a1a2e]'
                      }`}
                    >
                      <span
                        className={`w-6 text-[10px] text-right ${
                          i < 3 ? 'text-[#ffe600]' : 'text-[#666]'
                        }`}
                        style={{ fontFamily: 'var(--font-arcade)' }}
                      >
                        {entry.posicao}
                      </span>
                      <PixelFlag countryCode={entry.nacionalidade} size="sm" />
                      <span
                        className={`flex-1 text-[10px] truncate ${
                          isMeu ? 'text-[#ffe600]' : 'text-white'
                        }`}
                        style={{ fontFamily: 'var(--font-arcade)' }}
                      >
                        {entry.nome}
                      </span>
                      <span className="text-[9px] text-[#00ff88]" style={{ fontFamily: 'var(--font-arcade)' }}>
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
