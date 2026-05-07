import { useState, useEffect } from 'react'
import { X, Search, User, Users, Star, Trophy } from 'lucide-react'
import { motion, AnimatePresence } from 'motion/react'
import { NeonButton } from './NeonButton'
import { NeonCard } from './NeonCard'
import { PixelBar } from './PixelBar'
import { PixelFlag } from './PixelFlag'
import { api } from '../../api/client'
import type { TorneioCalendario } from '../../types'

interface Partner {
  nome: string
  nacionalidade: string
  overall: number
  posicao?: number
  vinculo?: {
    partidas: number
    vitorias: number
  }
}

interface Props {
  torneio: TorneioCalendario
  onClose: () => void
  onConfirm: (modalidade: string, parceiro?: string) => void
}

const FASE_LABEL: Record<string, string> = {
  campeao: 'Campeão',
  final: 'Final',
  semifinal: 'Semifinal',
  quarta: 'Quartas de Final',
  oitavas: 'Oitavas de Final',
  r16: 'R16',
  r32: 'R32',
  r64: 'R64',
  r128: 'R128',
  qualy_3: 'Qualifying',
  qualy_2: 'Qualifying',
  qualy_1: 'Qualifying',
}

export function TournamentEntryModal({ torneio, onClose, onConfirm }: Props) {
  const [step, setStep] = useState<'preview' | 'modalidade' | 'parceiro'>('preview')
  const [modalidade, setModalidade] = useState<'simples' | 'duplas' | 'ambos' | 'mistas'>('simples')
  const [sugestoes, setSugestoes] = useState<Partner[]>([])
  const [busca, setBusca] = useState('')
  const [resultadosBusca, setResultadosBusca] = useState<Partner[]>([])
  const [loading, setLoading] = useState(false)
  const [convidando, setConvidando] = useState<string | null>(null)
  const [feedback, setFeedback] = useState('')
  const [historico, setHistorico] = useState<{ pontos_a_defender: number; ultima_colocacao: string | null } | null>(null)

  useEffect(() => {
    api.torneio.historico(torneio.nome).then(setHistorico).catch(() => {})
  }, [torneio.nome])

  useEffect(() => {
    if (step === 'parceiro') {
      setLoading(true)
      api.duplas.sugestoes()
        .then(r => setSugestoes(r.parceiros))
        .finally(() => setLoading(false))
    }
  }, [step])

  const handleConfirmarModalidade = () => {
    if (modalidade === 'simples') {
      onConfirm('simples')
    } else {
      setStep('parceiro')
    }
  }

  const handleBuscar = async () => {
    if (!busca) return
    setLoading(true)
    try {
      const r = await api.duplas.buscar({ nome: busca })
      setResultadosBusca(r.parceiros)
    } finally {
      setLoading(false)
    }
  }

  const handleConvidar = async (partner: Partner) => {
    setConvidando(partner.nome)
    setFeedback('')
    try {
      const r = await api.duplas.convidar(partner.nome, torneio.tipo)
      if (r.ok) {
        setFeedback(`✅ ${r.mensagem}`)
        setTimeout(() => onConfirm(modalidade, partner.nome), 1500)
      } else {
        setFeedback(`❌ ${r.mensagem}`)
      }
    } catch (e: any) {
      setFeedback(`❌ Erro: ${e.message}`)
    } finally {
      setConvidando(null)
    }
  }

  const tier = torneio.tipo.toLowerCase()
  const defendingChampion = (torneio as any).ultimo_campeao || '---'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm">
      <motion.div 
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="app-panel relative w-full max-w-md border-2 border-[#00ff88] p-6 shadow-[0_0_30px_rgba(0,255,136,0.3)]"
      >
        <button onClick={onClose} className="absolute right-4 top-4 text-[#00ff88] hover:scale-110 transition-transform">
          <X size={24} />
        </button>

        <AnimatePresence mode="wait">
          {step === 'preview' ? (
            <motion.div
              key="preview"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              <div className="mb-2 text-[#00ff88] arcade-font text-[10px] tracking-widest">{torneio.tipo.toUpperCase()}</div>
              <h2 className="mb-4 pixel-font text-xl uppercase tracking-tighter leading-tight" style={{ color: 'var(--foreground)' }}>{torneio.nome}</h2>

              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="app-panel-elevated border-2 border-[#333] p-3">
                  <div className="text-[8px] app-muted arcade-font mb-1">LOCAL</div>
                  <div className="text-[10px] arcade-font truncate" style={{ color: 'var(--foreground)' }}>{torneio.local.toUpperCase()}</div>
                </div>
                <div className="app-panel-elevated border-2 border-[#333] p-3">
                  <div className="text-[8px] app-muted arcade-font mb-1">QUADRA</div>
                  <div className="text-[10px] text-[#ffe600] arcade-font">{torneio.superficie.toUpperCase()}</div>
                </div>
                <div className="app-panel-elevated border-2 border-[#333] p-3">
                  <div className="text-[8px] app-muted arcade-font mb-1">PREMIAÇÃO</div>
                  <div className="text-[10px] text-[#00ff88] arcade-font">{torneio.premiacao || '$ 0'}</div>
                </div>
                <div className="app-panel-elevated border-2 border-[#333] p-3">
                  <div className="text-[8px] app-muted arcade-font mb-1">DEF. CAMPEÃO</div>
                  <div className="text-[10px] text-[#00e5ff] arcade-font truncate">{defendingChampion.toUpperCase()}</div>
                </div>
              </div>

              {/* Histórico do jogador neste torneio */}
              {historico && (historico.pontos_a_defender > 0 || historico.ultima_colocacao) && (
                <div className="mb-4 border-2 border-[#ffe600]/40 bg-[#ffe600]/5 p-3 grid grid-cols-2 gap-3">
                  <div>
                    <div className="text-[8px] app-muted arcade-font mb-1">PONTOS A DEFENDER</div>
                    <div className="text-[12px] text-[#ffe600] pixel-font font-bold">
                      {historico.pontos_a_defender > 0 ? `${historico.pontos_a_defender} PTS` : '—'}
                    </div>
                  </div>
                  <div>
                    <div className="text-[8px] app-muted arcade-font mb-1">ÚLTIMA COLOCAÇÃO</div>
                    <div className="text-[10px] text-white arcade-font">
                      {historico.ultima_colocacao
                        ? (FASE_LABEL[historico.ultima_colocacao] ?? historico.ultima_colocacao).toUpperCase()
                        : '—'}
                    </div>
                  </div>
                </div>
              )}

              <NeonButton variant="green" className="w-full" onClick={() => setStep('modalidade')}>
                INSCREVER-SE
              </NeonButton>
            </motion.div>
          ) : step === 'modalidade' ? (
            <motion.div 
              key="step1"
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: 20, opacity: 0 }}
              className="space-y-4"
            >
              <div className="text-[10px] arcade-font text-[#00e5ff] mb-4">ESCOLHA A MODALIDADE:</div>

              <button
                onClick={() => setModalidade('simples')}
                className={`w-full border-2 p-4 flex items-center justify-between transition-all ${modalidade === 'simples' ? 'border-[#00ff88] bg-[#00ff88]/10' : 'border-[#333] opacity-60'}`}
              >
                <div className="flex items-center gap-3">
                  <User className={modalidade === 'simples' ? 'text-[#00ff88]' : 'text-[#888]'} />
                  <span className={`arcade-font text-xs ${modalidade === 'simples' ? 'text-white' : 'text-[#888]'}`}>SIMPLES</span>
                </div>
                {modalidade === 'simples' && <div className="text-[#00ff88]">◀</div>}
              </button>

              <button
                onClick={() => setModalidade('duplas')}
                className={`w-full border-2 p-4 flex items-center justify-between transition-all ${modalidade === 'duplas' ? 'border-[#00ff88] bg-[#00ff88]/10' : 'border-[#333] opacity-60'}`}
              >
                <div className="flex items-center gap-3">
                  <Users className={modalidade === 'duplas' ? 'text-[#00ff88]' : 'text-[#888]'} />
                  <span className={`arcade-font text-xs ${modalidade === 'duplas' ? 'text-white' : 'text-[#888]'}`}>DUPLAS</span>
                </div>
                {modalidade === 'duplas' && <div className="text-[#00ff88]">◀</div>}
              </button>

              {torneio.permite_mistas && (
                <button
                  onClick={() => setModalidade('mistas')}
                  className={`w-full border-2 p-4 flex items-center justify-between transition-all ${modalidade === 'mistas' ? 'border-[#ff0055] bg-[#ff0055]/10' : 'border-[#333] opacity-60'}`}
                >
                  <div className="flex items-center gap-3">
                    <Trophy className={modalidade === 'mistas' ? 'text-[#ff0055]' : 'text-[#888]'} />
                    <span className={`arcade-font text-xs ${modalidade === 'mistas' ? 'text-white' : 'text-[#888]'}`}>DUPLAS MISTAS</span>
                  </div>
                  {modalidade === 'mistas' && <div className="text-[#ff0055]">◀</div>}
                </button>
              )}

              <div className="pt-4">
                <NeonButton variant="green" className="w-full" onClick={handleConfirmarModalidade}>
                  CONFIRMAR
                </NeonButton>
              </div>
            </motion.div>
          ) : (
            <motion.div 
              key="step2"
              initial={{ x: 20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -20, opacity: 0 }}
              className="flex flex-col h-[400px]"
            >
              <div className="text-[10px] arcade-font text-[#ffe600] mb-4">ENCONTRAR PARCEIRO DE DUPLAS:</div>
              
              <div className="flex gap-2 mb-4">
                <div className="relative flex-1">
                  <Search className="absolute left-2 top-1/2 -translate-y-1/2 text-[#888]" size={14} />
                  <input 
                    type="text" 
                    value={busca}
                    onChange={e => setBusca(e.target.value)}
                    placeholder="BUSCAR JOGADOR..."
                    className="w-full bg-black border-2 border-[#333] p-2 pl-8 arcade-font text-[10px] text-white focus:border-[#00e5ff] outline-none"
                    onKeyDown={e => e.key === 'Enter' && handleBuscar()}
                  />
                </div>
                <button onClick={handleBuscar} className="bg-[#00e5ff] text-black px-4 py-1 arcade-font text-[9px]">GO</button>
              </div>

              {feedback && (
                <div className={`mb-4 p-2 text-center arcade-font text-[9px] border-2 ${feedback.startsWith('✅') ? 'border-[#00ff88] text-[#00ff88]' : 'border-[#ff0055] text-[#ff0055]'}`}>
                  {feedback.toUpperCase()}
                </div>
              )}

              <div className="flex-1 overflow-y-auto space-y-3 pr-1 [scrollbar-width:thin]">
                {loading ? (
                  <div className="py-12 text-center arcade-font text-[9px] text-[#00ff88] animate-pulse">BUSCANDO...</div>
                ) : (
                  (resultadosBusca.length > 0 ? resultadosBusca : sugestoes).map((p, i) => (
                    <div key={p.nome} className="border-2 border-[#333] bg-[#111] p-3 hover:border-[#00ff88] transition-colors group">
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex items-center gap-2">
                          <PixelFlag countryCode={p.nacionalidade} size="sm" />
                          <div className="arcade-font text-[10px] truncate max-w-[140px]" style={{ color: 'var(--foreground)' }}>{p.nome.toUpperCase()}</div>
                        </div>
                        <div className="text-[#ffe600] pixel-font text-sm">{p.overall}</div>
                      </div>
                      
                      <div className="flex justify-between items-end">
                        <div className="text-[8px] app-muted arcade-font">
                          {p.vinculo ? (
                            <span className="text-[#00ff88]">{p.vinculo.partidas} JOGOS • {Math.round((p.vinculo.vitorias/p.vinculo.partidas)*100)}% VITÓRIAS</span>
                          ) : (
                            `RANK #${p.posicao || '?'}`
                          )}
                        </div>
                        <button 
                          onClick={() => handleConvidar(p)}
                          disabled={!!convidando}
                          className="bg-[#00ff88] text-black px-3 py-1 arcade-font text-[8px] font-bold group-hover:animate-pulse disabled:opacity-50"
                        >
                          {convidando === p.nome ? '...' : 'CONVIDAR'}
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>

              <div className="pt-4 flex gap-3">
                <button onClick={() => setStep('modalidade')} className="flex-1 border-2 border-[#888] app-muted py-2 arcade-font text-[10px]">← VOLTAR</button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  )
}
