import { ArrowLeft } from 'lucide-react'
import { FutCard } from '../../../components/FutCard'
import { NeonButton } from '../../../components/NeonButton'
import { COURT_COLORS, MODOS_ACOMP, MODOS_VISIVEIS } from '../constants'
import type { AdversarioInfo, JogadorState, ModoAcomp } from '../types'

export function SetupHeader({
  faseTorneio,
  superficie,
  surface,
  onBack,
}: {
  faseTorneio: string
  superficie: string
  surface: string
  onBack: () => void
}) {
  return (
    <div className="app-panel match-topbar p-4 border-b-2 border-neon-green flex items-center justify-between shrink-0">
      <div className="flex items-center gap-3">
        <button onClick={onBack} className="text-neon-green hover:scale-110 transition-transform">
          <ArrowLeft size={22} />
        </button>
        <div>
          <div className="arcade-font text-[10px] text-neon-green tracking-[0.2em]">VESTIÁRIO</div>
          <div className="arcade-font text-[12px] text-white mt-0.5">
            {faseTorneio ? faseTorneio.replaceAll('_', ' ').toUpperCase() : 'PARTIDA'}
          </div>
        </div>
      </div>
      {superficie && (
        <div className="flex flex-col items-end">
          <div className="arcade-font text-[8px] text-[#555] mb-1">QUADRA</div>
          <div className="flex items-center gap-2">
            <div
              className="h-2 w-6 border border-white/20"
              style={{ background: COURT_COLORS[surface as keyof typeof COURT_COLORS] }}
            />
            <span className="arcade-font text-[10px] text-white">{superficie.toUpperCase()}</span>
          </div>
        </div>
      )}
    </div>
  )
}

export function MatchBriefingPanel({
  contexto,
  briefing,
  nomeTorneio,
}: {
  contexto: { cor: string; label: string; texto: string }
  briefing: { manchete: string; contexto: string; conflito: string; plano: string }
  nomeTorneio?: string
}) {
  return (
    <>
      <div
        className="border-l-4 px-4 py-3 flex items-start gap-3"
        style={{ borderColor: contexto.cor, background: `${contexto.cor}10` }}
      >
        <div className="shrink-0 arcade-font text-[14px]" aria-hidden="true">
          {contexto.label.split(' ')[0]}
        </div>
        <div className="min-w-0">
          <div className="arcade-font text-ui-tag tracking-widest mb-1" style={{ color: contexto.cor }}>
            {contexto.label.replace(/^[^\s]+\s/, '')}
          </div>
          <div className="arcade-font text-ui-body text-[#9ab0bc] leading-relaxed">{contexto.texto}</div>
        </div>
      </div>

      <div className="app-panel match-card border border-white/10 p-4 space-y-3">
        <div className="flex items-center justify-between gap-3">
          <div>
            <div className="arcade-font text-ui-tag tracking-widest text-neon-cyan">BRIEFING DA PARTIDA</div>
            <div className="pixel-font text-ui-body text-white mt-1">{briefing.manchete}</div>
          </div>
          <div className="arcade-font text-ui-label text-[#5d7380] text-right">
            {nomeTorneio ? nomeTorneio.toUpperCase() : 'CIRCUITO'}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <BriefingItem title="CONTEXTO" colorClass="text-neon-green" text={briefing.contexto} />
          <BriefingItem title="CONFLITO" colorClass="text-neon-yellow" text={briefing.conflito} />
          <BriefingItem title="PLANO" colorClass="text-neon-cyan" text={briefing.plano} />
        </div>
      </div>
    </>
  )
}

function BriefingItem({ title, colorClass, text }: { title: string; colorClass: string; text: string }) {
  return (
    <div className="match-card-soft border border-white/10 p-3">
      <div className={`arcade-font text-ui-label tracking-widest ${colorClass} mb-2`}>{title}</div>
      <div className="arcade-font text-ui-body text-[#c8d8e0] leading-relaxed">{text}</div>
    </div>
  )
}

export function MatchupCards({
  jogador,
  adversario,
  overallCardJogador,
  rankingJogador,
  overallCardAdversario,
  rankingAdversario,
}: {
  jogador: JogadorState | null
  adversario: AdversarioInfo
  overallCardJogador: number
  rankingJogador: number | null
  overallCardAdversario: number
  rankingAdversario: number | null
}) {
  const tour = (jogador?.tour ?? 'atp').toLowerCase() as 'atp' | 'wta'

  return (
    <div className="match-hero flex flex-col lg:flex-row gap-6 items-center justify-center py-4">
      <div className="flex flex-col items-center gap-2">
        <div className="arcade-font text-[10px] text-neon-green tracking-widest uppercase mb-2">SEU JOGADOR</div>
        <FutCard
          nome={jogador?.nome ?? 'VOCÊ'}
          nacionalidade={jogador?.nacionalidade ?? ''}
          overall={overallCardJogador}
          tour={tour}
          ranking={rankingJogador ?? 0}
          nivel={jogador?.nivel ?? 1}
          atributos={jogador?.atributos ?? {}}
          atributosPsicologicos={jogador?.atributos_psicologicos ?? {}}
          cartaTipo={jogador?.carta?.tipo}
          cartaRaridade={jogador?.carta?.raridade}
          cartaCor={jogador?.carta?.cor_primaria}
          overallBoosted={jogador?.carta?.overall_boosted}
          atributosBoosted={jogador?.carta?.atributos_boosted}
        />
      </div>

      <div className="flex items-center justify-center">
        <div className="arcade-font text-[24px] text-white/20 italic select-none">VS</div>
      </div>

      <div className="flex flex-col items-center gap-2">
        <div className="arcade-font text-[10px] text-[#ff4466] tracking-widest uppercase mb-2">ADVERSÁRIO</div>
        <FutCard
          nome={adversario.nome}
          nacionalidade={adversario.nacionalidade ?? ''}
          overall={overallCardAdversario}
          tour={tour}
          ranking={rankingAdversario ?? 0}
          nivel={1}
          atributos={adversario.atributos ?? {}}
          atributosPsicologicos={adversario.atributosPsicologicos ?? {}}
          cartaTipo={adversario.carta?.tipo}
          cartaRaridade={adversario.carta?.raridade}
          cartaCor={adversario.carta?.cor_primaria}
          overallBoosted={adversario.overallBoosted}
          atributosBoosted={adversario.atributosBoosted}
        />
      </div>
    </div>
  )
}

export function ExperienceModePanel({
  modo,
  trocarModoAcompanhamento,
}: {
  modo: ModoAcomp
  trocarModoAcompanhamento: (m: ModoAcomp) => void
}) {
  return (
    <div className="app-panel border border-white/5 p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="arcade-font text-[10px] text-[#b7c4d1] tracking-widest uppercase">Velocidade da Experiência</div>
        <div className="arcade-font text-[10px] text-neon-yellow">{MODOS_ACOMP.find(m => m.valor === modo)?.label}</div>
      </div>
      <div className="mb-3 arcade-font text-[10px] text-[#95a7b5] leading-relaxed">
        Escolha só entre manual, rápida ou simular até o fim.
      </div>
      <div className="grid grid-cols-3 gap-2">
        {MODOS_VISIVEIS.map(m => (
          <button
            key={m.valor}
            onClick={() => trocarModoAcompanhamento(m.valor)}
            className="py-2.5 border arcade-font text-[9px] transition-all"
            style={{
              borderColor: modo === m.valor ? 'var(--neon-green)' : '#1a1a2e',
              background: modo === m.valor ? '#00ff8812' : 'transparent',
              color: modo === m.valor ? 'var(--neon-green)' : '#c4d1dc',
            }}
          >
            {m.label}
          </button>
        ))}
      </div>
    </div>
  )
}

export function StickyStartBar({
  erroEntrada,
  handleIniciar,
  simulando,
  confirmandoEntrada,
}: {
  erroEntrada: string
  handleIniciar: () => void
  simulando: boolean
  confirmandoEntrada: boolean
}) {
  return (
    <div className="sticky bottom-0 z-30 p-4 border-t border-white/10 bg-black/80 backdrop-blur-md">
      {erroEntrada && (
        <div className="mb-3 border border-[#ff4466] bg-[#22040d] px-3 py-2 arcade-font text-[10px] text-[#ff9bb4]">
          {erroEntrada.toUpperCase()}
        </div>
      )}
      <NeonButton variant="green" className="w-full py-5 text-sm" onClick={handleIniciar} blink={simulando}>
        {simulando ? 'CALCULANDO ESTRATÉGIAS...' : confirmandoEntrada ? 'CONFIRMAR E ENTRAR EM QUADRA' : 'DEFINIR PLANO E JOGAR'}
      </NeonButton>
    </div>
  )
}
