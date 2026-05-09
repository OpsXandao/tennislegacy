import { useEffect, useState } from 'react'
import { TrendingUp, Award, Target, Brain, Sparkles } from 'lucide-react'
import { motion, AnimatePresence } from 'motion/react'
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from 'recharts'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'
import { PageHeader } from '../components'

const ATRIB_LABELS: Record<string, string> = {
  velocidade: 'VEL',
  forca: 'FOR',
  mental: 'MEN',
  resistencia: 'FIS',
  saque: 'SAQ',
  estrategia: 'TAT',
  consistencia: 'CON',
  retorno: 'RET',
  reflexo: 'REF',
  voleio: 'VOL',
}

type TrophySummary = {
  total: number
  grandSlams: number
  masters: number
}

export function ProgressionScreen() {
  const { jogador } = useGameStore()
  const [showLevelUp, setShowLevelUp] = useState(false)
  const [atributos, setAtributos] = useState<Record<string, number>>({})
  const [atributosPsicologicos, setAtributosPsicologicos] = useState<Record<string, number>>({})
  const [overall, setOverall] = useState(0)
  const [titulos, setTitulos] = useState<TrophySummary>({ total: 0, grandSlams: 0, masters: 0 })
  const [pontosSkill, setPontosSkill] = useState(0)
  const [alocando, setAlocando] = useState<string | null>(null)

  useEffect(() => {
    Promise.allSettled([api.progressao.status(), api.jogador.atributos(), api.historico.goat()]).then((results) => {
      const [progRes, atribRes, histRes] = results

      if (progRes.status === 'fulfilled') {
        setAtributos(progRes.value.atributos)
        setAtributosPsicologicos(progRes.value.atributos_psicologicos || {})
        setPontosSkill(progRes.value.pontos_de_skill || 0)
      }

      if (atribRes.status === 'fulfilled') {
        setOverall(atribRes.value.overall)
      }

      if (histRes.status === 'fulfilled') {
        const meusTitulos = histRes.value.meus_titulos || []
        setTitulos({
          total: meusTitulos.length,
          grandSlams: meusTitulos.filter((t: any) => t.tipo === 'Grand Slam').length,
          masters: meusTitulos.filter((t: any) => String(t.tipo || '').includes('1000')).length,
        })
      }
    })
  }, [])

  const nivel = jogador?.nivel ?? 1
  const xp = jogador?.xp ?? 0
  const xpToNext = Math.max(jogador?.xp_para_proximo_nivel ?? 100, 1)
  const xpPercentage = Math.min(100, (xp / xpToNext) * 100)
  const segments = 20

  const stats = Object.entries(atributos)
    .filter(([, value]) => typeof value === 'number')
    .slice(0, 6)
    .map(([attribute, current]) => ({
      attribute: ATRIB_LABELS[attribute] ?? attribute.toUpperCase(),
      current,
      base: Math.max(0, current - 12),
      fullMark: 100,
    }))

  const melhorAtributoTecnico = Object.entries(atributos).reduce<[string, number]>(
    (melhor, atual) => (atual[1] > melhor[1] ? atual : melhor),
    ['-', 0]
  )
  const melhorAtributoMental = Object.entries(atributosPsicologicos).reduce<[string, number]>(
    (melhor, atual) => (atual[1] > melhor[1] ? atual : melhor),
    ['-', 0]
  )
  const checkpoints = [
    {
      id: 'titulos',
      label: 'TOTAL TÍTULOS',
      value: String(titulos.total),
      detail: titulos.total > 0 ? 'TROFÉUS CONQUISTADOS' : 'SEM TÍTULOS AINDA',
      color: 'var(--neon-yellow)',
      icon: Award,
    },
    {
      id: 'slams',
      label: 'GRAND SLAMS',
      value: String(titulos.grandSlams),
      detail: titulos.grandSlams > 0 ? 'GRANDES PALCOS' : 'AGUARDANDO CONQUISTA',
      color: 'var(--neon-pink)',
      icon: Sparkles,
    },
    {
      id: 'masters',
      label: 'MASTERS 1000',
      value: String(titulos.masters),
      detail: titulos.masters > 0 ? 'VITÓRIAS ELITE' : 'EM BUSCA DO TOPO',
      color: 'var(--neon-cyan)',
      icon: Target,
    },
    {
      id: 'focus',
      label: 'MELHOR TÉC.',
      value: melhorAtributoTecnico[0] === '-' ? '--' : ATRIB_LABELS[melhorAtributoTecnico[0]] ?? melhorAtributoTecnico[0].toUpperCase(),
      detail: `${melhorAtributoTecnico[1]} IMPACTO OVR`,
      color: 'var(--neon-green)',
      icon: TrendingUp,
    },
    {
      id: 'mental',
      label: 'MELHOR MENTAL',
      value: melhorAtributoMental[0] === '-' ? '--' : melhorAtributoMental[0].replace(/_/g, ' ').toUpperCase(),
      detail: melhorAtributoMental[0] === '-' ? 'N/D' : `${melhorAtributoMental[1]} MENTAL`,
      color: '#9ca3af',
      icon: Brain,
    },
  ]

  async function handleAlocar(tipo: 'tecnico' | 'psicologico', atributo: string) {
    if (pontosSkill <= 0 || alocando) return
    const key = `${tipo}:${atributo}`
    setAlocando(key)
    try {
      const res = await api.progressao.alocar(tipo, atributo)
      setPontosSkill(res.pontos_de_skill)
      setAtributos(res.atributos)
      setAtributosPsicologicos(res.atributos_psicologicos || {})
    } finally {
      setAlocando(null)
    }
  }

  const levelBadge = (
    <div className="flex flex-col items-end gap-1.5">
      <div className="flex items-center gap-2">
        <div className="bg-neon-green px-2 py-1 text-[8px] font-bold text-black" style={{ fontFamily: 'var(--font-arcade)' }}>
          NÍV {nivel}
        </div>
        <TrendingUp size={14} className="animate-pulse text-neon-green" />
      </div>
      <button
        onClick={() => setShowLevelUp(true)}
        className="border border-neon-green bg-black px-2 py-1 text-[7px] text-neon-green transition-all hover:bg-neon-green hover:text-black"
        style={{ fontFamily: 'var(--font-arcade)' }}
      >
        EVOLUIR
      </button>
    </div>
  )

  return (
    <div className="app-shell min-h-screen font-mono pb-24">
      <PageHeader title="STATS DO JOGADOR" color="cyan" backTo="/hub" right={levelBadge} />

      <div className="p-4">

      <div className="mb-6 border-2 border-neon-green bg-[#1a1a2e] p-4" style={{ boxShadow: 'var(--glow-green)' }}>
        <div className="mb-2 flex justify-between text-[8px]">
          <span className="text-neon-green">EXPERIÊNCIA</span>
          <span className="text-neon-yellow">{xp} / {xpToNext} XP</span>
        </div>
        <div className="flex h-6 gap-[2px] bg-black p-1">
          {Array.from({ length: segments }).map((_, i) => {
            const segmentThreshold = ((i + 1) / segments) * 100
            const isFilled = xpPercentage >= segmentThreshold
            return (
              <motion.div
                key={i}
                className="flex-1"
                initial={{ scaleY: 0 }}
                animate={{
                  scaleY: isFilled ? 1 : 0.15,
                  backgroundColor: isFilled ? 'var(--neon-green)' : '#1a1a2e',
                }}
                transition={{ delay: i * 0.03, duration: 0.2 }}
                style={{
                  boxShadow: isFilled ? 'var(--glow-green)' : 'none',
                  transformOrigin: 'bottom',
                }}
              />
            )
          })}
        </div>
        <div className="mt-3 grid grid-cols-3 gap-3">
          <div className="border border-neon-green/40 bg-black p-3 text-center">
            <div className="text-[8px] text-[#888]">NÍVEL</div>
            <div className="pixel-font text-2xl text-neon-green">{nivel}</div>
          </div>
          <div className="border border-neon-yellow/40 bg-black p-3 text-center">
            <div className="text-[8px] text-[#888]">OVR</div>
            <div className="pixel-font text-2xl text-neon-yellow">{overall || '?'}</div>
          </div>
          <div className="border border-neon-cyan/40 bg-black p-3 text-center">
            <div className="text-[8px] text-[#888]">RANK</div>
            <div className="pixel-font text-2xl text-neon-cyan">#{jogador?.ranking ?? '?'}</div>
          </div>
        </div>
        <div className="mt-3 border border-neon-pink/40 bg-black p-3 text-center">
          <div className="text-[8px] text-[#888]">PONTOS DE SKILL</div>
          <div className="pixel-font text-2xl text-neon-pink">{pontosSkill}</div>
        </div>
      </div>

      <div className="mb-6 border-2 border-neon-cyan bg-[#1a1a2e] p-4" style={{ boxShadow: 'var(--glow-cyan)' }}>
        <div
          className="mb-4 text-center text-[10px] tracking-widest text-neon-cyan"
          style={{ fontFamily: 'var(--font-arcade)' }}
        >
          RADAR DE HABILIDADES
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={stats}>
              <PolarGrid stroke="#444466" strokeWidth={1} />
              <PolarAngleAxis dataKey="attribute" tick={{ fill: 'var(--neon-cyan)', fontSize: 9, fontFamily: 'Orbitron' }} />
              <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: '#444466', fontSize: 8 }} />
              <Radar name="Base" dataKey="base" stroke="#444466" fill="#444466" fillOpacity={0.3} />
              <Radar name="Atual" dataKey="current" stroke="var(--neon-cyan)" fill="var(--neon-cyan)" fillOpacity={0.6} strokeWidth={2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-4 grid grid-cols-2 gap-2">
          {stats.map((stat) => (
            <div key={stat.attribute} className="border border-neon-cyan bg-black p-2">
              <div className="mb-1 text-[8px] text-neon-cyan">{stat.attribute}</div>
              <div className="flex items-center gap-2 justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-neon-green" style={{ fontFamily: 'var(--font-arcade)' }}>
                    {stat.current}
                  </span>
                  <TrendingUp size={10} className="text-neon-green" />
                  <span className="text-[8px] text-[#888]">+{stat.current - stat.base}</span>
                </div>
                <button
                  onClick={() => handleAlocar('tecnico', Object.entries(ATRIB_LABELS).find(([, label]) => label === stat.attribute)?.[0] || 'velocidade')}
                  disabled={pontosSkill <= 0 || !!alocando}
                  className="border border-neon-green px-2 py-1 text-[8px] text-neon-green disabled:opacity-40"
                >
                  {alocando === `tecnico:${Object.entries(ATRIB_LABELS).find(([, label]) => label === stat.attribute)?.[0] || 'velocidade'}` ? '...' : '+1'}
                </button>
              </div>
            </div>
          ))}
        </div>
        {Object.keys(atributosPsicologicos).length > 0 && (
          <div className="mt-4 border border-neon-pink/40 bg-black p-3">
            <div className="mb-3 text-[9px] text-neon-pink">HABILIDADES MENTAIS</div>
            <div className="grid grid-cols-1 gap-2">
              {Object.entries(atributosPsicologicos).slice(0, 4).map(([attr, value]) => (
                <div key={attr} className="flex items-center justify-between border border-neon-pink/20 px-3 py-2">
                  <div>
                    <div className="text-[8px] text-[#888] uppercase">{attr.replace(/_/g, ' ')}</div>
                    <div className="text-[10px] text-[#ff7aa2]">{value}</div>
                  </div>
                  <button
                    onClick={() => handleAlocar('psicologico', attr)}
                    disabled={pontosSkill <= 0 || !!alocando}
                    className="border border-neon-pink px-2 py-1 text-[8px] text-neon-pink disabled:opacity-40"
                  >
                    {alocando === `psicologico:${attr}` ? '...' : '+1'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="border-2 border-neon-yellow bg-[#1a1a2e] p-4" style={{ boxShadow: 'var(--glow-gold)' }}>
        <div className="mb-4 flex items-center justify-between">
          <span className="text-[10px] tracking-widest text-neon-yellow" style={{ fontFamily: 'var(--font-arcade)' }}>
            MARCOS DE CARREIRA
          </span>
          <Award size={16} className="animate-pulse text-neon-yellow" />
        </div>
        <div className="space-y-3">
          {checkpoints.map((item, i) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08 }}
              className="flex items-center gap-3 border-2 bg-black p-3"
              style={{
                borderColor: item.color,
                boxShadow: `0 0 10px ${item.color}33`,
              }}
            >
              <div
                className="flex h-12 w-12 items-center justify-center border-2"
                style={{
                  borderColor: item.color,
                  backgroundColor: `${item.color}20`,
                }}
              >
                <item.icon size={18} style={{ color: item.color }} />
              </div>
              <div className="flex-1">
                <div className="mb-1 text-[8px] text-[#888]">{item.label}</div>
                <div className="mb-1 text-[10px] font-bold" style={{ color: item.color }}>
                  {item.value}
                </div>
                <div className="text-[8px] text-[#888]">{item.detail}</div>
              </div>
              <div className="border px-2 py-1 text-[7px]" style={{ borderColor: item.color, color: item.color }}>
                AO VIVO
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      </div>

      <AnimatePresence>
        {showLevelUp && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4"
            onClick={() => setShowLevelUp(false)}
          >
            <motion.div
              initial={{ scale: 0.8, rotate: -8 }}
              animate={{ scale: 1, rotate: 0 }}
              exit={{ scale: 0.8, rotate: 8 }}
              className="relative w-full max-w-[340px] border-4 border-neon-yellow bg-[#1a1a2e] p-6"
              style={{ boxShadow: '0 0 40px rgba(255, 230, 0, 0.8)' }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="absolute -top-2 left-1/4 animate-bounce text-2xl text-neon-yellow">✦</div>
              <div className="absolute -top-3 right-1/4 animate-bounce text-xl text-neon-yellow" style={{ animationDelay: '0.2s' }}>✦</div>
              <div className="absolute -top-1 left-1/2 animate-bounce text-3xl text-neon-yellow" style={{ animationDelay: '0.1s' }}>★</div>
              <div className="text-center">
                <motion.h2
                  className="mb-4 text-xl tracking-wider text-neon-yellow"
                  style={{ fontFamily: 'var(--font-arcade)', textShadow: 'var(--glow-gold)' }}
                  animate={{ scale: [1, 1.08, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                >
                  SUBIU DE NÍVEL!
                </motion.h2>
                <div className="mb-4 border-2 border-neon-yellow bg-black p-4">
                  <div className="mb-2 text-4xl text-neon-yellow">{nivel}</div>
                  <div className="text-[10px] text-[#888]">NOVO MARCO DESBLOQUEADO</div>
                </div>
                <button
                  onClick={() => setShowLevelUp(false)}
                  className="w-full border-2 border-neon-yellow bg-black py-2 text-[10px] text-neon-yellow transition-all hover:bg-neon-yellow hover:text-black"
                  style={{ fontFamily: 'var(--font-arcade)' }}
                >
                  CONTINUAR
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
