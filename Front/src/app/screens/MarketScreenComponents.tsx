import { Star, DollarSign, TrendingUp, X, UserCheck, UserX, Users } from 'lucide-react'
import { motion } from 'motion/react'
import type { MembroEquipe } from '../../types'

export interface Prof {
  id: string
  nome: string
  descricao?: string
  estrelas: number
  salario_semanal: number
  bonus?: string | Record<string, number>
  nivel?: number
  categoria?: string
  estilo?: string
  surface_fit?: number
  contrato_semanas?: number
}

export interface Equipe {
  treinador: MembroEquipe | null
  fisio: MembroEquipe | null
  psicologo: MembroEquipe | null
  empresario: MembroEquipe | null
}

export interface ConfirmModal {
  tipo: 'contratar' | 'demitir'
  prof: Prof
}

// ── Constantes ─────────────────────────────────────────────────────────────────

export const TABS = [
  { label: 'TÉCNICO',    cat: 'treinador',      equipeKey: 'treinador' as keyof Equipe,  icon: '🏋️', cor: 'var(--neon-green)' },
  { label: 'FISIO',      cat: 'fisioterapeuta', equipeKey: 'fisio' as keyof Equipe,      icon: '🩺', cor: 'var(--neon-cyan)' },
  { label: 'PSICÓLOGO',  cat: 'psicologo',      equipeKey: 'psicologo' as keyof Equipe,  icon: '🧠', cor: 'var(--neon-pink)' },
  { label: 'MARKETING',  cat: 'marketing',      equipeKey: null,                         icon: '📢', cor: 'var(--neon-yellow)' },
  { label: 'EMPRESÁRIO', cat: 'empresario',     equipeKey: 'empresario' as keyof Equipe, icon: '💼', cor: 'var(--neon-purple)' },
]

export const EMPTY_EQUIPE: Equipe = { treinador: null, fisio: null, psicologo: null, empresario: null }

// ── Utilitários ────────────────────────────────────────────────────────────────

function bonusLines(bonus: Record<string, number> | undefined): string[] {
  if (!bonus) return []
  const lines: string[] = []
  if (bonus.bonus_progressao)  lines.push(`+${Math.round(bonus.bonus_progressao * 100)}% evolução no treino`)
  if (bonus.bonus_recuperacao) lines.push(`+${bonus.bonus_recuperacao} energia/semana`)
  if (bonus.bonus_xp && bonus.bonus_xp !== 1) lines.push(`×${bonus.bonus_xp.toFixed(1)} XP por partida`)
  if (bonus.bonus_mental)      lines.push(`+${bonus.bonus_mental} em atributos mentais`)
  if (bonus.bonus_fadiga)      lines.push(`-${bonus.bonus_fadiga}% fadiga acumulada`)
  if (bonus.bonus_fisico_pct)  lines.push(`+${Math.round(bonus.bonus_fisico_pct * 100)}% atributos físicos`)
  if (bonus.bonus_patrocinio)  lines.push(`+${Math.round(bonus.bonus_patrocinio * 100)}% valor de patrocínios`)
  return lines
}

export function bonusString(bonus?: string | Record<string, number>): string[] {
  if (!bonus) return []
  if (typeof bonus === 'string') return [bonus]
  return bonusLines(bonus)
}

export function Stars({ count, total = 5, size = 10 }: { count: number; total?: number; size?: number }) {
  return (
    <div className="flex items-center gap-[2px]">
      {Array.from({ length: total }).map((_, i) => (
        <Star
          key={i} size={size}
          className={i < count ? 'text-neon-yellow' : 'text-[#333]'}
          fill={i < count ? 'var(--neon-yellow)' : 'none'}
        />
      ))}
    </div>
  )
}

// ── Tabs customizados ──────────────────────────────────────────────────────────

export function TabBar({
  activeTab,
  onChange,
  filled,
}: {
  activeTab: number
  onChange: (i: number) => void
  filled: boolean[]
}) {
  return (
    <div className="flex overflow-x-auto gap-0 border-b border-white/10">
      {TABS.map((tab, i) => {
        const isActive = i === activeTab
        const isFilled = filled[i]
        return (
          <button
            key={tab.cat}
            onClick={() => onChange(i)}
            className="relative flex flex-col items-center gap-0.5 px-3 py-2 shrink-0 transition-colors"
            style={{
              borderBottom: isActive ? `2px solid ${tab.cor}` : '2px solid transparent',
              color: isActive ? tab.cor : '#444',
            }}
          >
            <span className="text-[10px]">{tab.icon}</span>
            <span className="arcade-font text-[7px] tracking-wide whitespace-nowrap">{tab.label}</span>
            {/* Slot indicator */}
            <div
              className="w-1.5 h-1.5 rounded-full mt-0.5"
              style={{
                background: isFilled ? tab.cor : '#222',
                boxShadow: isFilled ? `0 0 4px ${tab.cor}` : 'none',
              }}
            />
          </button>
        )
      })}
    </div>
  )
}

// ── Slot atual (painel de quem está contratado) ────────────────────────────────

export function SlotAtualPanel({
  membro,
  cor,
  cargo,
  profNaLista,
  onDemitir,
}: {
  membro: MembroEquipe
  cor: string
  cargo: string
  profNaLista: Prof | undefined
  onDemitir: (prof: Prof) => void
}) {
  const linhas = bonusLines(membro.bonus)
  const profParaDemitir = profNaLista ?? {
    id: membro.nome,
    nome: membro.nome,
    estrelas: membro.nivel,
    salario_semanal: membro.custo_semanal,
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -4 }}
      animate={{ opacity: 1, y: 0 }}
      className="border-2 p-4 mb-4"
      style={{ borderColor: cor + '55', background: cor + '0a' }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 min-w-0">
          <div
            className="shrink-0 w-10 h-10 flex items-center justify-center border arcade-font text-[12px]"
            style={{ borderColor: cor, color: cor, background: cor + '14' }}
          >
            {membro.nome.charAt(0).toUpperCase()}
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span className="arcade-font text-[10px] text-white">{membro.nome.toUpperCase()}</span>
              <span
                className="arcade-font text-[7px] px-1.5 py-0.5 border"
                style={{ color: cor, borderColor: cor + '55', background: cor + '12' }}
              >
                SEU {cargo.toUpperCase()}
              </span>
            </div>
            <Stars count={membro.nivel} />
            <div className="mt-1.5 flex flex-wrap gap-1.5">
              {typeof membro.surface_fit === 'number' && (
                <span className="border border-neon-cyan/40 px-1.5 py-0.5 arcade-font text-[7px] text-neon-cyan">
                  FIT {membro.surface_fit}
                </span>
              )}
              {typeof membro.contrato_semanas === 'number' && membro.contrato_semanas > 0 && (
                <span className="border border-white/20 px-1.5 py-0.5 arcade-font text-[7px] text-[#bbb]">
                  {membro.contrato_semanas} SEMANAS
                </span>
              )}
            </div>
            {linhas.length > 0 && (
              <div className="mt-1.5 space-y-0.5">
                {linhas.map((l, i) => (
                  <div key={i} className="arcade-font text-[8px] flex items-center gap-1" style={{ color: cor + 'cc' }}>
                    <span>▸</span>{l}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        <div className="shrink-0 text-right space-y-2">
          <div>
            <div className="arcade-font text-[7px] text-[#444] tracking-wide">CUSTO</div>
            <div className="arcade-font text-[10px] text-neon-yellow">
              R$ {membro.custo_semanal.toLocaleString('pt-BR')}/sem
            </div>
          </div>
          <button
            onClick={() => onDemitir(profParaDemitir)}
            className="flex items-center gap-1 border border-neon-pink/50 px-2 py-1.5 text-[8px] text-neon-pink hover:bg-neon-pink/10 transition-colors"
            style={{ fontFamily: 'var(--font-arcade)' }}
          >
            <UserX size={10} />
            DEMITIR
          </button>
        </div>
      </div>
    </motion.div>
  )
}

export function SlotVagoPanel({ cor }: { cor: string }) {
  return (
    <div
      className="border border-dashed p-3 mb-4 flex items-center gap-2 opacity-50"
      style={{ borderColor: cor + '40' }}
    >
      <Users size={14} style={{ color: cor }} />
      <span className="arcade-font text-[9px]" style={{ color: cor }}>SLOT VAGO — Contrate um profissional abaixo</span>
    </div>
  )
}

// ── Modal de confirmação ───────────────────────────────────────────────────────

export function ContractConfirmModal({
  modal,
  onConfirm,
  onCancel,
  loading,
  accentColor,
}: {
  modal: ConfirmModal
  onConfirm: () => void
  onCancel: () => void
  loading: boolean
  accentColor: string
}) {
  const isDemitir = modal.tipo === 'demitir'
  const cor = isDemitir ? 'var(--neon-pink)' : accentColor
  const bonusLinhas = bonusString(modal.prof.bonus)

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/85 backdrop-blur-sm p-4"
      onClick={(e) => { if (e.target === e.currentTarget && !loading) onCancel() }}
    >
      <motion.div
        initial={{ y: 60, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: 30, opacity: 0 }}
        transition={{ type: 'spring', stiffness: 300, damping: 26 }}
        className="w-full max-w-md border-2 bg-[#08090f]"
        style={{ borderColor: cor }}
      >
        <div className="h-1" style={{ background: cor }} />
        <div className="p-5">
          <div className="flex items-start justify-between gap-3 mb-4">
            <div>
              <div className="arcade-font text-[8px] tracking-[0.25em] mb-1" style={{ color: cor }}>
                {isDemitir ? 'RESCISÃO DE CONTRATO' : 'PROPOSTA DE CONTRATO'}
              </div>
              <div className="pixel-font text-[14px] text-white">{modal.prof.nome.toUpperCase()}</div>
            </div>
            <button onClick={onCancel} className="text-[#444] hover:text-white transition-colors">
              <X size={16} />
            </button>
          </div>

          <div className="border border-white/10 bg-white/5 p-3 mb-4 space-y-2">
            <Stars count={modal.prof.estrelas} />
            {modal.prof.descricao && (
              <div className="arcade-font text-[8px] text-[#666] leading-relaxed">{modal.prof.descricao}</div>
            )}
            <div className="flex items-center gap-1 arcade-font text-[9px] text-neon-yellow">
              <DollarSign size={10} />
              R$ {modal.prof.salario_semanal.toLocaleString('pt-BR')}/semana
            </div>
            {typeof modal.prof.surface_fit === 'number' && (
              <div className="flex items-center gap-1 arcade-font text-[8px]" style={{ color: cor }}>
                <TrendingUp size={9} />FIT DE SUPERFÍCIE {modal.prof.surface_fit}
              </div>
            )}
            {bonusLinhas.map((l, i) => (
              <div key={i} className="flex items-center gap-1 arcade-font text-[8px]" style={{ color: cor }}>
                <TrendingUp size={9} />{l}
              </div>
            ))}
          </div>

          <div className="arcade-font text-[9px] leading-relaxed mb-4" style={{ color: isDemitir ? 'var(--neon-pink)' : '#8abfcc' }}>
            {isDemitir
              ? 'Ao demitir, você perde os bônus imediatamente. Pode contratar outro a qualquer momento.'
              : 'O salário semanal será debitado automaticamente. O profissional entra em ação na próxima semana.'}
          </div>

          <div className="flex gap-2">
            <button
              onClick={onCancel}
              disabled={loading}
              className="flex-1 border border-white/20 py-2.5 arcade-font text-[9px] text-[#777] hover:text-white hover:border-white/40 transition-colors disabled:opacity-40"
            >
              CANCELAR
            </button>
            <button
              onClick={onConfirm}
              disabled={loading}
              className="flex-1 flex items-center justify-center gap-1.5 py-2.5 arcade-font text-[9px] transition-colors disabled:opacity-40"
              style={{ background: cor, color: isDemitir ? '#fff' : '#000' }}
            >
              {isDemitir ? <UserX size={11} /> : <UserCheck size={11} />}
              {loading ? '...' : isDemitir ? 'CONFIRMAR DEMISSÃO' : 'ASSINAR CONTRATO'}
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}
