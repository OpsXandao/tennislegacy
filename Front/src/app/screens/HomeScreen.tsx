import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { useNavigate } from 'react-router'
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
} from 'recharts'
import { NeonButton } from '../components/NeonButton'
import { TronGrid } from '../components/TronGrid'
import { PixelFlag } from '../components/PixelFlag'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'

interface Archetype {
  nome: string;
  descricao: string;
  bonus?: Record<string, number>;
}

// 6 atributos representativos para o radar
const RADAR_KEYS: Array<{ key: string; label: string; psico?: boolean }> = [
  { key: 'vel_saque',   label: 'SAQUE'   },
  { key: 'forehand',    label: 'FUNDO'   },
  { key: 'voleio',      label: 'REDE'    },
  { key: 'resistencia', label: 'FÍSICO'  },
  { key: 'retorno',     label: 'RETORNO' },
  { key: 'clutch',      label: 'MENTAL', psico: true },
]

export function HomeScreen() {
  const navigate = useNavigate()
  const { setSaveAtivo, setJogador, setSemana, setTorneio, reset } = useGameStore()

  const [showForm, setShowForm] = useState(false)
  const [step, setStep] = useState(0) // 0: Tour, 1: Detalhes
  const [loading, setLoading] = useState(false)
  const [erro, setErro] = useState('')
  const [debugClicks, setDebugClicks] = useState(0)

  // Opções carregadas da API
  const [tecnicos, setTecnicos] = useState<Record<string, Archetype>>({})
  const [mentais, setMentais] = useState<Record<string, Archetype>>({})
  const [nacionalidades, setNacionalidades] = useState<string[]>([])
  const [showNacionalidades, setShowNacionalidades] = useState(false)

  // Campos do novo jogo
  const [nomeJogador, setNomeJogador] = useState('')
  const [idade, setIdade] = useState(18)
  const [nomeSave, setNomeSave] = useState('')
  const [nac, setNac] = useState('[BR] Brasil')
  const [tour, setTour] = useState<'atp' | 'wta'>('atp')
  const [archetypeId, setArchetypeId] = useState('3')
  const [mentalId, setMentalId] = useState('5')
  const [maoDominante, setMaoDominante] = useState<'Destro' | 'Canhoto'>('Destro')

  // Textos adaptáveis
  const isMasc = tour === 'atp'
  const t = {
    titulo: isMasc ? 'NOVO JOGADOR' : 'NOVA JOGADORA',
    nomeLabel: isMasc ? 'NOME DO JOGADOR' : 'NOME DA JOGADORA',
    placeholder: isMasc ? 'Ex: Carlos Silva' : 'Ex: Maria Silva',
  }

  useEffect(() => {
    Promise.all([
      api.saves.arquetipos(),
      api.saves.nacionalidades()
    ]).then(([arq, nacoes]) => {
      const nacionalidadesOrdenadas = [...nacoes.nacionalidades].sort((a, b) =>
        getCountryName(a).localeCompare(getCountryName(b), 'pt-BR')
      )
      setTecnicos(arq.tecnicos);
      setMentais(arq.mentais);
      setNacionalidades(nacionalidadesOrdenadas);

      // Fix: Tenta manter [BR] Brasil se existir, senão usa a primeira da lista
      const brBrasil = nacionalidadesOrdenadas.find(n => n === '[BR] Brasil');
      if (brBrasil) {
        setNac(brBrasil);
      } else if (nacionalidadesOrdenadas.length > 0) {
        setNac(nacionalidadesOrdenadas[0]);
      }
    }).catch(() => console.error("Erro ao carregar dados iniciais"));
  }, []);

  // Radar usa atributos reais do arquétipo (não bonus fictício)
  const getChartData = () => {
    const tec = (tecnicos[archetypeId] as any)?.atributos || {}
    const psi = (mentais[mentalId] as any)?.atributos || {}
    return RADAR_KEYS.map(({ key, label, psico }) => ({
      attribute: label,
      value: psico ? (psi[key] ?? 50) : (tec[key] ?? 60),
      fullMark: 100,
    }))
  }

  const calcularOVR = () => {
    const tec = (tecnicos[archetypeId] as any)?.atributos || {}
    const keys = ['vel_saque','pre_saque','segundo_saque','retorno','forehand',
                   'backhand','voleio','smash','lob','topspin','slice','winner',
                   'velocidade','aceleracao','resistencia','forca','agilidade']
    const vals = keys.map(k => tec[k] ?? 60).filter(v => v > 0)
    if (!vals.length) return 60
    return Math.round(vals.reduce((a, b) => a + b, 0) / vals.length)
  }

  const getOVRColor = (ovr: number) => {
    if (ovr >= 75) return 'var(--neon-yellow)'
    if (ovr >= 70) return 'var(--neon-cyan)'
    if (ovr >= 65) return 'var(--neon-green)'
    return '#7a8fa0'
  }

  const STAT_BARS = [
    { label: 'SAQUE',   key: 'vel_saque',    psico: false, color: 'var(--neon-cyan)' },
    { label: 'FUNDO',   key: 'forehand',     psico: false, color: 'var(--neon-cyan)' },
    { label: 'REDE',    key: 'voleio',       psico: false, color: 'var(--neon-cyan)' },
    { label: 'FÍSICO',  key: 'resistencia',  psico: false, color: 'var(--neon-green)' },
    { label: 'RETORNO', key: 'retorno',      psico: false, color: 'var(--neon-green)' },
    { label: 'MENTAL',  key: 'determinacao', psico: true,  color: 'var(--neon-yellow)' },
  ]

  async function handleCriar() {
    if (!nomeJogador.trim() || !nomeSave.trim()) {
      setErro('Preencha todos os campos.')
      return
    }
    setErro('')
    setLoading(true)
    try {
      const r = await api.saves.criar({
        nome: nomeSave.trim(),
        nome_jogador: nomeJogador.trim(),
        nacionalidade: nac,
        tour,
        idade,
        archetype_id: archetypeId,
        mental_id: mentalId,
        mao_dominante: maoDominante,
      })
      if (!r.ok) { setErro('Erro ao criar save.'); return }

      const c = await api.saves.carregar(r.save)
      if (!c.ok) { setErro('Erro ao carregar save.'); return }

      reset()
      setSaveAtivo(r.save)
      setJogador(c.jogador)
      setSemana(c.semana, c.ano)
      setTorneio(c.torneio ?? null)
      navigate('/signing')
    } catch (e: any) {
      setErro(e.message || 'Sem conexão com o servidor.')
    } finally {
      setLoading(false)
    }
  }

  async function handleCriarAlexandre() {
    if (loading) return
    const nome = 'alexandre_paiva'
    setErro('')
    setLoading(true)
    try {
      const r = await api.saves.criarAlexandre(nome)
      if (!r.ok) {
        setErro('Erro ao criar save preset.')
        return
      }

      const c = await api.saves.carregar(r.save)
      if (!c.ok) {
        setErro('Erro ao carregar save preset.')
        return
      }

      reset()
      setSaveAtivo(r.save)
      setJogador(c.jogador)
      setSemana(c.semana, c.ano)
      setTorneio(c.torneio ?? null)
      navigate('/signing')
    } catch (e: any) {
      setErro(e.message || 'Sem conexão com o servidor.')
    } finally {
      setLoading(false)
    }
  }

  const handleSelectTour = (selected: 'atp' | 'wta') => {
    setTour(selected)
    setStep(1)
  }

  const getCountryCode = (name: string) => {
    const match = name.match(/\[(.*?)\]/);
    return match ? match[1] : undefined;
  }

  const getCountryName = (name: string) =>
    name.replace(/\[.*?\]/, '').trim()

  return (
    <div className="app-shell min-h-screen flex flex-col items-center justify-center p-6 relative overflow-hidden">
      <TronGrid />

      {/* Logo */}
      <motion.div
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8 relative z-10"
        onClick={() => setDebugClicks(prev => prev + 1)}
      >
        <h1 className="text-neon-green pixel-font text-3xl mb-4 leading-relaxed">
          TENNIS
          <br />
          LEGACY
        </h1>
      </motion.div>

      <AnimatePresence mode="wait">
        {!showForm ? (
          <motion.div
            key="menu"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex flex-col gap-4 w-full max-w-xs relative z-10"
          >
            <NeonButton onClick={() => setShowForm(true)} variant="green">
              [ NOVO JOGO ]
            </NeonButton>
            <NeonButton onClick={() => navigate('/continue')} variant="cyan">
              [ CARREGAR ]
            </NeonButton>
            {debugClicks >= 5 && (
              <NeonButton onClick={handleCriarAlexandre} variant="yellow">
                [ ALEXANDRE PAIVA ]
              </NeonButton>
            )}
            <NeonButton onClick={() => navigate('/continue?mode=delete')} variant="yellow">
              [ APAGAR SAVES ]
            </NeonButton>
            <NeonButton onClick={() => {}} variant="pink">
              [ SAIR ]
            </NeonButton>
          </motion.div>
        ) : step === 0 ? (
          <motion.div
            key="step0"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.1 }}
            className="app-panel w-full max-w-sm relative z-10 border-2 border-neon-green p-8 text-center"
          >
            <h2 className="pixel-font text-sm text-neon-yellow mb-8">ESCOLHA SEU CIRCUITO</h2>
            <div className="grid grid-cols-1 gap-6">
              <button 
                onClick={() => handleSelectTour('atp')}
                className="group relative app-panel-elevated border-2 border-neon-green p-6 transition-all hover:bg-neon-green/10"
              >
                <div className="pixel-font text-2xl text-neon-green mb-2">ATP</div>
                <div className="arcade-font text-[10px] app-muted">MASCULINO</div>
              </button>
              <button 
                onClick={() => handleSelectTour('wta')}
                className="group relative app-panel-elevated border-2 border-neon-pink p-6 transition-all hover:bg-neon-pink/10"
              >
                <div className="pixel-font text-2xl text-neon-pink mb-2">WTA</div>
                <div className="arcade-font text-[10px] app-muted">FEMININO</div>
              </button>
            </div>
            <div className="mt-8">
              <NeonButton variant="pink" onClick={() => setShowForm(false)}>VOLTAR</NeonButton>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="step1"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            className="app-panel w-full max-w-2xl relative z-10 border-2 border-neon-green p-6 max-h-[90vh] overflow-y-auto"
          >
            <div className="flex justify-between items-center mb-6">
              <h2 className="pixel-font text-xs text-neon-green">{t.titulo}</h2>
              <span className={`arcade-font text-[10px] px-2 py-1 border ${isMasc ? 'border-neon-green text-neon-green' : 'border-neon-pink text-neon-pink'}`}>
                {tour.toUpperCase()}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Coluna Esquerda: Formulário */}
              <div className="space-y-5">
                <div className="space-y-3">
                  <div>
                    <label className="arcade-font text-[10px] app-muted block mb-1 uppercase">{t.nomeLabel}</label>
                    <input
                      className="app-input w-full border-2 border-neon-green/50 text-neon-green arcade-font text-xs px-3 py-2 outline-none focus:border-neon-green"
                      placeholder={t.placeholder}
                      value={nomeJogador}
                      onChange={(e) => {
                        setNomeJogador(e.target.value)
                        const rawSlug = e.target.value.toLowerCase().replace(/[^a-z0-9]/gi, '_')
                        const safeSlug = /[a-z0-9]/.test(rawSlug) ? rawSlug : `save_${Date.now()}`
                        setNomeSave(safeSlug)
                      }}
                    />
                  </div>

                  <div className="grid grid-cols-[80px_1fr] gap-4">
                    <div>
                      <label className="arcade-font text-[10px] app-muted block mb-1">IDADE</label>
                      <input
                        type="number"
                        className="app-input w-full border-2 border-neon-green/50 text-neon-green arcade-font text-xs px-2 py-2 outline-none focus:border-neon-green"
                        value={idade}
                        onChange={(e) => {
                          const val = parseInt(e.target.value) || 18
                          setIdade(Math.min(45, Math.max(14, val)))
                        }}
                      />
                    </div>
                    <div className="relative">
                      <label className="arcade-font text-[10px] app-muted block mb-1">PAÍS</label>
                      <button
                        type="button"
                        className="app-input w-full border-2 border-neon-green/50 text-neon-green arcade-font text-[10px] px-2 py-2 outline-none flex items-center justify-between gap-2"
                        onClick={() => setShowNacionalidades((v) => !v)}
                      >
                        <span className="flex items-center gap-2 min-w-0">
                          <PixelFlag countryCode={nac} size="md" />
                          <span className="truncate">{getCountryName(nac)}</span>
                        </span>
                        <span className="text-neon-cyan">{showNacionalidades ? '▲' : '▼'}</span>
                      </button>
                      {showNacionalidades && (
                        <div className="app-panel absolute z-20 mt-1 w-full max-h-56 overflow-y-auto border-2 border-neon-green shadow-[0_0_12px_#00ff8844]">
                          {nacionalidades.map((n) => (
                            <button
                              key={n}
                              type="button"
                              className={`w-full px-2 py-2 flex items-center gap-2 text-left arcade-font text-[10px] border-b border-neon-green/10 hover:bg-neon-green/10 ${
                                n === nac ? 'bg-neon-green/10 text-neon-green' : ''
                              }`}
                              style={{ color: n === nac ? 'var(--neon-green)' : 'var(--foreground)' }}
                              onClick={() => {
                                setNac(n)
                                setShowNacionalidades(false)
                              }}
                            >
                              <PixelFlag countryCode={n} size="sm" />
                              <span className="truncate">{getCountryName(n)}</span>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Mão dominante */}
                <div className="bg-black/40 p-3 border border-neon-green/20">
                  <label className="arcade-font text-[10px] text-neon-yellow block mb-2 text-center underline">MÃO DOMINANTE</label>
                  <div className="grid grid-cols-2 gap-2">
                    {(['Destro', 'Canhoto'] as const).map((mao) => (
                      <button
                        key={mao}
                        type="button"
                        onClick={() => setMaoDominante(mao)}
                        className="py-2 arcade-font text-[10px] border-2 transition-all"
                        style={{
                          borderColor: maoDominante === mao ? 'var(--neon-green)' : 'rgba(0,255,136,0.2)',
                          color: maoDominante === mao ? 'var(--neon-green)' : 'rgba(255,255,255,0.5)',
                          background: maoDominante === mao ? 'rgba(0,255,136,0.08)' : 'transparent',
                        }}
                      >
                        {mao === 'Destro' ? '→ DESTRO' : '← CANHOTO'}
                        {mao === 'Canhoto' && (
                          <span className="block text-[7px] text-neon-yellow/60 mt-0.5">11% no circuito</span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-3">
                  <div className="bg-black/40 p-3 border border-neon-green/20">
                    <label className="arcade-font text-[10px] text-neon-yellow block mb-2 text-center underline">ESTILO TÉCNICO</label>
                    <select
                      className="w-full bg-black border border-neon-green/50 text-white arcade-font text-[10px] px-2 py-2 outline-none mb-2"
                      value={archetypeId}
                      onChange={(e) => setArchetypeId(e.target.value)}
                    >
                      {Object.entries(tecnicos).map(([id, data]) => (
                        <option key={id} value={id}>{data.nome.toUpperCase()}</option>
                      ))}
                    </select>
                    <p className="text-[9px] arcade-font text-neon-cyan italic text-center leading-tight h-8 overflow-hidden">
                      {tecnicos[archetypeId]?.descricao}
                    </p>
                  </div>

                  <div className="bg-black/40 p-3 border border-neon-green/20">
                    <label className="arcade-font text-[10px] text-neon-yellow block mb-2 text-center underline">PERFIL MENTAL</label>
                    <select
                      className="w-full bg-black border border-neon-green/50 text-white arcade-font text-[10px] px-2 py-2 outline-none mb-2"
                      value={mentalId}
                      onChange={(e) => setMentalId(e.target.value)}
                    >
                      {Object.entries(mentais).map(([id, data]) => (
                        <option key={id} value={id}>{data.nome.toUpperCase()}</option>
                      ))}
                    </select>
                    <p className="text-[9px] arcade-font text-neon-cyan italic text-center leading-tight h-8 overflow-hidden">
                      {mentais[mentalId]?.descricao}
                    </p>
                  </div>
                </div>

                <div className="pt-2 border-t border-neon-green/20">
                  <label className="arcade-font text-[9px] text-neon-yellow block mb-1">NOME DA CARREIRA (ID DO SAVE)</label>
                  <input
                    className="w-full bg-black/40 border-2 border-neon-green/30 text-neon-green arcade-font text-[10px] px-3 py-2 outline-none focus:border-neon-green"
                    value={nomeSave}
                    onChange={(e) => setNomeSave(e.target.value.toLowerCase().replace(/[^a-z0-9_]/gi, '_'))}
                  />
                </div>
              </div>

              {/* Coluna Direita: Preview Visual */}
              {/* === PLAYER CARD PREVIEW === */}
              <div className="flex flex-col bg-black/30 border-2 border-neon-cyan/30 p-4 gap-3">
                {/* OVR + Nome */}
                <div className="flex items-center justify-between">
                  <div>
                    <div className="arcade-font text-ui-tag text-[#6e8fa5]">ARQUÉTIPO</div>
                    <div className="pixel-font text-base mt-0.5" style={{ color: 'var(--neon-cyan)' }}>
                      {tecnicos[archetypeId]?.nome?.toUpperCase() ?? '—'}
                    </div>
                    <div className="arcade-font text-ui-tag text-neon-yellow mt-0.5">
                      {mentais[mentalId]?.nome?.toUpperCase() ?? '—'}
                    </div>
                  </div>
                  <div className="text-center border-2 px-3 py-2" style={{ borderColor: getOVRColor(calcularOVR()) }}>
                    <div className="arcade-font text-ui-tag text-[#6e8fa5]">OVR</div>
                    <div className="pixel-font text-3xl leading-none mt-1" style={{ color: getOVRColor(calcularOVR()) }}>
                      {calcularOVR()}
                    </div>
                  </div>
                </div>

                {/* Radar Chart */}
                <div className="w-full h-36">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={getChartData()}>
                      <PolarGrid stroke="#1a3040" />
                      <PolarAngleAxis
                        dataKey="attribute"
                        tick={{ fill: 'var(--neon-cyan)', fontSize: 9, fontFamily: 'Orbitron' }}
                      />
                      <Radar
                        name="Player"
                        dataKey="value"
                        stroke="var(--neon-cyan)"
                        fill="var(--neon-cyan)"
                        fillOpacity={0.35}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>

                {/* Stat Bars */}
                <div className="space-y-1.5">
                  {STAT_BARS.map(({ label, key, psico, color }) => {
                    const tec = (tecnicos[archetypeId] as any)?.atributos || {}
                    const psi = (mentais[mentalId] as any)?.atributos || {}
                    const val = psico ? (psi[key] ?? 50) : (tec[key] ?? 60)
                    return (
                      <div key={key} className="flex items-center gap-2">
                        <div className="arcade-font text-ui-tag w-14 text-right text-[#6e8fa5]">{label}</div>
                        <div className="flex-1 h-2 bg-[#0a1520] border border-[#1a2e40] rounded-sm overflow-hidden">
                          <div
                            className="h-full rounded-sm transition-all duration-300"
                            style={{ width: `${val}%`, background: color, opacity: 0.85 }}
                          />
                        </div>
                        <div className="arcade-font text-ui-tag w-6 text-right" style={{ color }}>{val}</div>
                      </div>
                    )
                  })}
                </div>

                {/* Descrições */}
                <div className="border-t border-[#1a2e40] pt-2 space-y-1">
                  <p className="arcade-font text-ui-tag text-[#7ab5c8] italic leading-tight">
                    {tecnicos[archetypeId]?.descricao}
                  </p>
                  <p className="arcade-font text-ui-tag text-[#c8b870] italic leading-tight">
                    {mentais[mentalId]?.descricao}
                  </p>
                </div>
              </div>
            </div>

            {erro && <p className="arcade-font text-xs text-neon-pink text-center mt-4">{erro}</p>}

            <div className="grid grid-cols-2 gap-4 mt-6">
              <NeonButton variant="pink" onClick={() => setStep(0)}>VOLTAR</NeonButton>
              <NeonButton variant="green" onClick={handleCriar} blink={loading}>
                {loading ? 'PROCESSANDO...' : 'INICIAR JOGO'}
              </NeonButton>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div
        animate={{ opacity: [1, 0.5, 1] }}
        transition={{ duration: 2, repeat: Infinity }}
        className="mt-8 text-center arcade-font text-[9px] text-[#333] relative z-10"
      >
        TENNIS LEGACY v0.1.0 — © 2026
      </motion.div>
    </div>
  )
}
