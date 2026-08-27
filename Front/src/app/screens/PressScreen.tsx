import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'
import { motion, AnimatePresence } from 'motion/react'
import { Mic, ArrowLeft, RefreshCw, TrendingUp, TrendingDown, Radio } from 'lucide-react'
import { BottomNav } from '../components'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'
import imprensaData from '../../data/imprensa.json'

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

interface Jornalista {
  nome: string
  outlet: string
  iniciais: string
}

const CONTEXTOS: { id: Contexto; label: string; desc: string; cor: string }[] = [
  { id: 'pre',   label: 'PRÉ-JOGO',  desc: 'Antes da próxima partida',   cor: 'var(--neon-cyan)'  },
  { id: 'pos',   label: 'PÓS-JOGO',  desc: 'Após o último resultado',    cor: 'var(--neon-pink)'  },
  { id: 'geral', label: 'GERAL',     desc: 'Entrevista de carreira',      cor: 'var(--neon-green)' },
]

const CONTEXTO_LABEL: Record<Contexto, string> = {
  pre:   'coletiva pré-jogo',
  pos:   'entrevista pós-jogo',
  geral: 'entrevista de carreira',
}

function hashString(s: string): number {
  return s.split('').reduce((h, c) => ((h * 31 + c.charCodeAt(0)) | 0) >>> 0, 0)
}

function gerarJornalista(texto: string): Jornalista {
  const h      = hashString(texto)
  const nomes  = imprensaData.jornalistas
  const outlets = imprensaData.outlets
  const nome   = nomes[h % nomes.length]
  const outlet = outlets[(h >> 3) % outlets.length]
  const iniciais = nome.split(' ').map((p) => p[0]).join('').slice(0, 2).toUpperCase()
  return { nome, outlet, iniciais }
}

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
  const { jogador } = useGameStore()

  const [contexto,     setContexto]     = useState<Contexto>('geral')
  const [pergunta,     setPergunta]     = useState<Pergunta | null>(null)
  const [jornalista,   setJornalista]   = useState<Jornalista | null>(null)
  const [carregando,   setCarregando]   = useState(false)
  const [respondendo,  setRespondendo]  = useState(false)
  const [resultado,    setResultado]    = useState<Resultado | null>(null)
  const [erro,         setErro]         = useState('')
  const [flash,        setFlash]        = useState(false)

  async function carregarPergunta() {
    setCarregando(true)
    setResultado(null)
    setErro('')
    try {
      const res = await api.imprensa.pergunta(contexto)
      setPergunta(res.pergunta ?? null)
      if (res.pergunta) {
        setJornalista(gerarJornalista(res.pergunta.texto))
        setFlash(true)
        setTimeout(() => setFlash(false), 120)
      }
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
      const pergunta_hash = btoa(encodeURIComponent(pergunta.texto.slice(0, 50)))
      const res = await api.imprensa.responder(idx, contexto, pergunta_hash)
      if (res.ok) {
        setResultado(res)
      } else {
        setErro(res.mensagem || 'Erro ao processar resposta.')
      }
    } catch {
      setErro('Erro ao processar resposta.')
    } finally {
      setRespondendo(false)
    }
  }

  useEffect(() => { carregarPergunta() }, [contexto]) // eslint-disable-line

  const ctxItem    = CONTEXTOS.find((c) => c.id === contexto)!
  const corCtx     = ctxItem.cor
  const nomeJogador = jogador?.nome ?? 'ATLETA'

  return (
    <div className="app-shell min-h-screen overflow-y-auto pb-28 relative">

      <AnimatePresence>
        {flash && (
          <motion.div
            key="flash"
            initial={{ opacity: 0.9 }}
            animate={{ opacity: 0 }}
            transition={{ duration: 0.14 }}
            className="fixed inset-0 bg-white z-[60] pointer-events-none"
          />
        )}
      </AnimatePresence>

      <div
        className="fixed inset-0 pointer-events-none z-0"
        style={{
          background: 'radial-gradient(ellipse at 50% 0%, rgba(30,30,50,0.7) 0%, transparent 70%)',
        }}
      />

      <div
        className="relative z-10 flex items-center gap-3 px-4 py-3 border-b"
        style={{ borderColor: `${corCtx}33` }}
      >
        <button
          onClick={() => navigate('/hub')}
          className="p-1 text-white/30 hover:text-white/70 transition-colors"
          aria-label="Voltar"
        >
          <ArrowLeft size={16} />
        </button>
        <Radio size={13} style={{ color: corCtx }} />
        <span
          className="text-[10px] tracking-widest flex-1"
          style={{ fontFamily: 'var(--font-pixel)', color: corCtx }}
        >
          SALA DE IMPRENSA
        </span>
        <span
          className="text-[8px] text-white/20"
          style={{ fontFamily: 'var(--font-arcade)' }}
        >
          {nomeJogador.toUpperCase()}
        </span>
      </div>

      <div className="relative z-10 px-4 pt-4 flex gap-2">
        {CONTEXTOS.map((c) => (
          <button
            key={c.id}
            onClick={() => setContexto(c.id)}
            className="flex-1 py-2.5 border transition-all active:scale-95"
            style={{
              fontFamily: 'var(--font-pixel)',
              fontSize: 9,
              borderColor: contexto === c.id ? c.cor : 'rgba(255,255,255,0.08)',
              color: contexto === c.id ? c.cor : '#444',
              background: contexto === c.id ? `${c.cor}0d` : 'transparent',
              boxShadow: contexto === c.id ? `0 0 10px ${c.cor}22` : 'none',
            }}
          >
            <div>{c.label}</div>
            <div
              className="mt-0.5 text-[7px] text-white/25 normal-case"
              style={{ fontFamily: 'var(--font-arcade)', fontStyle: 'normal' }}
            >
              {c.desc}
            </div>
          </button>
        ))}
      </div>

      <div className="relative z-10 px-4 mt-5">
        <AnimatePresence mode="wait">

          {carregando && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center gap-2 text-[10px] text-white/25 py-10 justify-center"
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
              <div
                className="border p-4 mb-4"
                style={{ borderColor: `${corCtx}22`, background: 'rgba(255,255,255,0.02)' }}
              >
                <div className="flex items-start gap-3 mb-3">
                  <div
                    className="w-10 h-10 shrink-0 flex items-center justify-center text-[11px] font-bold border"
                    style={{
                      fontFamily: 'var(--font-arcade)',
                      background: `${corCtx}12`,
                      borderColor: `${corCtx}30`,
                      color: corCtx,
                    }}
                  >
                    {jornalista?.iniciais ?? '🎙️'}
                  </div>

                  <div className="flex-1">
                    <div
                      className="text-[10px] text-white/80 leading-tight"
                      style={{ fontFamily: 'var(--font-pixel)' }}
                    >
                      {jornalista?.nome ?? 'Jornalista'}
                    </div>
                    <div
                      className="text-[8px] text-white/25 mt-0.5"
                      style={{ fontFamily: 'var(--font-arcade)' }}
                    >
                      {jornalista?.outlet ?? '—'} · {ctxItem.desc.toUpperCase()}
                    </div>
                  </div>

                  <Mic size={13} style={{ color: corCtx, opacity: 0.6, flexShrink: 0 }} />
                </div>

                <p
                  className="text-[12px] leading-relaxed text-white"
                  style={{ fontFamily: 'var(--font-pixel)' }}
                >
                  {pergunta.texto}
                </p>

                {pergunta.etiquetas.length > 0 && (
                  <div className="flex gap-1 mt-3 flex-wrap">
                    {pergunta.etiquetas.map((tag) => (
                      <span
                        key={tag}
                        className="text-[8px] px-2 py-0.5 border"
                        style={{
                          fontFamily: 'var(--font-arcade)',
                          borderColor: `${corCtx}33`,
                          color: '#555',
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div
                className="text-[8px] mb-2 tracking-widest text-white/20"
                style={{ fontFamily: 'var(--font-pixel)' }}
              >
                SUA RESPOSTA
              </div>
              <div className="flex flex-col gap-2">
                {pergunta.opcoes.map((op, idx) => {
                  const positivoMoral = op.moral > 0
                  const positivoRep   = op.reputacao > 0
                  const hasDelta      = op.moral !== 0 || op.reputacao !== 0
                  return (
                    <button
                      key={idx}
                      onClick={() => responder(idx)}
                      disabled={respondendo}
                      className="border p-3 text-left transition-all active:scale-[0.98] disabled:opacity-50"
                      style={{ borderColor: '#222', background: 'var(--card)' }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = corCtx
                        e.currentTarget.style.background = `${corCtx}08`
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = '#222'
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
                className="border p-4 mb-4 relative overflow-hidden"
                style={{ borderColor: `${corCtx}30`, background: `${corCtx}06` }}
              >
                <div
                  className="absolute top-0 left-0 right-0 h-0.5"
                  style={{ background: corCtx, opacity: 0.4 }}
                />
                <div
                  className="text-[7px] tracking-[0.3em] text-white/25 mb-3"
                  style={{ fontFamily: 'var(--font-arcade)' }}
                >
                  {jornalista?.outlet?.toUpperCase() ?? 'IMPRENSA'} · DECLARAÇÃO
                </div>
                <p
                  className="text-[12px] text-white leading-relaxed italic"
                  style={{ fontFamily: 'var(--font-pixel)' }}
                >
                  "{resultado.texto_opcao}"
                </p>
                <div
                  className="mt-3 text-[8px] text-white/25"
                  style={{ fontFamily: 'var(--font-arcade)' }}
                >
                  — {nomeJogador}, {CONTEXTO_LABEL[contexto]}
                </div>
              </div>

              <div className="flex gap-3 mb-5">
                <DeltaBadge value={resultado.moral_delta} label="MORAL" />
                <DeltaBadge value={resultado.rep_delta}   label="REPUTAÇÃO" />
              </div>

              <div className="flex gap-3 mb-6">
                <div
                  className="flex-1 border p-3"
                  style={{ borderColor: 'var(--neon-green)', background: 'var(--card)' }}
                >
                  <div className="text-[8px] text-white/25 mb-1" style={{ fontFamily: 'var(--font-pixel)' }}>
                    MORAL
                  </div>
                  <div className="text-[18px] text-neon-green" style={{ fontFamily: 'var(--font-pixel)' }}>
                    {resultado.moral}
                  </div>
                </div>
                <div
                  className="flex-1 border p-3"
                  style={{ borderColor: 'var(--neon-cyan)', background: 'var(--card)' }}
                >
                  <div className="text-[8px] text-white/25 mb-1" style={{ fontFamily: 'var(--font-pixel)' }}>
                    REPUTAÇÃO
                  </div>
                  <div className="text-[18px] text-neon-cyan" style={{ fontFamily: 'var(--font-pixel)' }}>
                    {resultado.reputacao}
                  </div>
                </div>
              </div>

              <button
                onClick={carregarPergunta}
                className="w-full border py-3 text-[10px] transition-colors"
                style={{
                  fontFamily: 'var(--font-pixel)',
                  borderColor: corCtx,
                  color: corCtx,
                  background: `${corCtx}08`,
                }}
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
