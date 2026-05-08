import { useState, useEffect, useCallback, useMemo } from 'react'
import { useNavigate } from 'react-router'
import { ApiError } from '../../api/client'
import { PageHeader, BottomNav } from '../components'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'
import type { RankingEntry } from '../../types'
import { RankingStats } from './ranking/RankingStats'
import { RankingFilters } from './ranking/RankingFilters'
import { RankingEntryCard } from './ranking/RankingEntryCard'
import { RankingTourToggles } from './ranking/RankingTourToggles'

type Tour = 'atp' | 'wta' | 'davis'
type Modalidade = 'simples' | 'duplas' | 'clay' | 'hard' | 'grass'
type FiltroTab = 'nome' | 'nacionalidade' | 'idade' | 'pontos'

const SUP_MAP: Partial<Record<Modalidade, string>> = { clay: 'clay', hard: 'hard', grass: 'grass' }
const SUPERFICIES_LABEL: Partial<Record<Modalidade, string>> = { clay: 'ARGILA', hard: 'DURO', grass: 'GRAMA' }

function formatDateLabel() {
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(new Date()).toUpperCase()
}

export function RankingsScreen() {
  const navigate = useNavigate()
  const { jogador } = useGameStore()
  const [tour, setTour] = useState<Tour>('atp')
  const [modalidade, setModalidade] = useState<Modalidade>('simples')
  const [ranking, setRanking] = useState<RankingEntry[]>([])
  const [totalJogadores, setTotalJogadores] = useState(0)
  const [loading, setLoading] = useState(false)
  const [semSessao, setSemSessao] = useState(false)
  const [filtroTab, setFiltroTab] = useState<FiltroTab>('nome')
  const [filtroValor, setFiltroValor] = useState('')

  const carregar = useCallback(async () => {
    setLoading(true)
    setSemSessao(false)
    try {
      if (tour === 'davis') {
        const r = await api.ranking.nacoes(5000)
        setRanking(
          r.ranking.map((n) => ({
            posicao: n.posicao,
            nome: n.nome,
            nacionalidade: n.codigo,
            pontos: n.pontos,
          }))
        )
        setTotalJogadores(r.total)
        return
      }
      const supKey = SUP_MAP[modalidade]
      if (supKey) {
        const r = await api.ranking.superficie(supKey, tour === 'wta' ? 'wta' : 'atp', 500)
        setRanking(
          r.jogadores.map((j) => ({
            posicao: j.posicao,
            nome: j.nome,
            pontos: j.pontos_superficie,
            overall: j.overall,
            nacionalidade: j.nacionalidade,
          }))
        )
        setTotalJogadores(r.jogadores.length)
        return
      }
      let r
      if (modalidade === 'simples') {
        r = tour === 'atp' ? await api.ranking.atp(5000) : await api.ranking.wta(5000)
      } else {
        r = await api.ranking.duplas(tour, 5000)
      }
      setRanking(r.ranking)
      setTotalJogadores(r.total)
    } catch (e) {
      setRanking([])
      setTotalJogadores(0)
      if (e instanceof ApiError && (e.status === 400 || e.status === 404)) {
        setSemSessao(true)
      }
    } finally {
      setLoading(false)
    }
  }, [tour, modalidade])

  useEffect(() => {
    carregar()
  }, [carregar])

  useEffect(() => {
    setFiltroValor('')
    setFiltroTab('nome')
  }, [tour, modalidade])

  const bestRanking =
    tour === 'davis'
      ? '-'
      : modalidade === 'simples'
        ? (jogador?.ranking ?? ranking.find((p) => p.nome === jogador?.nome)?.posicao ?? '-')
        : (ranking.find((p) => p.nome === jogador?.nome)?.posicao ?? '-')

  const stats = [
    { label: 'SEU RANKING', value: `#${bestRanking}`, color: '#ffe600' },
    {
      label: 'PONTOS',
      value: String(
        (tour === 'davis'
          ? (ranking[0]?.pontos ?? 0)
          : (modalidade === 'simples'
              ? jogador?.pontos
              : (ranking.find((p) => p.nome === jogador?.nome)?.pontos ?? 0))
        )?.toLocaleString('pt-BR') ?? '0'
      ),
      color: '#00ff88',
    },
    {
      label: 'TOUR',
      value: String((tour === 'davis' ? 'DAVIS' : (jogador?.tour || tour)).toUpperCase()),
      color: '#00e5ff',
    },
    { label: 'NÍVEL', value: String(jogador?.nivel ?? 1), color: '#ffe600' },
  ]

  const rankingFiltrado = useMemo(() => {
    const termo = filtroValor.trim().toLowerCase()
    let lista = [...ranking]
    if (termo) {
      if (filtroTab === 'nome') {
        lista = lista.filter((p) => p.nome.toLowerCase().includes(termo))
      } else if (filtroTab === 'nacionalidade') {
        lista = lista.filter((p) => String(p.nacionalidade ?? '').toLowerCase().includes(termo))
      } else if (filtroTab === 'idade') {
        const min = Number(termo)
        if (Number.isFinite(min) && min > 0) {
          lista = lista.filter((p) => Number(p.idade ?? 0) >= min)
        }
      } else if (filtroTab === 'pontos') {
        const min = Number(termo.replace(/\./g, '').replace(',', '.'))
        if (Number.isFinite(min) && min > 0) {
          lista = lista.filter((p) => Number(p.pontos ?? 0) >= min)
        }
      }
    }
    if (filtroTab === 'idade') {
      lista.sort((a, b) => Number(b.idade ?? 0) - Number(a.idade ?? 0) || a.posicao - b.posicao)
    } else if (filtroTab === 'pontos') {
      lista.sort((a, b) => Number(b.pontos ?? 0) - Number(a.pontos ?? 0) || a.posicao - b.posicao)
    }
    return lista
  }, [ranking, filtroTab, filtroValor])

  const filtroLabel = { nome: 'Nome', nacionalidade: 'Nacionalidade', idade: 'Idade mínima', pontos: 'Pontos mínimos' }[filtroTab]

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
