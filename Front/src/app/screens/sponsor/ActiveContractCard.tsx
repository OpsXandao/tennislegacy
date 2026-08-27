import { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { ChevronDown, ChevronUp, AlertTriangle } from 'lucide-react'
import type { Patrocinio, PatrocinioMeta } from '../../../types'

const STATUS_CONFIG = {
  em_dia:      { label: 'EM DIA',      color: 'var(--neon-green)', bg: 'rgba(0,255,136,0.08)' },
  sob_pressao: { label: 'SOB PRESSÃO', color: 'var(--neon-yellow)', bg: 'rgba(255,230,0,0.08)' },
  em_risco:    { label: 'EM RISCO',    color: 'var(--neon-pink)', bg: 'rgba(255,0,85,0.08)' },
} satisfies Record<string, { label: string; color: string; bg: string }>

const META_STATUS_COLOR: Record<string, string> = {
  ok:      'var(--neon-green)',
  atencao: 'var(--neon-yellow)',
  risco:   'var(--neon-pink)',
}

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

function ProgressBar({ value, color, height = 4 }: { value: number; color: string; height?: number }) {
  const pct = Math.min(100, Math.max(0, value * 100))
  return (
    <div className="w-full bg-white/5 overflow-hidden" style={{ height }}>
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${pct}%` }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        style={{ height: '100%', background: color, boxShadow: `0 0 6px ${color}88` }}
      />
    </div>
  )
}

function MetaRow({ meta }: { meta: PatrocinioMeta }) {
  const cor = META_STATUS_COLOR[meta.status] ?? '#888'
  const pct = Math.round(Math.min(1, Math.max(0, meta.progresso)) * 100)
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between gap-2">
        <span className="arcade-font text-[8px] text-[#8aa0b5] truncate">{meta.titulo}</span>
        <div className="flex items-center gap-1.5 shrink-0">
          <span className="arcade-font text-[8px]" style={{ color: cor }}>
            {meta.atual}/{meta.alvo} {meta.unidade}
          </span>
          <span className="arcade-font text-[7px]" style={{ color: cor }}>
            {pct}%
          </span>
        </div>
      </div>
      <ProgressBar value={meta.progresso} color={cor} />
    </div>
  )
}

interface Props {
  patrocinio: Patrocinio
}

export function ActiveContractCard({ patrocinio: p }: Props) {
  const [expanded, setExpanded] = useState(false)

  const cfg = STATUS_CONFIG[p.status] ?? STATUS_CONFIG.em_dia
  const nivel = nivelColor(p.nivel)
  const semanasCorridas = p.duracao_semanas - p.semanas_restantes
  const duracaoPct = p.duracao_semanas > 0 ? semanasCorridas / p.duracao_semanas : 0
  const confiancaPct = p.confianca / 100
  const confiancaCor = p.confianca >= 70 ? 'var(--neon-green)' : p.confianca >= 40 ? 'var(--neon-yellow)' : 'var(--neon-pink)'
  const hasMetas = p.metas && p.metas.length > 0

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className="border"
      style={{ borderColor: cfg.color + '55', background: cfg.bg }}
    >
      {/* Header */}
      <button
        onClick={() => setExpanded(v => !v)}
        className="w-full flex items-start gap-3 p-3 text-left"
      >
        {/* Sponsor letter logo */}
        <div
          className="shrink-0 w-9 h-9 flex items-center justify-center border text-white arcade-font text-[11px]"
          style={{ borderColor: nivel, color: nivel, background: nivel + '14' }}
        >
          {p.nome.charAt(0).toUpperCase()}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="arcade-font text-[10px] text-white">{p.nome}</span>
            <span
              className="arcade-font text-[7px] px-1.5 py-0.5 border uppercase"
              style={{ color: nivel, borderColor: nivel + '60', background: nivel + '15' }}
            >
              {p.nivel}
            </span>
            {p.status === 'em_risco' && (
              <AlertTriangle size={10} style={{ color: 'var(--neon-pink)' }} />
            )}
          </div>
          <div className="arcade-font text-[8px] text-[#555] mt-0.5 uppercase">
            {p.categoria}
          </div>
        </div>

        <div className="flex flex-col items-end shrink-0 gap-1">
          <span
            className="arcade-font text-[7px] px-2 py-0.5 border"
            style={{ color: cfg.color, borderColor: cfg.color + '55', background: cfg.color + '12' }}
          >
            {cfg.label}
          </span>
          <span className="arcade-font text-[9px] text-neon-green">
            R$ {p.valor.toLocaleString('pt-BR')}/sem
          </span>
          {expanded ? <ChevronUp size={12} color="#555" /> : <ChevronDown size={12} color="#555" />}
        </div>
      </button>

      {/* Confidence + Duration bars (always visible) */}
      <div className="px-3 pb-3 space-y-2">
        <div>
          <div className="flex justify-between items-center mb-1">
            <span className="arcade-font text-[7px] text-[#555] tracking-wider">CONFIANÇA DO PATROCINADOR</span>
            <span className="arcade-font text-[8px]" style={{ color: confiancaCor }}>{p.confianca}%</span>
          </div>
          <ProgressBar value={confiancaPct} color={confiancaCor} height={5} />
        </div>

        <div>
          <div className="flex justify-between items-center mb-1">
            <span className="arcade-font text-[7px] text-[#555] tracking-wider">DURAÇÃO DO CONTRATO</span>
            <span className="arcade-font text-[8px] text-[#8aa0b5]">
              {p.semanas_restantes} sem. restantes
            </span>
          </div>
          <ProgressBar value={duracaoPct} color={nivel} height={4} />
        </div>
      </div>

      {/* Metas — expandable */}
      <AnimatePresence>
        {expanded && hasMetas && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="px-3 pb-3 border-t border-white/5 pt-3 space-y-3">
              <div className="arcade-font text-[7px] tracking-widest text-[#444]">METAS CONTRATUAIS</div>
              {p.metas.map((meta) => (
                <MetaRow key={meta.id} meta={meta} />
              ))}
              {p.perfil && (
                <div className="arcade-font text-[8px] text-[#445560] leading-relaxed border-t border-white/5 pt-2 mt-2">
                  {p.perfil}
                </div>
              )}
            </div>
          </motion.div>
        )}
        {expanded && !hasMetas && p.perfil && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="px-3 pb-3 border-t border-white/5 pt-3">
              <div className="arcade-font text-[8px] text-[#445560] leading-relaxed">{p.perfil}</div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
