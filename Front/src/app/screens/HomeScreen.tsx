import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { useNavigate } from 'react-router'
import { NeonButton } from '../components/NeonButton'
import { TronGrid } from '../components/TronGrid'
import { PixelFlag } from '../components/PixelFlag'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'

interface Archetype {
  nome: string;
  descricao: string;
}

export function HomeScreen() {
  const navigate = useNavigate()
  const { setSaveAtivo, setJogador, setSemana, setTorneio, reset } = useGameStore()

  const [showForm, setShowForm] = useState(false)
  const [step, setStep] = useState(0) // 0: Tour, 1: Detalhes
  const [loading, setLoading] = useState(false)
  const [erro, setErro] = useState('')

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
      if (nacionalidadesOrdenadas.length > 0 && !nacionalidadesOrdenadas.includes(nac)) {
        setNac(nacionalidadesOrdenadas[0]);
      }
    }).catch(() => console.error("Erro ao carregar dados iniciais"));
  }, []);

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
        mental_id: mentalId
      })
      if (!r.ok) { setErro('Erro ao criar save.'); return }

      const c = await api.saves.carregar(r.save)
      if (!c.ok) { setErro('Erro ao carregar save.'); return }

      reset()
      setSaveAtivo(r.save)
      setJogador(c.jogador)
      setSemana(c.semana, c.ano)
      setTorneio(c.torneio ?? null)
      navigate('/hub')
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
      navigate('/hub')
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
            {import.meta.env.DEV && (
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
            className="app-panel w-full max-w-sm relative z-10 border-2 border-[#00ff88] p-8 text-center"
          >
            <h2 className="pixel-font text-sm text-neon-yellow mb-8">ESCOLHA SEU CIRCUITO</h2>
            <div className="grid grid-cols-1 gap-6">
              <button 
                onClick={() => handleSelectTour('atp')}
                className="group relative app-panel-elevated border-2 border-[#00ff88] p-6 transition-all hover:bg-[#00ff88]/10"
              >
                <div className="pixel-font text-2xl text-[#00ff88] mb-2">ATP</div>
                <div className="arcade-font text-[10px] app-muted">MASCULINO</div>
              </button>
              <button 
                onClick={() => handleSelectTour('wta')}
                className="group relative app-panel-elevated border-2 border-[#ff0055] p-6 transition-all hover:bg-[#ff0055]/10"
              >
                <div className="pixel-font text-2xl text-[#ff0055] mb-2">WTA</div>
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
            className="app-panel w-full max-w-md relative z-10 border-2 border-[#00ff88] p-6 max-h-[85vh] overflow-y-auto"
          >
            <div className="flex justify-between items-center mb-6">
              <h2 className="pixel-font text-xs text-neon-green">{t.titulo}</h2>
              <span className={`arcade-font text-[10px] px-2 py-1 border ${isMasc ? 'border-[#00ff88] text-[#00ff88]' : 'border-[#ff0055] text-[#ff0055]'}`}>
                {tour.toUpperCase()}
              </span>
            </div>

            <div className="space-y-5">
              {/* 1. Dados Pessoais */}
              <div className="space-y-3">
                <div>
                  <label className="arcade-font text-[10px] app-muted block mb-1">{t.nomeLabel}</label>
                  <input
                    className="app-input w-full border-2 border-[#00ff88]/50 text-[#00ff88] arcade-font text-xs px-3 py-2 outline-none focus:border-[#00ff88]"
                    placeholder={t.placeholder}
                    value={nomeJogador}
                    onChange={(e) => {
                      setNomeJogador(e.target.value)
                      const rawSlug = e.target.value.toLowerCase().replace(/[^a-z0-9]/gi, '_')
                      // Audit: Garante pelo menos um alfanumérico ou mantém original se for dev
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
                      className="app-input w-full border-2 border-[#00ff88]/50 text-[#00ff88] arcade-font text-xs px-2 py-2 outline-none focus:border-[#00ff88]"
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
                      className="app-input w-full border-2 border-[#00ff88]/50 text-[#00ff88] arcade-font text-[10px] px-2 py-2 outline-none flex items-center justify-between gap-2"
                      onClick={() => setShowNacionalidades((v) => !v)}
                    >
                      <span className="flex items-center gap-2 min-w-0">
                        <PixelFlag countryCode={nac} size="md" />
                        <span className="truncate">{getCountryName(nac)}</span>
                      </span>
                      <span className="text-[#00e5ff]">{showNacionalidades ? '▲' : '▼'}</span>
                    </button>
                    {showNacionalidades && (
                      <div className="app-panel absolute z-20 mt-1 w-full max-h-56 overflow-y-auto border-2 border-[#00ff88] shadow-[0_0_12px_#00ff8844]">
                        {nacionalidades.map((n) => (
                          <button
                            key={n}
                            type="button"
                            className={`w-full px-2 py-2 flex items-center gap-2 text-left arcade-font text-[10px] border-b border-[#00ff88]/10 hover:bg-[#00ff88]/10 ${
                              n === nac ? 'bg-[#00ff88]/10 text-[#00ff88]' : ''
                            }`}
                            style={{ color: n === nac ? '#00ff88' : 'var(--foreground)' }}
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

              {/* 2. Estilo e Perfil */}
              <div className="grid grid-cols-1 gap-3">
                <div className="bg-black/40 p-3 border border-[#00ff88]/20">
                  <label className="arcade-font text-[10px] text-neon-yellow block mb-2 text-center underline">ESTILO TÉCNICO</label>
                  <select
                    className="w-full bg-black border border-[#00ff88]/50 text-white arcade-font text-[10px] px-2 py-2 outline-none mb-2"
                    value={archetypeId}
                    onChange={(e) => setArchetypeId(e.target.value)}
                  >
                    {Object.entries(tecnicos).map(([id, data]) => (
                      <option key={id} value={id}>{data.nome.toUpperCase()}</option>
                    ))}
                  </select>
                  <p className="text-[9px] arcade-font text-[#00e5ff] italic text-center leading-tight">
                    {tecnicos[archetypeId]?.descricao}
                  </p>
                </div>

                <div className="bg-black/40 p-3 border border-[#00ff88]/20">
                  <label className="arcade-font text-[10px] text-neon-yellow block mb-2 text-center underline">PERFIL MENTAL</label>
                  <select
                    className="w-full bg-black border border-[#00ff88]/50 text-white arcade-font text-[10px] px-2 py-2 outline-none mb-2"
                    value={mentalId}
                    onChange={(e) => setMentalId(e.target.value)}
                  >
                    {Object.entries(mentais).map(([id, data]) => (
                      <option key={id} value={id}>{data.nome.toUpperCase()}</option>
                    ))}
                  </select>
                  <p className="text-[9px] arcade-font text-[#00e5ff] italic text-center leading-tight">
                    {mentais[mentalId]?.descricao}
                  </p>
                </div>
              </div>

              {/* 3. Slot da Carreira (ID) */}
              <div className="pt-2 border-t border-[#00ff88]/20">
                <label className="arcade-font text-[9px] text-[#555] block mb-1">NOME DA CARREIRA (ID DO SAVE)</label>
                <input
                  className="w-full bg-transparent border-b border-[#333] text-[#555] arcade-font text-[10px] px-1 py-1 outline-none"
                  value={nomeSave}
                  onChange={(e) => setNomeSave(e.target.value.toLowerCase().replace(/[^a-z0-9_]/gi, '_'))}
                />
              </div>

              {erro && <p className="arcade-font text-xs text-[#ff0055] text-center">{erro}</p>}

              <div className="grid grid-cols-2 gap-4 pt-2">
                <NeonButton variant="pink" onClick={() => setStep(0)}>VOLTAR</NeonButton>
                <NeonButton variant="green" onClick={handleCriar} blink={loading}>
                  {loading ? 'PROCESSANDO...' : 'INICIAR JOGO'}
                </NeonButton>
              </div>
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
