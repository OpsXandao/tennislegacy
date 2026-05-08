import { motion } from 'motion/react'
import type {
  AdversarioInfo,
  Alvo,
  Faixa,
  AbordagemValor,
  InstrucaoValor,
  MentalidadeValor,
  SegundoSaqueModo,
} from './types'
import {
} from './model'

export const INTENCOES = [
  { valor: 'ARRISCAR', label: 'PRESSIONAR', sub: 'Winner / Ace', color: '#ff0055', emoji: '⚡' },
  { valor: 'EQUILIBRADO', label: 'CONSTRUIR', sub: 'Rally consistente', color: '#00e5ff', emoji: '◎' },
  { valor: 'DEFENSIVO', label: 'DEFENDER', sub: 'Cansar o rival', color: '#00ff88', emoji: '🛡' },
] as const

export const MENTALIDADES = [
  { valor: 'DEFENSIVA', label: 'CONSERVADORA', desc: 'Foca na consistência, espera o erro.', color: '#00e5ff', emoji: '🧱' },
  { valor: 'EQUILIBRADA', label: 'EQUILIBRADA', desc: 'Padrão moderno de trocas.', color: '#00ff88', emoji: '⚖️' },
  { valor: 'OFENSIVA', label: 'AGRESSIVA', desc: 'Busca winners e encurta pontos.', color: '#ff4466', emoji: '🔥' },
] as const

export const ABORDAGENS = [
  { valor: 'BASELINE', label: 'BASE-LINER', desc: 'Trocas pesadas do fundo.', icon: '🎾' },
  { valor: 'SERVE_VOLLEY', label: 'SAQUE E REDE', desc: 'Agressão máxima na rede.', icon: '👟' },
  { valor: 'COUNTER', label: 'CONTRA-ATAQUE', desc: 'Usa a força do rival.', icon: '🛡️' },
] as const

export const INSTRUCOES = [
  { valor: 'PADRAO', label: 'PADRÃO', desc: 'Sem ordens específicas.', emoji: '•' },
  { valor: 'FORCAR_BACKHAND', label: 'FORÇAR BACKHAND', desc: 'Ataca o lado mais fraco.', emoji: '↙️' },
  { valor: 'TROCAS_LONGAS', label: 'TROCAS LONGAS', desc: 'Desgasta o físico do rival.', emoji: '🔁' },
  { valor: 'ATACAR_SAQUE', label: 'ATACAR 2º SAQUE', desc: 'Pressão na devolução.', emoji: '🎯' },
] as const

export function CourtMini({
  servindo,
  faixa,
  alvo,
  intencao,
}: {
  servindo: 'jogador' | 'adversario'
  faixa: Faixa
  alvo: Alvo
  intencao: string | null
}) {
  const alvoX = alvo === 'ESQUERDA' ? '22%' : alvo === 'DIREITA' ? '78%' : '50%'
  const alvoY = faixa === 'REDE' ? '35%' : faixa === 'MEIO' ? '50%' : '66%'
  const bolaX = servindo === 'jogador' ? '38%' : '62%'
  const bolaY = servindo === 'jogador' ? '64%' : '36%'
  const intencaoColor =
    intencao === 'ARRISCAR' ? '#ffe600' : intencao === 'DEFENSIVO' ? '#00ff88' : '#00e5ff'

  return (
    <div className="border border-[#00e5ff]/25 bg-[#07121c] px-3 py-3">
      <div className="mb-2 flex items-center justify-between">
        <div className="arcade-font text-[7px] tracking-widest text-[#6fa7b5]">QUADRA TÁTICA</div>
        <div className="arcade-font text-[7px] text-[#7b91a7]">
          {servindo === 'jogador' ? 'SEU SAQUE' : 'SAQUE RIVAL'}
        </div>
      </div>
      <div className="relative h-36 overflow-hidden border border-[#7cc7d9] bg-[linear-gradient(180deg,#0f2840_0%,#11273b_45%,#0f2840_100%)]">
        <div className="absolute inset-y-0 left-1/2 w-px -translate-x-1/2 bg-white/35" />
        <div className="absolute bottom-[16%] left-[12%] right-[12%] top-[16%] border border-white/40" />
        <div className="absolute left-[12%] right-[12%] top-1/2 h-px -translate-y-1/2 bg-white/40" />
        <div className="absolute bottom-[16%] left-1/2 top-[16%] w-px -translate-x-1/2 bg-white/30" />
        <div
          className="absolute h-3.5 w-3.5 -translate-x-1/2 -translate-y-1/2 border-2 border-[#00ff88] bg-[#04190e] shadow-[0_0_12px_rgba(0,255,136,0.45)]"
          style={{ left: '18%', top: '72%' }}
        />
        <div
          className="absolute h-3.5 w-3.5 -translate-x-1/2 -translate-y-1/2 border-2 border-[#ff8d6d] bg-[#28120d] shadow-[0_0_12px_rgba(255,141,109,0.4)]"
          style={{ left: '82%', top: '28%' }}
        />
        <motion.div
          className="absolute h-2.5 w-2.5 rounded-full border border-white/40"
          style={{ background: intencaoColor }}
          animate={{ left: [bolaX, alvoX], top: [bolaY, alvoY], scale: [0.9, 1.15, 1] }}
          transition={{ duration: 0.55, ease: 'easeOut' }}
        />
        <div
          className="absolute h-5 w-5 -translate-x-1/2 -translate-y-1/2 rounded-full border border-[#ffe600] bg-[#ffe60014] shadow-[0_0_18px_rgba(255,230,0,0.28)]"
          style={{ left: alvoX, top: alvoY }}
        />
      </div>
      <div className="mt-2 grid grid-cols-3 gap-2">
        <div className="border border-[#1c3140] bg-[#08121a] px-2 py-1.5">
          <div className="arcade-font text-[6px] tracking-widest text-[#5e7388]">INTENÇÃO</div>
          <div className="mt-1 arcade-font text-[8px]" style={{ color: intencaoColor }}>
            {INTENCOES.find(item => item.valor === intencao)?.label ?? 'CONSTRUIR'}
          </div>
        </div>
        <div className="border border-[#1c3140] bg-[#08121a] px-2 py-1.5">
          <div className="arcade-font text-[6px] tracking-widest text-[#5e7388]">FAIXA</div>
          <div className="mt-1 arcade-font text-[8px] text-[#d6f2ff]">{faixa}</div>
        </div>
        <div className="border border-[#1c3140] bg-[#08121a] px-2 py-1.5">
          <div className="arcade-font text-[6px] tracking-widest text-[#5e7388]">ALVO</div>
          <div className="mt-1 arcade-font text-[8px] text-[#d6f2ff]">{alvo}</div>
        </div>
      </div>
    </div>
  )
}

export function EnergyBar({
  label,
  value,
  color,
  inverted,
}: {
  label: string
  value: number
  color: string
  inverted?: boolean
}) {
  const safe = Math.max(0, Math.min(100, Math.round(value)))
  const barColor = inverted
    ? safe > 70 ? '#ff0055' : safe > 40 ? '#ffe600' : '#00ff88'
    : safe < 30 ? '#ff0055' : safe < 60 ? '#ffe600' : color
  return (
    <div>
      <div className="mb-0.5 flex justify-between arcade-font text-[7px] text-[#555]">
        <span>{label}</span>
        <span>{safe}%</span>
      </div>
      <div className="h-1.5 overflow-hidden border border-[#1a1a2e] bg-black">
        <div
          className="h-full transition-all duration-300"
          style={{ width: `${safe}%`, background: barColor }}
        />
      </div>
    </div>
  )
}

export function CircularGauge({
  label,
  value,
  color,
  track = '#14212d',
}: {
  label: string
  value: number
  color: string
  track?: string
}) {
  const safe = Math.max(0, Math.min(100, Math.round(value)))
  const radius = 27
  const circumference = 2 * Math.PI * radius
  const offset = circumference * (1 - safe / 100)

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative h-20 w-20">
        <svg className="h-20 w-20 -rotate-90" viewBox="0 0 72 72">
          <circle cx="36" cy="36" r={radius} fill="none" stroke={track} strokeWidth="6" />
          <circle
            cx="36"
            cy="36"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ filter: `drop-shadow(0 0 8px ${color})` }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className="pixel-font text-[16px]" style={{ color }}>{safe}</div>
          <div className="arcade-font text-[8px] text-[#9fb0bf]">%</div>
        </div>
      </div>
      <div className="arcade-font text-[10px] tracking-widest" style={{ color }}>
        {label}
      </div>
    </div>
  )
}

export function StatLine({ label, j, a }: { label: string; j: any; a: any }) {
  return (
    <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-3 arcade-font text-[13px]">
      <div className="text-[#00ff88]">{j}</div>
      <div className="text-center text-[12px] text-[#c6d8e8]">{label}</div>
      <div className="text-right text-[#ff8d6d]">{a}</div>
    </div>
  )
}

export function InlineMeter({ value, color }: { value: number; color: string }) {
  const blocks = 10
  const filled = Math.round((Math.min(100, Math.max(0, value)) / 100) * blocks)
  return (
    <div className="flex gap-[2px]">
      {Array.from({ length: blocks }).map((_, i) => (
        <div
          key={i}
          className="h-[8px] flex-1"
          style={{
            background: i < filled ? color : '#1a1f27',
            boxShadow: i < filled && i === filled - 1 ? `0 0 6px ${color}` : 'none',
          }}
        />
      ))}
    </div>
  )
}

export function TacticalPackageEditor({
  mentalidade,
  abordagem,
  instrucao,
  segundoSaque,
  setMentalidade,
  setAbordagem,
  setInstrucao,
  setSegundoSaque,
  compact = false,
}: {
  mentalidade: MentalidadeValor
  abordagem: AbordagemValor
  instrucao: InstrucaoValor
  segundoSaque: SegundoSaqueModo
  setMentalidade: (valor: MentalidadeValor) => void
  setAbordagem: (valor: AbordagemValor) => void
  setInstrucao: (valor: InstrucaoValor) => void
  setSegundoSaque: (valor: SegundoSaqueModo) => void
  compact?: boolean
}) {
  const sectionLabel = compact ? 'text-[9px]' : 'text-[10px]'
  const itemLabel = compact ? 'text-[10px]' : 'text-[11px]'
  const itemDesc = compact ? 'text-[8px]' : 'text-[9px]'
  const buttonPadding = compact ? 'p-2.5' : 'p-3'
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <div>
        <div className={`arcade-font ${sectionLabel} mb-2 tracking-widest text-[#8fa3b5] uppercase`}>Mentalidade</div>
        <div className="space-y-2">
          {MENTALIDADES.map(m => (
            <button
              key={m.valor}
              onClick={() => setMentalidade(m.valor)}
              className={`w-full ${buttonPadding} flex items-center justify-between border-2 text-left transition-all`}
              style={{
                borderColor: mentalidade === m.valor ? m.color : '#1a1a2e',
                background: mentalidade === m.valor ? `${m.color}15` : 'transparent',
                boxShadow: mentalidade === m.valor ? `0 0 15px ${m.color}20` : 'none',
              }}
            >
              <div className="flex items-center gap-3">
                <span className={compact ? 'text-base' : 'text-lg'}>{m.emoji}</span>
                <div>
                  <div className={`arcade-font ${itemLabel}`} style={{ color: mentalidade === m.valor ? m.color : '#d6e0ea' }}>{m.label}</div>
                  <div className={`arcade-font ${itemDesc} text-[#8ea3b7]`}>{m.desc}</div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div>
        <div className={`arcade-font ${sectionLabel} mb-2 tracking-widest text-[#8fa3b5] uppercase`}>Abordagem</div>
        <div className="space-y-2">
          {ABORDAGENS.map(a => (
            <button
              key={a.valor}
              onClick={() => setAbordagem(a.valor)}
              className={`w-full ${buttonPadding} flex items-center justify-between border-2 text-left transition-all`}
              style={{
                borderColor: abordagem === a.valor ? '#ffe600' : '#1a1a2e',
                background: abordagem === a.valor ? '#ffe6000a' : 'transparent',
              }}
            >
              <div className="flex items-center gap-3">
                <span className={compact ? 'text-base' : 'text-lg'}>{a.icon}</span>
                <div>
                  <div className={`arcade-font ${itemLabel}`} style={{ color: abordagem === a.valor ? '#ffe600' : '#d6e0ea' }}>{a.label}</div>
                  <div className={`arcade-font ${itemDesc} text-[#9fb0bf]`}>{a.desc}</div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div>
        <div className={`arcade-font ${sectionLabel} mb-2 tracking-widest text-[#8fa3b5] uppercase`}>Instrução Específica</div>
        <div className="space-y-2">
          {INSTRUCOES.map(i => (
            <button
              key={i.valor}
              onClick={() => setInstrucao(i.valor)}
              className={`w-full ${buttonPadding} border-2 text-left transition-all`}
              style={{
                borderColor: instrucao === i.valor ? '#00ff88' : '#1a1a2e',
                background: instrucao === i.valor ? '#00ff880a' : 'transparent',
              }}
            >
              <div className="flex items-center gap-3">
                <span className={compact ? 'text-sm' : 'text-base'}>{i.emoji}</span>
                <div>
                  <div className={`arcade-font ${itemLabel}`} style={{ color: instrucao === i.valor ? '#00ff88' : '#d6e0ea' }}>{i.label}</div>
                  <div className={`arcade-font ${itemDesc} mt-1 text-[#9fb0bf]`}>{i.desc}</div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div>
        <div className={`arcade-font ${sectionLabel} mb-2 tracking-widest text-[#8fa3b5] uppercase`}>Segundo Saque</div>
        <div className="space-y-2">
          {([
            {
              valor: 'SEGURO' as SegundoSaqueModo,
              label: '🛡️ SEGURO',
              desc: 'Menos dupla falta, menos pressão imediata.',
              color: '#00ff88',
            },
            {
              valor: 'FORCAR' as SegundoSaqueModo,
              label: '⚡ FORÇAR',
              desc: 'Mais agressão no 2º saque, com risco maior.',
              color: '#ffe600',
            },
          ]).map((opcao) => (
            <button
              key={opcao.valor}
              onClick={() => setSegundoSaque(opcao.valor)}
              className={`w-full border px-3 ${compact ? 'py-2.5' : 'py-3'} text-left transition-all`}
              style={{
                borderColor: segundoSaque === opcao.valor ? opcao.color : '#1a1a2e',
                background: segundoSaque === opcao.valor ? `${opcao.color}10` : 'transparent',
              }}
            >
              <div className={`arcade-font ${itemLabel}`} style={{ color: segundoSaque === opcao.valor ? opcao.color : '#d6e0ea' }}>
                {opcao.label}
              </div>
              <div className={`arcade-font ${itemDesc} mt-1 text-[#9fb0bf]`}>{opcao.desc}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
