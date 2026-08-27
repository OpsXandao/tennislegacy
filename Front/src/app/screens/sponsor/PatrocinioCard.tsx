import { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { PenLine, CheckCircle2, FileText } from 'lucide-react'
import type { PatrocinioDisponivel } from '../../../types'

const NIVEL_COLOR: Record<string, string> = {
  bronze:   '#cd7f32',
  silver:   '#c0c0c0',
  prata:    '#c0c0c0',
  gold:     'var(--neon-yellow)',
  ouro:     'var(--neon-yellow)',
  platinum: 'var(--neon-cyan)',
  platina:  'var(--neon-cyan)',
  diamond:  'var(--neon-pink)',
  diamante: 'var(--neon-pink)',
}

function nivelColor(nivel: string) {
  return NIVEL_COLOR[nivel?.toLowerCase()] ?? '#aaa'
}

function fmtBRL(v: number) {
  return `R$ ${v.toLocaleString('pt-BR')}`
}

interface PatrocinioCardProps {
  p: PatrocinioDisponivel
  assinando: string | null
  onAssinar: (id: string) => void
}

function SigningModal({
  p,
  onConfirm,
  onCancel,
  loading,
}: {
  p: PatrocinioDisponivel
  onConfirm: () => void
  onCancel: () => void
  loading: boolean
}) {
  const [signed, setSigned] = useState(false)
  const cor = nivelColor(p.nivel)

  function handleSign() {
    setSigned(true)
    setTimeout(onConfirm, 900)
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/85 backdrop-blur-sm p-4"
      onClick={(e) => { if (e.target === e.currentTarget && !loading) onCancel() }}
    >
      <motion.div
        initial={{ y: 80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: 40, opacity: 0 }}
        transition={{ type: 'spring', stiffness: 280, damping: 24 }}
        className="w-full max-w-md"
      >
        <AnimatePresence mode="wait">
          {!signed ? (
            <motion.div key="doc" exit={{ scale: 0.95, opacity: 0 }} className="border-2 bg-[#f4f1eb] text-[#111] shadow-[0_0_40px_rgba(255,255,255,0.08)]" style={{ borderColor: cor }}>
              {/* Faixa colorida no topo */}
              <div className="h-1.5" style={{ background: cor }} />

              <div className="p-5">
                <div className="flex items-start justify-between gap-3 mb-4">
                  <div>
                    <div className="arcade-font text-[8px] text-[#888] tracking-[0.25em] mb-1">CONTRATO DE PATROCÍNIO</div>
                    <div className="pixel-font text-[15px] text-[#111] leading-tight">{p.nome.toUpperCase()}</div>
                    <div className="arcade-font text-[9px] mt-1 px-2 py-0.5 border inline-block" style={{ color: cor, borderColor: cor + '60', background: cor + '15' }}>
                      {p.nivel.toUpperCase()} · {p.categoria.toUpperCase()}
                    </div>
                  </div>
                  <FileText size={32} className="opacity-10 shrink-0" />
                </div>

                {p.descricao && (
                  <p className="arcade-font text-[9px] text-[#555] leading-relaxed mb-4 italic border-l-2 pl-3" style={{ borderColor: cor + '55' }}>
                    "{p.descricao}"
                  </p>
                )}

                <div className="bg-[#e8e4da] border border-[#d4cfc5] p-3 space-y-2 mb-4">
                  <div className="arcade-font text-[8px] text-[#888] tracking-widest mb-2">TERMOS DO CONTRATO</div>
                  <div className="grid grid-cols-2 gap-x-4 gap-y-1.5">
                    <div>
                      <div className="arcade-font text-[7px] text-[#999]">VALOR SEMANAL</div>
                      <div className="arcade-font text-[10px] text-[#111]">{fmtBRL(p.valor_semanal)}</div>
                    </div>
                    {p.bonus_assinatura > 0 && (
                      <div>
                        <div className="arcade-font text-[7px] text-[#999]">BÔNUS DE ASSINATURA</div>
                        <div className="arcade-font text-[10px]" style={{ color: cor }}>{fmtBRL(p.bonus_assinatura)}</div>
                      </div>
                    )}
                    {p.requisito_ranking > 0 && (
                      <div>
                        <div className="arcade-font text-[7px] text-[#999]">RANKING MÍNIMO</div>
                        <div className="arcade-font text-[10px] text-[#111]">TOP {p.requisito_ranking}</div>
                      </div>
                    )}
                    {p.requisito_seguidores > 0 && (
                      <div>
                        <div className="arcade-font text-[7px] text-[#999]">SEGUIDORES MÍNIMOS</div>
                        <div className="arcade-font text-[10px] text-[#111]">{p.requisito_seguidores.toLocaleString('pt-BR')}</div>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={onCancel}
                    className="flex-1 border border-[#ccc] py-2.5 arcade-font text-[9px] text-[#888] hover:bg-[#e8e4da] transition-colors"
                  >
                    CANCELAR
                  </button>
                  <button
                    onClick={handleSign}
                    disabled={loading}
                    className="flex-1 flex items-center justify-center gap-2 py-2.5 arcade-font text-[9px] transition-colors"
                    style={{ background: cor, color: '#000' }}
                  >
                    <PenLine size={12} />
                    ASSINAR
                  </button>
                </div>

                <div className="mt-3 flex justify-between items-center opacity-30">
                  <div className="arcade-font text-[7px]">TL-{Date.now().toString(36).toUpperCase().slice(-6)}</div>
                  <div className="pixel-font text-[10px]">LEGACY TOUR</div>
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="ok"
              initial={{ scale: 0.7, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="flex flex-col items-center gap-4 py-10"
            >
              <motion.div
                animate={{ scale: [1, 1.15, 1] }}
                transition={{ duration: 0.5, repeat: 1 }}
                className="w-16 h-16 rounded-full flex items-center justify-center"
                style={{ background: cor, boxShadow: `0 0 30px ${cor}` }}
              >
                <CheckCircle2 size={32} color="#000" />
              </motion.div>
              <div className="pixel-font text-[14px] text-white text-center">CONTRATO ASSINADO!</div>
              <div className="arcade-font text-[9px] text-[#555]">{p.nome.toUpperCase()}</div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  )
}

export function PatrocinioCard({ p, assinando, onAssinar }: PatrocinioCardProps) {
  const [showModal, setShowModal] = useState(false)
  const cor = nivelColor(p.nivel)
  const loading = assinando === p.id

  function handleConfirm() {
    setShowModal(false)
    onAssinar(p.id)
  }

  return (
    <>
      <motion.div
        initial={{ opacity: 0, x: -8 }}
        animate={{ opacity: 1, x: 0 }}
        className={`border p-3 ${p.elegivel ? 'border-neon-yellow/50 bg-neon-yellow/5' : 'border-white/10 bg-white/2 opacity-60'}`}
      >
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[10px]" style={{ fontFamily: 'var(--font-arcade)', color: cor }}>
                {p.nome}
              </span>
              <span
                className="text-[8px] px-1.5 py-0.5 border uppercase"
                style={{ fontFamily: 'var(--font-arcade)', color: cor, borderColor: cor + '60', background: cor + '15' }}
              >
                {p.nivel}
              </span>
            </div>

            {p.descricao && (
              <p className="text-[9px] text-white/50 mt-1 leading-relaxed">{p.descricao}</p>
            )}

            <div className="flex flex-wrap gap-x-4 gap-y-0.5 mt-1.5">
              <span className="text-[9px] text-neon-green">{fmtBRL(p.valor_semanal)}/sem</span>
              <span className="text-[9px] text-white/50 uppercase">{p.categoria}</span>
              {p.requisito_ranking > 0 && (
                <span className="text-[9px] text-white/40">Req: top {p.requisito_ranking}</span>
              )}
              {p.bonus_assinatura > 0 && (
                <span className="text-[9px] text-neon-yellow/70">Bônus: {fmtBRL(p.bonus_assinatura)}</span>
              )}
            </div>

            {!p.elegivel && p.motivo_bloqueio && (
              <p className="text-[9px] text-neon-pink/70 mt-1">Bloqueio: {p.motivo_bloqueio}</p>
            )}
          </div>

          {p.elegivel && (
            <button
              onClick={() => setShowModal(true)}
              disabled={!!assinando}
              className="shrink-0 flex items-center gap-1.5 border border-neon-yellow px-3 py-1.5 text-[8px] text-neon-yellow hover:bg-neon-yellow/20 disabled:opacity-40 transition-colors"
              style={{ fontFamily: 'var(--font-arcade)' }}
            >
              <PenLine size={10} />
              {loading ? '...' : 'ASSINAR'}
            </button>
          )}
        </div>
      </motion.div>

      <AnimatePresence>
        {showModal && (
          <SigningModal
            p={p}
            onConfirm={handleConfirm}
            onCancel={() => setShowModal(false)}
            loading={loading}
          />
        )}
      </AnimatePresence>
    </>
  )
}
