import { useNavigate } from 'react-router'
import { PageHeader } from '../components'
import { useGameStore } from '../../store/gameStore'
import { RankingStats } from './ranking/RankingStats'
import { RankingFilters } from './ranking/RankingFilters'
import { RankingEntryCard } from './ranking/RankingEntryCard'
import { RankingTourToggles } from './ranking/RankingTourToggles'
import { formatDateLabel, SUPERFICIES_LABEL } from './ranking/model'
import { useRankingsScreen } from './ranking/useRankingsScreen'

export function RankingsScreen() {
  const navigate = useNavigate()
  const { jogador } = useGameStore()
  const {
    tour,
    setTour,
    modalidade,
    setModalidade,
    ranking,
    totalJogadores,
    loading,
    semSessao,
    filtroTab,
    setFiltroTab,
    filtroValor,
    setFiltroValor,
    rankingFiltrado,
    stats,
    filtroLabel,
  } = useRankingsScreen(jogador)

  const supLabel = SUPERFICIES_LABEL[modalidade]
  const titleLabel =
    tour === 'davis'
      ? 'NAÇÕES DAVIS'
      : supLabel
        ? `${tour.toUpperCase()} ${supLabel}`
        : `${tour.toUpperCase()} ${modalidade.toUpperCase()}`

  function handleNavigate(nome: string) {
    const modalidadeParam = modalidade === 'duplas' ? '?modalidade=duplas' : ''
    navigate(`/player/${tour}/${encodeURIComponent(nome)}${modalidadeParam}`)
  }

  return (
    <div className="app-shell min-h-screen font-mono pb-24">
      <PageHeader
        title={titleLabel}
        subtitle={tour === 'davis' ? `TOP NAÇÕES • ${formatDateLabel()}` : `AO VIVO • ${formatDateLabel()}`}
        color="yellow"
        backTo="/hub"
        right={
          <RankingTourToggles
            tour={tour}
            modalidade={modalidade}
            onTourChange={setTour}
            onModalidadeChange={setModalidade}
          />
        }
      />

      <div className="p-4">
        <RankingStats stats={stats} />

        <div className="mb-4 border-2 border-[#ffe600] bg-[#1a1a2e] p-3" style={{ boxShadow: 'var(--glow-gold)' }}>
          <div className="flex justify-between text-[8px] text-[#ffe600]">
            <span className="w-10">RANK</span>
            <span className="flex-1">JOGADOR</span>
            <span className="w-12 text-center">IDADE</span>
            <span className="w-20 text-right">PONTOS</span>
            <span className="w-10 text-center">VAR</span>
          </div>
        </div>

        <RankingFilters
          filtroTab={filtroTab}
          setFiltroTab={setFiltroTab}
          filtroValor={filtroValor}
          setFiltroValor={setFiltroValor}
          filtroLabel={filtroLabel}
          rankingFiltradoCount={rankingFiltrado.length}
          totalCount={totalJogadores || ranking.length}
        />

        {loading && (
          <div className="py-16 text-center pixel-font text-sm text-[#00ff88] animate-pulse">
            CARREGANDO...
          </div>
        )}

        {!loading && semSessao && (
          <div className="py-16 text-center">
            <div className="text-sm text-[#ff0055] arcade-font">Carregue um save primeiro</div>
          </div>
        )}

        {!loading && !semSessao && (
          <div className="space-y-2">
            {rankingFiltrado.map((player, i) => (
              <RankingEntryCard
                key={`${player.posicao}-${player.nome}`}
                player={player}
                index={i}
                isUser={player.nome === jogador?.nome}
                tour={tour}
                modalidade={modalidade}
                totalJogadores={totalJogadores}
                onNavigate={handleNavigate}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
