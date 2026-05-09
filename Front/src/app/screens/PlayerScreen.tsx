import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router'
import { ArcadeTab, NeonCard, PixelFlag, PageHeader } from '../components'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'
import { getDuplasRating, getOverallTierLabel, isDoublesSpecialist } from '../utils/playerRatings'
import { usePlayerData } from './player/usePlayerData'
import { AtributosTab } from './player/AtributosTab'
import { RankingTab } from './player/RankingTab'
import { HistoricoTab } from './player/HistoricoTab'
import { FormaTab } from './player/FormaTab'
import { FinanceiroTab } from './player/FinanceiroTab'
import { CarreiraTab } from './player/CarreiraTab'
import { EquipeTab } from './player/EquipeTab'
import { EmailTab } from './player/EmailTab'

const TABS = ['ATRIBUTOS', 'RANKING', 'HISTÓRICO', 'FORMA', 'FINANCEIRO', 'CARREIRA', 'EQUIPE', 'EMAIL']

function fmt(v: number) {
  if (v >= 1_000_000) return `$${(v / 1_000_000).toFixed(1)}M`
  if (v >= 1_000) return `$${(v / 1_000).toFixed(0)}K`
  return `$${v}`
}

export function PlayerScreen() {
  const navigate = useNavigate()
  const location = useLocation()
  const { jogador } = useGameStore()

  const initialTab = location.state?.tab !== undefined ? location.state.tab : 0
  const [activeTab, setActiveTab] = useState(initialTab)
  const [processandoEmail, setProcessandoEmail] = useState<string | null>(null)

  const { data, loading, recarregar } = usePlayerData()

  async function handleEmailAcao(id: string, acao: 'aceitar' | 'recusar' | 'deletar') {
    setProcessandoEmail(id)
    try {
      const res = await api.email.acao(id, acao)
      if (res.ok) recarregar()
    } catch (e: any) {
      alert(e.message)
    } finally {
      setProcessandoEmail(null)
    }
  }

  const nome = jogador?.nome ?? '...'
  const rank = jogador?.ranking ?? '?'
  const money = jogador?.dinheiro ?? 0
  const titulo = jogador?.tour?.toUpperCase() ?? 'ATP'
  const atributosMentais = jogador?.atributos_psicologicos ?? {}
  const duplas = getDuplasRating(data.atributos)
  const tier = getOverallTierLabel(data.overall, typeof rank === 'number' ? rank : null)
  const especialistaDuplas = isDoublesSpecialist(data.atributos)
  const carta = jogador?.carta ?? null
  const identity = jogador?.identity ?? null
  const emailsPendentes = data.emails.filter((e) => e.status === 'pendente').length

  return (
    <div className="app-shell app-player-screen min-h-screen">
      <PageHeader title="PERFIL DO ATLETA" color="green" backTo="/hub">
        <ArcadeTab tabs={TABS} activeTab={activeTab} onChange={setActiveTab} color="green" />
      </PageHeader>

      <div className="p-4 space-y-4 pb-24 overflow-y-auto">
        <NeonCard variant="green" hover={false}>
          <div className="flex flex-col items-center gap-3">
            <div className="w-20 h-20 bg-black border-4 border-[#00ff88] flex items-center justify-center relative">
              <div className="text-4xl">🎾</div>
              {emailsPendentes > 0 && (
                <div className="absolute -top-2 -right-2 bg-[#ff0055] text-white pixel-font text-[10px] w-6 h-6 flex items-center justify-center rounded-full animate-bounce border-2 border-white">
                  {emailsPendentes}
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
                  <span className="border px-2 py-1 text-[8px] arcade-font" style={{ borderColor: carta.cor_primaria, color: carta.cor_primaria }}>
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
                <div className="text-xl pixel-font" style={{ color: carta?.cor_primaria ?? '#00ff88' }}>
                  {data.overall || '?'}
                </div>
                <div className="text-[8px] text-[#888] arcade-font">OVR</div>
              </div>
            </div>
            {identity && (
              <div className="w-full border border-white/10 bg-black/20 px-3 py-3">
                <div className="arcade-font text-[8px] text-[#8ca8b9]">PLAYSTYLES</div>
                <div className="mt-2 flex flex-wrap justify-center gap-2">
                  {identity.playstyles.slice(0, 4).map((ps: any) => (
                    <span
                      key={ps.id}
                      className="border px-2 py-1 text-[8px] arcade-font"
                      style={{ borderColor: ps.tier === 'plus' ? '#f6c453' : '#00e5ff', color: ps.tier === 'plus' ? '#f6c453' : '#00e5ff' }}
                    >
                      {ps.label}
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

        {!loading && activeTab === 0 && (
          <AtributosTab atributos={data.atributos} atributosMentais={atributosMentais} />
        )}
        {!loading && activeTab === 1 && data.rankingDet && (
          <RankingTab rankingDet={data.rankingDet} />
        )}
        {!loading && activeTab === 2 && (
          <HistoricoTab historico={data.historico} />
        )}
        {!loading && activeTab === 3 && <FormaTab />}
        {!loading && activeTab === 4 && data.financeiro && (
          <FinanceiroTab financeiro={data.financeiro} />
        )}
        {!loading && activeTab === 5 && data.carreira && (
          <CarreiraTab carreira={data.carreira} meusTitulos={data.meusTitulos} />
        )}
        {!loading && activeTab === 6 && (
          <EquipeTab equipe={data.equipe} />
        )}
        {!loading && activeTab === 7 && (
          <EmailTab
            emails={data.emails}
            processandoId={processandoEmail}
            onAcao={handleEmailAcao}
          />
        )}
      </div>
    </div>
  )
}
