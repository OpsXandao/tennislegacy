import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router'
import { Mail, Trash2, Check, X, Trophy } from 'lucide-react'
import { ArcadeTab, NeonCard, PixelFlag, NeonButton, PageHeader } from '../components'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'
import type { MembroEquipe, Patrocinio, Transaction, MatchHistoryEntry, RankingDetalhado } from '../../types'
import { getDuplasRating, getOverallTierLabel, isDoublesSpecialist } from '../utils/playerRatings'
import { FormaTab } from './player/FormaTab'

const TABS = ['ATRIBUTOS', 'RANKING', 'HISTÓRICO', 'FORMA', 'FINANCEIRO', 'CARREIRA', 'EQUIPE', 'EMAIL']

const ATRIB_TECNICOS: [string, string][] = [
  ['saque', 'SAQUE'],
  ['forehand', 'FOREHAND'],
  ['backhand', 'BACKHAND'],
  ['voleio', 'VOLEIO'],
  ['topspin', 'TOPSPIN'],
  ['slice', 'SLICE'],
  ['lob', 'LOB'],
  ['winner', 'WINNER'],
]

const ATRIB_FISICOS: [string, string][] = [
  ['movimento', 'MOVIMENTO'],
  ['fisico', 'FÍSICO'],
]

const ATRIB_MENTAIS: [string, string][] = [
  ['concentracao', 'CONCENTRAÇÃO'],
  ['agressividade', 'AGRESSIVIDADE'],
  ['leitura_de_jogo', 'LEIT. JOGO'],
  ['determinacao', 'DETERMINAÇÃO'],
]

const FASE_LABEL: Record<string, string> = {
  campeao: 'CAMPEÃO', final: 'FINAL', semifinal: 'SEMIFINAL', semis: 'SEMIFINAL',
  quartas: 'QUARTAS', qf: 'QUARTAS', oitavas: 'OITAVAS', r16: 'OITAVAS',
  r32: 'R32', r64: 'R64', r128: 'R128', qualy_1: 'QUALY', qualy_2: 'QUALY',
}

function fmt(v: number) {
  if (v >= 1_000_000) return `$${(v / 1_000_000).toFixed(1)}M`
  if (v >= 1_000) return `$${(v / 1_000).toFixed(0)}K`
  return `$${v}`
}

function faseLabel(f: string) {
  return FASE_LABEL[f?.toLowerCase()] ?? f?.toUpperCase() ?? '?'
}

function historicoFoiVitoria(resultado: string | undefined) {
  const valor = String(resultado || '').trim().toUpperCase()
  return valor === 'V' || valor === 'VITORIA' || valor === 'VITÓRIA'
}

export function PlayerScreen() {
  const navigate = useNavigate()
  const location = useLocation()
  const { jogador, setJogador } = useGameStore()
  
  const initialTab = location.state?.tab !== undefined ? location.state.tab : 0
  const [activeTab, setActiveTab] = useState(initialTab)

  const [atributos, setAtributos] = useState<Record<string, number>>({})
  const [overall, setOverall] = useState(0)
  const [equipe, setEquipe] = useState<{
    treinador: MembroEquipe | null; fisio: MembroEquipe | null
    psicologo: MembroEquipe | null; empresario: MembroEquipe | null
  } | null>(null)
  const [emails, setEmails] = useState<any[]>([])
  const [meusTitulos, setMeusTitulos] = useState<any[]>([])
  const [rankingDet, setRankingDet] = useState<RankingDetalhado | null>(null)
  const [historico, setHistorico] = useState<MatchHistoryEntry[]>([])
  const [financeiro, setFinanceiro] = useState<{
    saldo: number; transacoes: Transaction[]; resumo_categorias: Record<string, number>
  } | null>(null)
  const [carreira, setCarreira] = useState<any | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false) // Audit: add error state
  const [processandoEmail, setProcessandoEmail] = useState<string | null>(null)

  const carregarDados = async () => {
    setLoading(true)
    setError(false)
    try {
      const [j, a, e, em, hist, rk, hp, fin, car] = await Promise.all([
        api.jogador.get(),
        api.jogador.atributos(),
        api.jogador.equipe(),
        api.email.inbox(),
        api.historico.goat(),
        api.jogador.rankingDetalhado(),
        api.jogador.historicoPartidas(),
        api.jogador.financeiro(),
        api.jogador.carreira(),
      ])
      
      setJogador(j)
      setAtributos(a.atributos)
      setOverall(a.overall)
      setEquipe(e)
      setEmails(em.emails)
      setMeusTitulos(hist.meus_titulos || [])
      setRankingDet(rk)
      setHistorico(hp.historico || [])
      setFinanceiro(fin)
      setCarreira(car)
      
      // Audit: marcar como lidos silenciosamente
      api.email.marcarLidos().catch(() => {})
    } catch (err) {
      console.error('Erro ao carregar dados do jogador:', err)
      setError(true)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { carregarDados() }, [])

  async function handleEmailAcao(id: string, acao: 'aceitar' | 'recusar' | 'deletar') {
    setProcessandoEmail(id)
    try {
      const res = await api.email.acao(id, acao)
      if (res.ok) carregarDados()
    } catch (e: any) {
      alert(e.message)
    } finally {
      setProcessandoEmail(null)
    }
  }

  const nome   = jogador?.nome ?? '...'
  const rank   = jogador?.ranking ?? '?'
  const money  = jogador?.dinheiro ?? 0
  const titulo = jogador?.tour?.toUpperCase() ?? 'ATP'
  const atributosMentais = jogador?.atributos_psicologicos ?? {}
  const duplas = getDuplasRating(atributos)
  const tier = getOverallTierLabel(overall, typeof rank === 'number' ? rank : null)
  const especialistaDuplas = isDoublesSpecialist(atributos)
  const carta = jogador?.carta ?? null
  const identity = jogador?.identity ?? null

  const sumarioTitulos = {
    GS: meusTitulos.filter(t => t.tipo === 'Grand Slam').length,
    M1000: meusTitulos.filter(t => t.tipo?.includes('1000')).length,
    Total: meusTitulos.length,
  }

  return (
    <div className="app-shell app-player-screen min-h-screen">
      <PageHeader title="PERFIL DO ATLETA" color="green" backTo="/hub">
        <ArcadeTab tabs={TABS} activeTab={activeTab} onChange={setActiveTab} color="green" />
      </PageHeader>

      <div className="p-4 space-y-4 pb-24 overflow-y-auto">

        {/* Header card */}
        <NeonCard variant="green" hover={false}>
          <div className="flex flex-col items-center gap-3">
            <div className="w-20 h-20 bg-black border-4 border-[#00ff88] flex items-center justify-center relative">
              <div className="text-4xl">🎾</div>
              {emails.filter(e => e.status === 'pendente').length > 0 && (
                <div className="absolute -top-2 -right-2 bg-[#ff0055] text-white pixel-font text-[10px] w-6 h-6 flex items-center justify-center rounded-full animate-bounce border-2 border-white">
                  {emails.filter(e => e.status === 'pendente').length}
                </div>
              )}
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-1">
                <PixelFlag countryCode={jogador?.nacionalidade} size="md" />
                <h3 className="pixel-font text-lg text-[#00ff88]">{nome}</h3>
              </div>
              <div className="arcade-font text-[10px] text-[#888]">{titulo} WORLD TOUR</div>
              <div className="mt-2 flex items-center justify-center gap-2 flex-wrap">
                <span className="border border-[#00ff88] px-2 py-1 text-[8px] arcade-font text-[#00ff88]">{tier}</span>
                {carta && !['gold', 'silver', 'bronze'].includes(carta.tipo) && (
                  <span
                    className="border px-2 py-1 text-[8px] arcade-font"
                    style={{ borderColor: carta.cor_primaria, color: carta.cor_primaria }}
                  >
                    {carta.label}
                  </span>
                )}
                {duplas > 0 && (
                  <span className={`border px-2 py-1 text-[8px] arcade-font ${especialistaDuplas ? 'border-[#f6c453] text-[#f6c453]' : 'border-[#335264] text-[#8ca8b9]'}`}>
                    DUPLAS {duplas}
                  </span>
                )}
                {identity && (
                  <>
                    <span className="border border-[#00e5ff] px-2 py-1 text-[8px] arcade-font text-[#00e5ff]">{identity.role.label}</span>
                    <span className="border border-white/20 px-2 py-1 text-[8px] arcade-font text-white/80">{identity.body_type.label}</span>
                  </>
                )}
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3 w-full text-center">
              <div>
                <div className="text-xl text-[#ffe600] pixel-font">#{rank}</div>
                <div className="text-[8px] text-[#888] arcade-font">RANK</div>
              </div>
              <div>
                <div className="text-xl text-[#00e5ff] pixel-font">{fmt(money)}</div>
                <div className="text-[8px] text-[#888] arcade-font">CAIXA</div>
              </div>
              <div>
                <div
                  className="text-xl pixel-font"
                  style={{ color: carta?.cor_primaria ?? '#00ff88' }}
                >
                  {overall || '?'}
                </div>
                {carta && Object.keys(carta.bonus).length > 0 && (
                  <div className="text-[7px] arcade-font" style={{ color: '#00FF88' }}>
                    {carta.label}
                  </div>
                )}
                <div className="text-[8px] text-[#888] arcade-font">OVR</div>
              </div>
            </div>
            {identity && (
              <div className="w-full border border-white/10 bg-black/20 px-3 py-3">
                <div className="arcade-font text-[8px] text-[#8ca8b9]">PLAYSTYLES</div>
                <div className="mt-2 flex flex-wrap justify-center gap-2">
                  {identity.playstyles.slice(0, 4).map((playstyle) => (
                    <span
                      key={playstyle.id}
                      className="border px-2 py-1 text-[8px] arcade-font"
                      style={{
                        borderColor: playstyle.tier === 'plus' ? '#f6c453' : '#00e5ff',
                        color: playstyle.tier === 'plus' ? '#f6c453' : '#00e5ff',
                      }}
                    >
                      {playstyle.label}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </NeonCard>

        {loading && (
          <div className="text-center py-12 pixel-font text-xs text-[#00ff88] animate-pulse">CARREGANDO...</div>
        )}

        {/* TAB 0: ATRIBUTOS */}
        {!loading && activeTab === 0 && (
          <div className="space-y-3">
            <NeonCard variant="cyan" hover={false}>
              <div className="arcade-font text-[9px] text-[#00e5ff] tracking-widest mb-3">TÉCNICOS</div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {ATRIB_TECNICOS.map(([key, label]) =>
                  atributos[key] !== undefined ? (
                    <div key={key} className="border border-[#163041] bg-[#0b1821] px-4 py-3">
                      <div className="arcade-font text-[9px] text-[#8eb5c8] tracking-widest">{label}</div>
                      <div className="pixel-font text-2xl text-[#00e5ff] mt-2">{atributos[key]}</div>
                    </div>
                  ) : null
                )}
              </div>
            </NeonCard>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <NeonCard variant="green" hover={false}>
                <div className="arcade-font text-[9px] text-[#00ff88] tracking-widest mb-3">FÍSICOS</div>
                <div className="grid grid-cols-2 gap-3">
                  {ATRIB_FISICOS.map(([key, label]) =>
                    atributos[key] !== undefined ? (
                      <div key={key} className="border border-[#173520] bg-[#0c160f] px-4 py-3">
                        <div className="arcade-font text-[9px] text-[#9fd8b2] tracking-widest">{label}</div>
                        <div className="pixel-font text-2xl text-[#00ff88] mt-2">{atributos[key]}</div>
                      </div>
                    ) : null
                  )}
                </div>
              </NeonCard>

              <NeonCard variant="yellow" hover={false}>
                <div className="arcade-font text-[9px] text-[#ffe600] tracking-widest mb-3">MENTAIS</div>
                <div className="grid grid-cols-2 gap-3">
                  {ATRIB_MENTAIS.map(([key, label]) =>
                    atributosMentais[key] !== undefined ? (
                      <div key={key} className="border border-[#3a3516] bg-[#171407] px-4 py-3">
                        <div className="arcade-font text-[9px] text-[#d8ca7a] tracking-widest">{label}</div>
                        <div className="pixel-font text-2xl text-[#ffe600] mt-2">{atributosMentais[key]}</div>
                      </div>
                    ) : null
                  )}
                </div>
              </NeonCard>
            </div>
          </div>
        )}

        {/* TAB 1: RANKING */}
        {!loading && activeTab === 1 && rankingDet && (
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div className="border-2 border-[#00ff88] bg-[#111] p-3 text-center">
                <div className="arcade-font text-[8px] text-[#888] mb-1">SIMPLES</div>
                <div className="pixel-font text-2xl text-[#00ff88]">
                  {rankingDet.posicao_simples ? `#${rankingDet.posicao_simples}` : 'N/A'}
                </div>
                <div className="arcade-font text-[9px] text-[#666] mt-1">
                  {rankingDet.pontos_simples.toLocaleString('pt-BR')} pts
                </div>
              </div>
              <div className="border-2 border-[#00e5ff] bg-[#111] p-3 text-center">
                <div className="arcade-font text-[8px] text-[#888] mb-1">DUPLAS</div>
                <div className="pixel-font text-2xl text-[#00e5ff]">
                  {rankingDet.posicao_duplas ? `#${rankingDet.posicao_duplas}` : 'N/A'}
                </div>
                <div className="arcade-font text-[9px] text-[#666] mt-1">
                  {rankingDet.pontos_duplas.toLocaleString('pt-BR')} pts
                </div>
              </div>
            </div>

            {rankingDet.pontos_ytd > 0 && (
              <div className="border border-[#ffe600]/40 bg-[#ffe600]/5 p-3 text-center">
                <div className="arcade-font text-[8px] text-[#888]">RACE TO FINALS (YTD)</div>
                <div className="pixel-font text-xl text-[#ffe600] mt-1">
                  {rankingDet.pontos_ytd.toLocaleString('pt-BR')} pts
                </div>
              </div>
            )}

            {rankingDet.resultados_simples.length > 0 && (
              <div className="border border-[#333] bg-[#111]">
                <div className="border-b border-[#333] px-3 py-2 arcade-font text-[9px] text-[#00ff88]">
                  RESULTADOS SIMPLES (BEST-18)
                </div>
                <div className="divide-y divide-[#1a1a1a]">
                  {rankingDet.resultados_simples.map((r, i) => (
                    <div key={i} className="flex items-center justify-between px-3 py-2">
                      <div className="flex items-center gap-2 min-w-0">
                        <span className="text-[8px] text-[#333] w-4 shrink-0">{i + 1}</span>
                        {r.obrigatorio && <span className="text-[#ffe600] text-[8px] shrink-0">●</span>}
                        <span className="arcade-font text-[9px] text-white truncate">{r.nome}</span>
                      </div>
                      <div className="flex items-center gap-3 shrink-0 ml-2">
                        <span className="arcade-font text-[8px] text-[#666]">{faseLabel(r.fase)}</span>
                        <span className="pixel-font text-[10px] text-[#00ff88] w-10 text-right">{r.pontos}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {rankingDet.resultados_duplas.length > 0 && (
              <div className="border border-[#333] bg-[#111]">
                <div className="border-b border-[#333] px-3 py-2 arcade-font text-[9px] text-[#00e5ff]">
                  RESULTADOS DUPLAS
                </div>
                <div className="divide-y divide-[#1a1a1a]">
                  {rankingDet.resultados_duplas.map((r, i) => (
                    <div key={i} className="flex items-center justify-between px-3 py-2">
                      <div className="flex items-center gap-2 min-w-0">
                        <span className="text-[8px] text-[#333] w-4 shrink-0">{i + 1}</span>
                        <span className="arcade-font text-[9px] text-white truncate">{r.nome}</span>
                      </div>
                      <div className="flex items-center gap-3 shrink-0 ml-2">
                        <span className="arcade-font text-[8px] text-[#666]">{faseLabel(r.fase)}</span>
                        <span className="pixel-font text-[10px] text-[#00e5ff] w-10 text-right">{r.pontos}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="arcade-font text-[8px] text-[#333] text-center">
              ● = torneio obrigatório (Grand Slam / Masters 1000)
            </div>

            <button
              type="button"
              onClick={() => navigate('/ranking-historico')}
              className="w-full border border-[#00ff88]/30 bg-[#060f0a] py-2 arcade-font text-[9px] text-[#00ff88]/60 hover:text-[#00ff88] hover:border-[#00ff88]/60 transition-colors"
            >
              VER HISTÓRICO DE POSIÇÕES →
            </button>
          </div>
        )}

        {/* TAB 2: HISTÓRICO */}
        {!loading && activeTab === 2 && (
          <div className="space-y-2">
            {historico.length === 0 ? (
              <div className="text-center py-12 arcade-font text-[10px] text-[#444]">NENHUMA PARTIDA REGISTRADA</div>
            ) : (
              [...historico].reverse().map((h, i) => (
                <div
                  key={i}
                  className={`border-l-4 bg-[#111] px-3 py-3 ${historicoFoiVitoria(h.resultado) ? 'border-[#00ff88]' : 'border-[#ff0055]'}`}
                >
                  <div className="flex items-center justify-between gap-3 mb-1">
                    <span className="arcade-font text-[11px] text-white truncate max-w-[220px]">{h.adversario}</span>
                    <span className={`pixel-font text-[11px] font-bold ${historicoFoiVitoria(h.resultado) ? 'text-[#00ff88]' : 'text-[#ff0055]'}`}>
                      {historicoFoiVitoria(h.resultado) ? 'VIT' : 'DER'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between gap-3">
                    <span className="arcade-font text-[10px] text-[#7a8c98]">{h.torneio} • {faseLabel(h.fase)}</span>
                    <span className="arcade-font text-[10px] text-[#8f9aa3] text-right">{h.placar}</span>
                  </div>
                  <div className="arcade-font text-[9px] text-[#4a5a64] mt-1">SEM {h.semana} / {h.ano}</div>
                </div>
              ))
            )}
          </div>
        )}

        {/* TAB 3: FORMA */}
        {!loading && activeTab === 3 && <FormaTab />}

        {/* TAB 4: FINANCEIRO */}
        {!loading && activeTab === 4 && financeiro && (
          <div className="space-y-3">
            <div className="border-2 border-[#00ff88] bg-[#111] p-4 text-center">
              <div className="arcade-font text-[8px] text-[#888] mb-1">SALDO ATUAL</div>
              <div className="pixel-font text-3xl text-[#00ff88]">{fmt(financeiro.saldo)}</div>
            </div>

            {Object.keys(financeiro.resumo_categorias).length > 0 && (
              <div className="border border-[#333] bg-[#111]">
                <div className="border-b border-[#333] px-3 py-2 arcade-font text-[9px] text-[#ffe600]">TOTAIS POR CATEGORIA</div>
                <div className="divide-y divide-[#1a1a1a]">
                  {Object.entries(financeiro.resumo_categorias)
                    .sort(([, a], [, b]) => b - a)
                    .map(([cat, total]) => (
                      <div key={cat} className="flex items-center justify-between px-3 py-2">
                        <span className="arcade-font text-[9px] text-[#888] capitalize">{cat}</span>
                        <span className={`pixel-font text-[10px] ${total >= 0 ? 'text-[#00ff88]' : 'text-[#ff0055]'}`}>
                          {total >= 0 ? '+' : ''}{fmt(total)}
                        </span>
                      </div>
                    ))}
                </div>
              </div>
            )}

            <div className="border border-[#333] bg-[#111]">
              <div className="border-b border-[#333] px-3 py-2 arcade-font text-[9px] text-[#00e5ff]">ÚLTIMAS TRANSAÇÕES</div>
              <div className="divide-y divide-[#1a1a1a]">
                {financeiro.transacoes.length === 0 ? (
                  <div className="px-3 py-4 text-center arcade-font text-[9px] text-[#444]">Sem transações</div>
                ) : (
                  [...financeiro.transacoes].reverse().map((t, i) => (
                    <div key={i} className="px-3 py-2">
                      <div className="flex items-center justify-between mb-0.5">
                        <span className="arcade-font text-[9px] text-white truncate max-w-[180px]">{t.descricao}</span>
                        <span className={`pixel-font text-[10px] shrink-0 ml-2 ${t.valor >= 0 ? 'text-[#00ff88]' : 'text-[#ff0055]'}`}>
                          {t.valor >= 0 ? '+' : ''}{fmt(t.valor)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="arcade-font text-[7px] text-[#444]">S{t.semana} • {t.categoria}</span>
                        {t.saldo_pos !== undefined && (
                          <span className="arcade-font text-[7px] text-[#444]">saldo: {fmt(t.saldo_pos)}</span>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: CARREIRA */}
        {!loading && activeTab === 5 && carreira && (
          <div className="space-y-3">
            <div className="border-2 border-[#ffe600] bg-[#111] p-4">
              <div className="grid grid-cols-3 gap-3 text-center mb-4">
                <div>
                  <div className="arcade-font text-[8px] text-[#888]">FASE</div>
                  <div className="arcade-font text-[9px] text-[#ffe600] mt-1">{carreira.fase?.toUpperCase()}</div>
                </div>
                <div>
                  <div className="arcade-font text-[8px] text-[#888]">IDADE</div>
                  <div className="pixel-font text-xl text-white">{carreira.idade}</div>
                </div>
                <div>
                  <div className="arcade-font text-[8px] text-[#888]">PICO</div>
                  <div className="pixel-font text-xl text-[#00ff88]">{carreira.pico_carreira}a</div>
                </div>
              </div>
              <div className="mb-1">
                <div className="flex justify-between arcade-font text-[7px] text-[#333] mb-1">
                  <span>16</span><span>40</span>
                </div>
                <div className="relative h-3 bg-[#222] border border-[#2a2a2a]">
                  <div
                    className="absolute top-0 bottom-0 w-0.5 bg-[#00ff88]"
                    style={{ left: `${Math.min(99, Math.max(1, (carreira.pico_carreira - 16) / 24 * 100))}%` }}
                  />
                  <div
                    className="absolute top-0 bottom-0 w-1 bg-[#ffe600]"
                    style={{ left: `${Math.min(99, Math.max(0, (carreira.idade - 16) / 24 * 100))}%` }}
                  />
                </div>
                <div className="flex justify-between arcade-font text-[7px] mt-1">
                  <span className="text-[#ffe600]">▲ você ({carreira.idade}a)</span>
                  <span className="text-[#00ff88]">| pico ({carreira.pico_carreira}a)</span>
                </div>
              </div>
            </div>

            <div className="border border-[#00ff88]/20 bg-[#111] p-3">
              <div className="flex justify-between arcade-font text-[8px] text-[#888] mb-2">
                <span>NÍVEL {carreira.nivel}</span>
                <span>{carreira.xp} / {carreira.xp_para_proximo} XP</span>
              </div>
              <div className="h-2 bg-[#222]">
                <div
                  className="h-full bg-[#00ff88]"
                  style={{ width: `${Math.min(100, (carreira.xp / Math.max(1, carreira.xp_para_proximo)) * 100)}%` }}
                />
              </div>
            </div>

            <div className="border-2 border-[#ffe600]/30 bg-[#111] p-3">
              <div className="arcade-font text-[9px] text-[#ffe600] mb-3">TÍTULOS ({sumarioTitulos.Total})</div>
              <div className="grid grid-cols-3 gap-2 text-center mb-3">
                {[
                  { label: 'TOTAL', count: sumarioTitulos.Total, color: '#ffe600' },
                  { label: 'SLAMS', count: sumarioTitulos.GS, color: '#00ff88' },
                  { label: 'MASTERS', count: sumarioTitulos.M1000, color: '#00e5ff' },
                ].map(s => (
                  <div key={s.label} className="border border-[#222] py-2">
                    <div className="pixel-font text-xl" style={{ color: s.color }}>{s.count}</div>
                    <div className="arcade-font text-[7px] text-[#666] mt-1">{s.label}</div>
                  </div>
                ))}
              </div>
              {(carreira.titulos || []).slice(-5).reverse().map((t: any, i: number) => (
                <div key={i} className="flex justify-between arcade-font text-[9px] py-1.5 border-t border-[#1a1a1a]">
                  <div className="flex items-center gap-1 min-w-0">
                    <Trophy size={10} className="text-[#ffe600] shrink-0" />
                    <span className="text-white truncate">{t.torneio}</span>
                  </div>
                  <span className="text-[#555] shrink-0 ml-2">{t.ano}</span>
                </div>
              ))}
              {meusTitulos.length > 0 && (
                <button
                  onClick={() => navigate('/history')}
                  className="mt-3 w-full arcade-font text-[9px] text-[#ffe600] border border-[#ffe600]/20 py-2 hover:bg-[#ffe600]/5"
                >
                  VER HISTÓRICO COMPLETO
                </button>
              )}
            </div>
          </div>
        )}

        {/* TAB 6: EQUIPE */}
        {!loading && activeTab === 6 && (
          <div className="space-y-3">
            {[
              ['TÉCNICO', equipe?.treinador, '🏋️'],
              ['FISIOTERAPEUTA', equipe?.fisio, '🩺'],
              ['PSICÓLOGO', equipe?.psicologo, '🧠'],
              ['EMPRESÁRIO', equipe?.empresario, '💼'],
            ].map(([cargo, membro, icon]) => {
              const m = membro as any
              const bonus = m?.bonus ?? {}
              const bonusLines: string[] = []
              if (bonus.bonus_progressao)
                bonusLines.push(`+${Math.round(bonus.bonus_progressao * 100)}% chance de evoluir no treino`)
              if (bonus.bonus_recuperacao)
                bonusLines.push(`+${bonus.bonus_recuperacao} energia recuperada/semana`)
              if (bonus.bonus_xp && bonus.bonus_xp !== 1)
                bonusLines.push(`×${bonus.bonus_xp.toFixed(1)} XP por partida`)
              if (bonus.bonus_mental)
                bonusLines.push(`+${bonus.bonus_mental} em atributos mentais`)
              if (bonus.bonus_fadiga)
                bonusLines.push(`-${bonus.bonus_fadiga}% fadiga acumulada`)
              if (bonus.bonus_fisico_pct)
                bonusLines.push(`+${Math.round(bonus.bonus_fisico_pct * 100)}% atributos físicos`)
              if (bonus.bonus_patrocinio)
                bonusLines.push(`+${Math.round(bonus.bonus_patrocinio * 100)}% valor de patrocínios`)
              return (
                <NeonCard key={cargo as string} variant="green" hover={false}>
                  <div className="flex justify-between items-start">
                    <div className="flex items-start gap-3 flex-1">
                      <span className="text-xl mt-0.5">{icon as string}</span>
                      <div className="flex-1">
                        <div className="arcade-font text-[10px] text-[#00ff88]">{cargo as string}</div>
                        <div className="arcade-font text-[9px] text-[#888] mt-1">
                          {m ? m.nome : 'VAGO'}
                        </div>
                        {m && bonusLines.length > 0 && (
                          <div className="mt-2 space-y-1">
                            {bonusLines.map((line, i) => (
                              <div key={i} className="arcade-font text-[8px] text-[#ffe600] flex items-center gap-1">
                                <span className="text-[#ffe600]">▸</span> {line}
                              </div>
                            ))}
                          </div>
                        )}
                        {m && bonusLines.length === 0 && (
                          <div className="mt-1 arcade-font text-[8px] text-[#555]">bônus não carregados</div>
                        )}
                      </div>
                    </div>
                    {m && (
                      <div className="flex gap-1 ml-2 mt-1">
                        {Array.from({ length: 5 }).map((_, i) => (
                          <div key={i} className={`w-2 h-2 border ${i < m.nivel ? 'bg-[#ffe600] border-[#ffe600]' : 'border-[#333]'}`} />
                        ))}
                      </div>
                    )}
                  </div>
                </NeonCard>
              )
            })}
            <NeonButton variant="green" className="w-full" onClick={() => navigate('/market')}>
              MERCADO DE PROFISSIONAIS
            </NeonButton>
          </div>
        )}

        {/* TAB 7: EMAIL */}
        {!loading && activeTab === 7 && (
          <div className="space-y-3">
            {emails.length === 0 ? (
              <div className="text-center py-12 arcade-font text-[10px] text-[#444]">CAIXA VAZIA</div>
            ) : (
              emails.map((email, i) => (
                <NeonCard key={email.id || i} variant="pink" hover={false} className={processandoEmail === email.id ? 'opacity-50' : ''}>
                  <div className="flex items-start gap-3">
                    <Mail className="text-[#ff0055] shrink-0 mt-0.5" size={16} />
                    <div className="flex-1 min-w-0">
                      <div className="arcade-font text-[10px] text-white font-bold mb-1 uppercase">
                        {email.assunto || 'PROPOSTA DE CARREIRA'}
                      </div>
                      <p className="arcade-font text-[9px] text-[#888] mb-3 leading-relaxed">{email.corpo}</p>
                      <div className="flex gap-2">
                        {(email.tipo === 'proposta_patrocinio' || email.tipo === 'convite_duplas') ? (
                          <>
                            <button
                              onClick={() => handleEmailAcao(email.id, 'aceitar')}
                              className="bg-[#00ff88]/20 border border-[#00ff88] text-[#00ff88] px-3 py-1 arcade-font text-[8px] flex items-center gap-1"
                            >
                              <Check size={10} /> ACEITAR
                            </button>
                            <button
                              onClick={() => handleEmailAcao(email.id, 'recusar')}
                              className="bg-[#ff0055]/20 border border-[#ff0055] text-[#ff0055] px-3 py-1 arcade-font text-[8px] flex items-center gap-1"
                            >
                              <X size={10} /> RECUSAR
                            </button>
                          </>
                        ) : (
                          <button
                            onClick={() => handleEmailAcao(email.id, 'deletar')}
                            className="bg-[#444] border border-[#666] text-white px-3 py-1 arcade-font text-[8px] flex items-center gap-1"
                          >
                            <Trash2 size={10} /> APAGAR
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </NeonCard>
              ))
            )}
          </div>
        )}

      </div>
    </div>
  )
}
