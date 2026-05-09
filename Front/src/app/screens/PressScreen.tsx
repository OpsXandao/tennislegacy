import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'
import { motion, AnimatePresence } from 'motion/react'
import { Mic, ArrowLeft, RefreshCw, TrendingUp, TrendingDown } from 'lucide-react'
import { BottomNav } from '../components'
import { api } from '../../api/client'

type Contexto = 'pre' | 'pos' | 'geral'

interface Pergunta {
  texto: string
  etiquetas: string[]
  opcoes: { texto: string; moral: number; reputacao: number }[]
}

interface Resultado {
  texto_opcao: string
  moral_delta: number
  rep_delta: number
  moral: number
  reputacao: number
}

const CONTEXTOS: { id: Contexto; label: string; cor: string; rgb: string }[] = [
  { id: 'pre',   label: 'PRÉ-JOGO', cor: 'var(--neon-cyan)',   rgb: 'var(--neon-cyan-rgb)' },
  { id: 'pos',   label: 'PÓS-JOGO', cor: 'var(--neon-pink)',   rgb: 'var(--neon-pink-rgb)' },
  { id: 'geral', label: 'GERAL',    cor: 'var(--neon-green)',  rgb: 'var(--neon-green-rgb)' },
]

function DeltaBadge({ value, label }: { value: number; label: string }) {
  if (value === 0) return null
  const pos = value > 0
  return (
    <div
      className="flex items-center gap-1 text-[11px]"
      style={{ fontFamily: 'var(--font-pixel)', color: pos ? 'var(--neon-green)' : 'var(--neon-pink)' }}
    >
      {pos ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
      {pos ? '+' : ''}{value} {label}
    </div>
  )
}

export function PressScreen() {
  const navigate = useNavigate()
  const [contexto, setContexto] = useState<Contexto>('geral')
  const [pergunta, setPergunta] = useState<Pergunta | null>(null)
  const [carregando, setCarregando] = useState(false)
  const [respondendo, setRespondendo] = useState(false)
  const [resultado, setResultado] = useState<Resultado | null>(null)
  const [erro, setErro] = useState('')

  async function carregarPergunta() {
    setCarregando(true)
    setResultado(null)
    setErro('')
    try {
      const res = await api.imprensa.pergunta(contexto)
      setPergunta(res.pergunta ?? null)
      if (!res.pergunta) setErro('Nenhuma pergunta disponível para este contexto.')
    } catch {
      setErro('Erro ao carregar pergunta.')
    } finally {
      setCarregando(false)
    }
  }

  async function responder(idx: number) {
    if (!pergunta || respondendo) return
    setRespondendo(true)
    try {
      const res = await api.imprensa.responder(idx, contexto)
      if (res.ok) setResultado(res)
    } catch {
      setErro('Erro ao processar resposta.')
    } finally {
      setRespondendo(false)
    }
  }

  useEffect(() => {
    carregarPergunta()
  }, [contexto])

  const ctxItem = CONTEXTOS.find(c => c.id === contexto)
  const corContexto = ctxItem?.cor ?? 'var(--neon-green)'
  const corContextoRgb = ctxItem?.rgb ?? 'var(--neon-green-rgb)'

  return (
    <div className="app-shell min-h-screen overflow-y-auto pb-28">
      {/* Header */}
      <div
        className="flex items-center gap-3 px-4 py-3 border-b-2"
        style={{ borderColor: corContexto, boxShadow: `0 2px 12px rgba(${corContextoRgb},0.13)` }}
      >
        <button
          onClick={() => navigate('/hub')}
          className="p-1 transition-colors"
          style={{ color: '#555' }}
          aria-label="Voltar"
        >
          <ArrowLeft size={16} />
        </button>
        <Mic size={14} style={{ color: corContexto }} />
        <span
          className="text-[10px] tracking-widest"
          style={{ fontFamily: 'var(--font-pixel)', color: corContexto }}
        >
          SALA DE IMPRENSA
        </span>
      </div>

      {/* Seletor de contexto */}
      <div className="px-4 pt-4 flex gap-2">
        {CONTEXTOS.map(c => (
          <button
            key={c.id}
            onClick={() => setContexto(c.id)}
            className="flex-1 py-2 border-2 text-[9px] transition-all active:scale-95"
            style={{
              fontFamily: 'var(--font-pixel)',
              borderColor: contexto === c.id ? c.cor : `rgba(${c.rgb},0.20)`,
              color: contexto === c.id ? c.cor : '#444',
              background: contexto === c.id ? `rgba(${c.rgb},0.07)` : 'var(--card)',
              boxShadow: contexto === c.id ? `0 0 8px rgba(${c.rgb},0.27)` : 'none',
            }}
          >
            {c.label}
          </button>
        ))}
      </div>

      {/* Conteúdo */}
      <div className="px-4 mt-4">
        <AnimatePresence mode="wait">
          {carregando && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center gap-2 text-[10px] text-[#555] py-8"
              style={{ fontFamily: 'var(--font-pixel)' }}
            >
              <RefreshCw size={12} className="animate-spin" />
              CARREGANDO...
            </motion.div>
          )}

          {!carregando && erro && (
            <motion.div
              key="erro"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-[10px] text-neon-pink py-4"
              style={{ fontFamily: 'var(--font-pixel)' }}
            >
              {erro}
            </motion.div>
          )}

          {!carregando && pergunta && !resultado && (
            <motion.div
              key="pergunta"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
            >
              {/* Jornalista */}
              <div
                className="border-2 p-4 mb-4"
                style={{ borderColor: `rgba(${corContextoRgb},0.27)`, background: 'var(--card)' }}
              >
                <div
                  className="text-[8px] mb-2 tracking-widest"
                  style={{ fontFamily: 'var(--font-pixel)', color: corContexto }}
                >
                  JORNALISTA
                </div>
                <p
                  className="text-[13px] leading-relaxed text-white"
                  style={{ fontFamily: 'var(--font-pixel)' }}
                >
                  {pergunta.texto}
                </p>
                {pergunta.etiquetas.length > 0 && (
                  <div className="flex gap-1 mt-3 flex-wrap">
                    {pergunta.etiquetas.map(tag => (
                      <span
                        key={tag}
                        className="text-[8px] px-2 py-0.5 border"
                        style={{
                          fontFamily: 'var(--font-arcade)',
                          borderColor: `${corContexto}44`,
                          color: '#555',
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Opções de resposta */}
              <div
                className="text-[8px] mb-2 tracking-widest"
                style={{ fontFamily: 'var(--font-pixel)', color: '#444' }}
              >
                SUA RESPOSTA
              </div>
              <div className="flex flex-col gap-2">
                {pergunta.opcoes.map((op, idx) => {
                  const positivoMoral = op.moral > 0
                  const positivoRep = op.reputacao > 0
                  const hasDelta = op.moral !== 0 || op.reputacao !== 0
                  return (
                    <button
                      key={idx}
                      onClick={() => responder(idx)}
                      disabled={respondendo}
                      className="border-2 p-3 text-left transition-all active:scale-[0.98] disabled:opacity-50"
                      style={{
                        borderColor: '#333',
                        background: 'var(--card)',
                      }}
                      onMouseEnter={e => {
                        e.currentTarget.style.borderColor = corContexto
                        e.currentTarget.style.background = `rgba(${corContextoRgb},0.05)`
                      }}
                      onMouseLeave={e => {
                        e.currentTarget.style.borderColor = '#333'
                        e.currentTarget.style.background = 'var(--card)'
                      }}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <span
                          className="text-[11px] leading-relaxed text-white flex-1"
                          style={{ fontFamily: 'var(--font-pixel)' }}
                        >
                          {op.texto}
                        </span>
                        {hasDelta && (
                          <div className="flex flex-col gap-0.5 items-end shrink-0 mt-0.5">
                            {op.moral !== 0 && (
                              <span
                                className="text-[8px]"
                                style={{
                                  fontFamily: 'var(--font-arcade)',
                                  color: positivoMoral ? 'var(--neon-green)' : 'var(--neon-pink)',
                                }}
                              >
                                {positivoMoral ? '+' : ''}{op.moral} MORAL
                              </span>
                            )}
                            {op.reputacao !== 0 && (
                              <span
                                className="text-[8px]"
                                style={{
                                  fontFamily: 'var(--font-arcade)',
                                  color: positivoRep ? 'var(--neon-green)' : 'var(--neon-pink)',
                                }}
                              >
                                {positivoRep ? '+' : ''}{op.reputacao} REP
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </button>
                  )
                })}
              </div>
            </motion.div>
          )}

          {!carregando && resultado && (
            <motion.div
              key="resultado"
              initial={{ opacity: 0, scale: 0.97 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
            >
              <div
                className="border-2 p-4 mb-4"
                style={{ borderColor: 'var(--neon-green)', background: 'var(--card)', boxShadow: '0 0 12px rgba(0,255,136,0.12)' }}
              >
                <div
                  className="text-[8px] mb-2 tracking-widest text-neon-green"
                  style={{ fontFamily: 'var(--font-pixel)' }}
                >
                  VOCÊ RESPONDEU
                </div>
                <p
                  className="text-[12px] text-white leading-relaxed"
                  style={{ fontFamily: 'var(--font-pixel)' }}
                >
                  "{resultado.texto_opcao}"
                </p>
              </div>

              <div className="flex gap-3 mb-5">
                <DeltaBadge value={resultado.moral_delta} label="MORAL" />
                <DeltaBadge value={resultado.rep_delta} label="REPUTAÇÃO" />
              </div>

              <div className="flex gap-3 mb-6">
                <div
                  className="flex-1 border-2 p-3"
                  style={{ borderColor: 'var(--neon-green)', background: 'var(--card)' }}
                >
                  <div className="text-[8px] text-[#444] mb-1" style={{ fontFamily: 'var(--font-pixel)' }}>MORAL</div>
                  <div className="text-[16px] text-neon-green" style={{ fontFamily: 'var(--font-pixel)' }}>{resultado.moral}</div>
                </div>
                <div
                  className="flex-1 border-2 p-3"
                  style={{ borderColor: 'var(--neon-cyan)', background: 'var(--card)' }}
                >
                  <div className="text-[8px] text-[#444] mb-1" style={{ fontFamily: 'var(--font-pixel)' }}>REPUTAÇÃO</div>
                  <div className="text-[16px] text-neon-cyan" style={{ fontFamily: 'var(--font-pixel)' }}>{resultado.reputacao}</div>
                </div>
              </div>

              <button
                onClick={carregarPergunta}
                className="w-full border-2 border-neon-green py-3 text-[10px] text-neon-green active:scale-[0.98] transition-transform"
                style={{ fontFamily: 'var(--font-pixel)', background: 'rgba(0,255,136,0.06)' }}
              >
                PRÓXIMA PERGUNTA
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <BottomNav />
    </div>
  )
}
