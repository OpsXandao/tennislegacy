import { useState, useEffect, useCallback, useMemo } from 'react'
import { useNavigate } from 'react-router'
import { ApiError } from '../../api/client'
import { Trophy, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { motion } from 'motion/react'
import { PixelFlag, PageHeader, BottomNav } from '../components'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'
import type { RankingEntry } from '../../types'
import { getOverallTierLabel } from '../utils/playerRatings'

type Tour = 'atp' | 'wta' | 'davis'
type Modalidade = 'simples' | 'duplas' | 'clay' | 'hard' | 'grass'
type FiltroTab = 'nome' | 'nacionalidade' | 'idade' | 'pontos'

const SUPERFICIES: { id: Modalidade; label: string; color: string }[] = [
  { id: 'clay',  label: 'ARGILA', color: '#cd7f32' },
  { id: 'hard',  label: 'DURO',   color: '#00e5ff' },
  { id: 'grass', label: 'GRAMA',  color: '#00ff88' },
]
const SUP_MAP: Partial<Record<Modalidade, string>> = { clay: 'clay', hard: 'hard', grass: 'grass' }

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

  const bestRanking = tour === 'davis'
    ? '-'
    : modalidade === 'simples' 
      ? (jogador?.ranking ?? ranking.find((p) => p.nome === jogador?.nome)?.posicao ?? '-')
      : (ranking.find((p) => p.nome === jogador?.nome)?.posicao ?? '-')

  const stats = [
    { label: 'SEU RANKING', value: `#${bestRanking}`, color: '#ffe600' },
    { label: 'PONTOS', value: String(
      (tour === 'davis'
        ? (ranking[0]?.pontos ?? 0)
        : (modalidade === 'simples' ? jogador?.pontos : (ranking.find(p => p.nome === jogador?.nome)?.pontos ?? 0)))?.toLocaleString('pt-BR') ?? '0'
    ), color: '#00ff88' },
    { label: 'TOUR', value: String((tour === 'davis' ? 'DAVIS' : (jogador?.tour || tour)).toUpperCase()), color: '#00e5ff' },
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
      return lista
    }

    if (filtroTab === 'pontos') {
      lista.sort((a, b) => Number(b.pontos ?? 0) - Number(a.pontos ?? 0) || a.posicao - b.posicao)
      return lista
    }

    return lista
  }, [ranking, filtroTab, filtroValor])

  const filtroLabel = {
    nome: 'Nome',
    nacionalidade: 'Nacionalidade',
    idade: 'Idade mínima',
    pontos: 'Pontos mínimos',
  }[filtroTab]

  const tourToggles = (
    <div className="flex flex-col gap-1.5">
      <div className="flex gap-1.5">
        <button
          onClick={() => setTour('atp')}
          className={`border-2 px-2 py-1.5 text-[7px] transition-all ${tour === 'atp' ? 'border-[#00ff88] bg-[#00ff88] text-black' : 'border-[#00ff88] bg-black text-[#00ff88]'}`}
          style={{ fontFamily: 'var(--font-arcade)', boxShadow: tour === 'atp' ? 'var(--glow-green-sm)' : 'none' }}
        >
          ATP
        </button>
        <button
          onClick={() => setTour('wta')}
          className={`border-2 px-2 py-1.5 text-[7px] transition-all ${tour === 'wta' ? 'border-[#ff0055] bg-[#ff0055] text-black' : 'border-[#ff0055] bg-black text-[#ff0055]'}`}
          style={{ fontFamily: 'var(--font-arcade)', boxShadow: tour === 'wta' ? 'var(--glow-pink-sm)' : 'none' }}
        >
          WTA
        </button>
        <button
          onClick={() => { setTour('davis'); setModalidade('simples') }}
          className={`border-2 px-2 py-1.5 text-[7px] transition-all ${tour === 'davis' ? 'border-[#ffe600] bg-[#ffe600] text-black' : 'border-[#ffe600] bg-black text-[#ffe600]'}`}
          style={{ fontFamily: 'var(--font-arcade)', boxShadow: tour === 'davis' ? 'var(--glow-gold)' : 'none' }}
        >
          DAVIS
        </button>
      </div>
      <div className={`flex gap-1 ${tour === 'davis' ? 'pointer-events-none opacity-40' : ''}`}>
        {(['simples', 'duplas'] as const).map((m) => (
          <button
            key={m}
            onClick={() => setModalidade(m)}
            className={`flex-1 border px-1 py-1 text-[6px] transition-all ${modalidade === m ? 'border-white bg-white text-black' : 'border-white/30 text-white/60'}`}
            style={{ fontFamily: 'var(--font-arcade)' }}
          >
            {m === 'simples' ? 'SIM' : 'DUP'}
          </button>
        ))}
        {SUPERFICIES.map((s) => (
          <button
            key={s.id}
            onClick={() => setModalidade(s.id)}
            className={`flex-1 border px-1 py-1 text-[6px] transition-all`}
            style={{
              fontFamily: 'var(--font-arcade)',
              borderColor: modalidade === s.id ? s.color : `${s.color}44`,
              background: modalidade === s.id ? s.color : 'transparent',
              color: modalidade === s.id ? '#000' : `${s.color}99`,
            }}
          >
            {s.label.slice(0, 3)}
          </button>
        ))}
      </div>
    </div>
  )

  return (
    <div className="app-shell min-h-screen font-mono pb-24">
      <PageHeader
        title={tour === 'davis' ? 'NAÇÕES DAVIS' : SUP_MAP[modalidade] ? `${tour.toUpperCase()} ${SUPERFICIES.find(s => s.id === modalidade)?.label ?? ''}` : `${tour.toUpperCase()} ${modalidade.toUpperCase()}`}
        subtitle={tour === 'davis' ? `TOP NAÇÕES • ${formatDateLabel()}` : `AO VIVO • ${formatDateLabel()}`}
        color="yellow"
        backTo="/hub"
        right={tourToggles}
      />

      <div className="p-4">

      <div className="mb-6 border-2 border-[#00ff88] bg-[#1a1a2e] p-4" style={{ boxShadow: 'var(--glow-green)' }}>
        <div className="mb-4 text-[10px] tracking-wider text-[#00ff88]" style={{ fontFamily: 'var(--font-arcade)' }}>
          SUAS ESTATÍSTICAS
        </div>
        <div className="grid grid-cols-2 gap-3">
          {stats.map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.08 }}
              className="border-2 border-[#00e5ff] bg-black p-3 text-center"
            >
              <div className="mb-1 text-[8px] text-[#888]">{stat.label}</div>
              <div className="text-2xl font-bold" style={{ color: stat.color, fontFamily: 'var(--font-arcade)' }}>
                {stat.value}
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="mb-4 border-2 border-[#ffe600] bg-[#1a1a2e] p-3" style={{ boxShadow: 'var(--glow-gold)' }}>
        <div className="flex justify-between text-[8px] text-[#ffe600]">
          <span className="w-10">RANK</span>
          <span className="flex-1">JOGADOR</span>
          <span className="w-12 text-center">IDADE</span>
          <span className="w-20 text-right">PONTOS</span>
          <span className="w-10 text-center">VAR</span>
        </div>
      </div>

      <div className="mb-4 border border-[#00e5ff]/30 bg-[#111927] p-3">
        <div className="mb-3 flex flex-wrap gap-2">
          {([
            ['nome', 'NOME'],
            ['nacionalidade', 'NAÇÃO'],
            ['idade', 'IDADE'],
            ['pontos', 'PONTOS'],
          ] as const).map(([valor, label]) => (
            <button
              key={valor}
              onClick={() => setFiltroTab(valor)}
              className="border px-3 py-2 text-[8px] arcade-font transition-all"
              style={{
                borderColor: filtroTab === valor ? '#00e5ff' : '#274050',
                background: filtroTab === valor ? '#00e5ff' : 'transparent',
                color: filtroTab === valor ? '#061118' : '#88bfd5',
              }}
            >
              {label}
            </button>
          ))}
        </div>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-[1fr_auto]">
          <input
            value={filtroValor}
            onChange={(e) => setFiltroValor(e.target.value)}
            placeholder={`Filtrar por ${filtroLabel.toLowerCase()}...`}
            className="border border-[#284657] bg-black px-3 py-3 arcade-font text-[10px] text-[#d8eef8] outline-none placeholder:text-[#5e7e8f]"
          />
          <div className="flex items-center justify-center border border-[#284657] bg-black px-3 py-3 arcade-font text-[9px] text-[#ffe600]">
            {rankingFiltrado.length} / {totalJogadores || ranking.length} jogadores
          </div>
        </div>
      </div>

      {loading && (
        <motion.div
          animate={{ opacity: [1, 0.3, 1] }}
          transition={{ duration: 1, repeat: Infinity }}
          className="py-16 text-center pixel-font text-sm text-[#00ff88]"
        >
          CARREGANDO...
        </motion.div>
      )}

      {!loading && semSessao && (
        <div className="py-16 text-center">
          <div className="text-sm text-[#ff0055] arcade-font">Carregue um save primeiro</div>
        </div>
      )}

      {!loading && !semSessao && (
        <div className="space-y-2">
          {rankingFiltrado.map((player, i) => {
            const highlight = player.nome === jogador?.nome
            const change = 0 // Removido hardcoded +1 (audit feedback)
            const tier = getOverallTierLabel(0, player.posicao, totalJogadores)
            return (
              <motion.div
                key={`${player.posicao}-${player.nome}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: Math.min(i * 0.03, 0.6) }} // Limita delay a 0.6s
                onClick={() => {
                  if (tour === 'davis') return
                  const modalidadeParam = modalidade === 'duplas' ? '?modalidade=duplas' : ''
                  navigate(`/player/${tour}/${encodeURIComponent(player.nome)}${modalidadeParam}`)
                }}
                className={`relative overflow-hidden border-2 p-3 ${
                  highlight ? 'border-[#00ff88] bg-[#00ff88]/20' : 'border-[#00e5ff]/30 bg-[#1a1a2e]'
                } ${tour !== 'davis' ? 'cursor-pointer transition-transform hover:-translate-y-0.5' : ''}`}
                style={highlight ? { boxShadow: 'var(--glow-green)' } : undefined}
              >
                {highlight && <div className="absolute bottom-0 left-0 top-0 w-1 animate-pulse bg-[#00ff88]" />}
                <div className="flex items-center justify-between gap-3">
                  <div className={`w-10 text-center ${player.posicao <= 3 ? 'text-[#ffe600]' : highlight ? 'text-[#00ff88]' : 'text-[#00e5ff]'}`}>
                    <span className="text-xl font-bold" style={{ fontFamily: 'var(--font-arcade)' }}>{player.posicao}</span>
                    {player.posicao === 1 && <Trophy size={12} className="ml-1 inline animate-pulse text-[#ffe600]" />}
                  </div>
                  <div className="flex flex-1 items-center gap-2 min-w-0">
                    <PixelFlag countryCode={player.nacionalidade} size="md" />
                    <div className="min-w-0">
                      <div className={`truncate text-[11px] ${highlight ? 'text-[#00ff88]' : 'text-[#00e5ff]'}`} style={{ fontFamily: 'var(--font-arcade)' }}>
                        {player.nome}
                      </div>
                      <div className={`text-[7px] ${highlight ? 'text-[#ffe600]' : 'text-[#6e8091]'}`}>
                        {tier}
                      </div>
                      {tour !== 'davis' && !highlight && (
                        <div className="text-[7px] text-[#6e8091]">Clique para abrir o perfil</div>
                      )}
                      {highlight && <div className="text-[7px] text-[#ffe600]">★ VOCÊ ★</div>}
                    </div>
                  </div>
                  <div className="w-12 text-center">
                    <div className="text-[11px] text-[#d9ebf5] arcade-font">{player.idade || '—'}</div>
                    <div className="text-[7px] text-[#66798b]">IDADE</div>
                  </div>
                  <div className="w-20 text-right">
                    <div className={`text-sm font-bold ${highlight ? 'text-[#00ff88]' : 'text-white'}`}>
                      {player.pontos.toLocaleString('pt-BR')}
                    </div>
                    <div className="text-[7px] text-[#888]">PTS</div>
                  </div>
                  <div className="flex w-10 justify-center">
                    {change > 0 ? (
                      <div className="flex items-center gap-1 text-[#00ff88]">
                        <TrendingUp size={12} />
                        <span className="text-[9px]">+{change}</span>
                      </div>
                    ) : change < 0 ? (
                      <div className="flex items-center gap-1 text-[#ff0055]">
                        <TrendingDown size={12} />
                        <span className="text-[9px]">{change}</span>
                      </div>
                    ) : (
                      <Minus size={12} className="text-[#888]" />
                    )}
                  </div>
                </div>
                {player.posicao === 4 && <div className="absolute bottom-0 left-0 right-0 h-px bg-[#ffe600] opacity-50" />}
                {player.posicao === 8 && <div className="absolute bottom-0 left-0 right-0 h-px bg-[#00e5ff] opacity-30" />}
              </motion.div>
            )
          })}
        </div>
      )}
      </div>
    </div>
  )
}
