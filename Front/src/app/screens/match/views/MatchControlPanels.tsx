import { AnimatePresence, motion } from 'motion/react'
import { NeonButton } from '../../../components/NeonButton'
import { INTENCOES, TacticalPackageEditor } from '../components'
import {
  ALVOS,
  FAIXAS,
  PLANOS,
  VELOCIDADES_RAPIDAS,
} from '../constants'
import {
  resumoModo,
  resumoMomentum,
} from '../scouting'
import type { Alvo, Faixa, GameResult, ModoAcomp, PlanoValor, VelocidadeRapida } from '../types'
import type { PlacarState } from '../../../../types'
import type { TacticalPackageControls } from './MatchControls'

interface RapidSimulationPanelProps extends TacticalPackageControls {
  fase: string
  modo: ModoAcomp
  partidaId: string | null
  simulacaoPausada: boolean
  alternarPausaSimulacao: () => void
  velocidadeRapidaAtual: { label: string }
  velocidadeRapida: VelocidadeRapida
  setVelocidadeRapida: (v: VelocidadeRapida) => void
  ajustandoPlanoRapido: boolean
  setAjustandoPlanoRapido: (v: any) => void
  handleAplicarPausaRapida: () => void
}

export function RapidSimulationPanel({
  fase,
  modo,
  partidaId,
  simulacaoPausada,
  alternarPausaSimulacao,
  velocidadeRapidaAtual,
  velocidadeRapida,
  setVelocidadeRapida,
  ajustandoPlanoRapido,
  setAjustandoPlanoRapido,
  handleAplicarPausaRapida,
  ...tactical
}: RapidSimulationPanelProps) {
  if (fase === 'encerrada' || fase === 'entre-games' || fase === 'entre-sets' || modo !== 'detalhado') {
    return null
  }

  return (
    <div className="border border-neon-yellow/25 bg-[#110d02] p-3 space-y-3">
      <div className="flex items-center justify-between gap-3">
        <div>
          <div className="arcade-font text-[8px] tracking-widest text-neon-yellow">SIMULAÇÃO RÁPIDA</div>
          <div className="arcade-font text-[9px] text-[#c8b877] mt-1">
            Velocidade atual: {velocidadeRapidaAtual.label} · {simulacaoPausada ? 'pausada' : 'rodando'}
          </div>
        </div>
        <button
          onClick={alternarPausaSimulacao}
          disabled={!partidaId || fase === 'jogando'}
          className="border px-3 py-2 arcade-font text-[8px] transition-all disabled:opacity-40"
          style={{
            borderColor: simulacaoPausada ? 'var(--neon-green)' : 'var(--neon-yellow)',
            color: simulacaoPausada ? 'var(--neon-green)' : 'var(--neon-yellow)',
            background: simulacaoPausada ? '#00ff8810' : '#ffe60010',
          }}
        >
          {simulacaoPausada ? 'CONTINUAR' : 'PAUSAR'}
        </button>
      </div>

      <div className="grid grid-cols-4 gap-2">
        {VELOCIDADES_RAPIDAS.map((item) => (
          <button
            key={item.valor}
            onClick={() => setVelocidadeRapida(item.valor)}
            className="border px-2 py-2 text-center transition-all"
            style={{
              borderColor: velocidadeRapida === item.valor ? 'var(--neon-yellow)' : '#3a3220',
              background: velocidadeRapida === item.valor ? '#ffe60012' : 'transparent',
              color: velocidadeRapida === item.valor ? 'var(--neon-yellow)' : '#bcae72',
            }}
          >
            <div className="arcade-font text-[9px]">{item.label}</div>
            <div className="arcade-font text-[7px] mt-1 opacity-80">{item.desc}</div>
          </button>
        ))}
      </div>

      {simulacaoPausada && (
        <div className="border border-neon-cyan/20 bg-[#04101b] p-3 space-y-3">
          <div className="flex items-center justify-between gap-3">
            <div>
              <div className="arcade-font text-[8px] tracking-widest text-neon-cyan">PAINEL TÁTICO</div>
              <div className="arcade-font text-[9px] text-[#90b8c9] mt-1">
                Pause, ajuste o plano e retome a simulação.
              </div>
            </div>
            <button
              onClick={() => setAjustandoPlanoRapido((atual: boolean) => !atual)}
              className="border px-3 py-2 arcade-font text-[8px] text-neon-cyan transition-all"
              style={{ borderColor: '#00e5ff33', background: ajustandoPlanoRapido ? '#00e5ff10' : 'transparent' }}
            >
              {ajustandoPlanoRapido ? 'OCULTAR' : 'AJUSTAR'}
            </button>
          </div>

          {ajustandoPlanoRapido && (
            <>
              <TacticalPackageEditor {...tactical} compact />
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => {
                    setAjustandoPlanoRapido(false)
                    alternarPausaSimulacao()
                  }}
                  className="py-3 border border-neon-cyan/25 arcade-font text-[9px] text-[#9ac9d8] text-center transition-all hover:border-neon-cyan/60"
                >
                  SEGUIR SEM MUDAR
                </button>
                <NeonButton variant="cyan" className="text-[10px] py-3" onClick={handleAplicarPausaRapida}>
                  APLICAR E CONTINUAR
                </NeonButton>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}

export function FinishedResultCard({ fase, placar }: { fase: string; placar: PlacarState }) {
  return (
    <AnimatePresence>
      {fase === 'encerrada' && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`border-2 p-8 text-center ${
            placar.vencedor === 'jogador' ? 'border-neon-green bg-[#001a10]' : 'border-neon-pink bg-[#1a0010]'
          }`}
        >
          <div className={`pixel-font text-4xl mb-3 ${placar.vencedor === 'jogador' ? 'text-neon-green' : 'text-neon-pink'}`}>
            {placar.vencedor === 'jogador' ? 'VITÓRIA!' : 'DERROTA'}
          </div>
          <div className="arcade-font text-base text-[#888]">
            {placar.placar_final || `${placar.sets[0]} × ${placar.sets[1]} sets`}
          </div>
          <div className="arcade-font text-[8px] text-[#7a8994] mt-3 tracking-widest">
            RESUMO DA PARTIDA EM INSTANTES...
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

interface BetweenGamesPanelProps extends TacticalPackageControls {
  fase: string
  gameResult: GameResult | null
  momentum: number
  planoAtual: { color: string; label: string }
  ajustandoPlanoGame: boolean
  setAjustandoPlanoGame: (v: boolean) => void
  handleContinuarGame: () => void
  simulando: boolean
}

export function BetweenGamesPanel({
  fase,
  gameResult,
  momentum,
  planoAtual,
  ajustandoPlanoGame,
  setAjustandoPlanoGame,
  handleContinuarGame,
  simulando,
  ...tactical
}: BetweenGamesPanelProps) {
  return (
    <AnimatePresence>
      {fase === 'entre-games' && gameResult && (
        <motion.div
          key="entre-games"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="border-2 border-neon-cyan bg-[#00040d] p-4"
          style={{ boxShadow: '0 0 16px rgba(0,229,255,0.15)' }}
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="arcade-font text-[12px]" style={{ color: gameResult.quemGanhou === 'jogador' ? 'var(--neon-green)' : '#ff4466' }}>
                {gameResult.quemGanhou === 'jogador' ? '✓ GAME GANHO' : '✗ GAME PERDIDO'}
              </div>
              {gameResult.foiBreak && (
                <div className="arcade-font text-[9px] mt-0.5" style={{ color: gameResult.quemGanhou === 'jogador' ? '#ff9900' : '#ff4444' }}>
                  {gameResult.quemGanhou === 'jogador' ? '⚡ BREAK!' : '⚡ BREAK SOFRIDO'}
                </div>
              )}
            </div>
            <div className="arcade-font text-[13px] text-[#888]">
              {gameResult.placarGames[0]} – {gameResult.placarGames[1]}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="border border-neon-cyan/20 bg-[#04101b] px-3 py-2">
              <div className="arcade-font text-[7px] text-[#5ba6bd] tracking-widest mb-1">MOMENTO</div>
              <div className="arcade-font text-[9px] text-[#d6f2ff] uppercase">{resumoMomentum(momentum)}</div>
            </div>
            <div className="border border-neon-cyan/20 bg-[#04101b] px-3 py-2">
              <div className="arcade-font text-[7px] text-[#5ba6bd] tracking-widest mb-1">PLANO ATUAL</div>
              <div className="arcade-font text-[9px]" style={{ color: planoAtual.color }}>
                {planoAtual.label}
              </div>
            </div>
          </div>

          {ajustandoPlanoGame ? (
            <div className="space-y-4">
              <div className="border border-neon-cyan/20 bg-[#04101b] p-3">
                <div className="arcade-font text-[8px] text-[#5ba6bd] tracking-widest mb-3">MUDAR ESTRATÉGIA</div>
                <TacticalPackageEditor {...tactical} compact />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <button onClick={() => setAjustandoPlanoGame(false)} className="py-3 border border-neon-cyan/25 arcade-font text-[9px] text-[#9ac9d8] text-center transition-all hover:border-neon-cyan/60">
                  CANCELAR
                </button>
                <NeonButton variant="cyan" className="text-[10px] py-3" onClick={handleContinuarGame}>
                  APLICAR E JOGAR →
                </NeonButton>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-2">
              <button onClick={handleContinuarGame} disabled={simulando} className="py-3 border border-neon-cyan/30 arcade-font text-[9px] text-[#9ac9d8] text-center transition-all hover:text-neon-cyan hover:border-neon-cyan/60 disabled:opacity-30">
                MANTER ESTRATÉGIA
              </button>
              <NeonButton variant="cyan" className="text-[10px] py-3" onClick={() => setAjustandoPlanoGame(true)}>
                MUDAR ESTRATÉGIA →
              </NeonButton>
            </div>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  )
}

interface BetweenSetsModalProps extends TacticalPackageControls {
  fase: string
  placar: PlacarState
  energiaJogadorAoVivo: number
  fadigaJogadorAoVivo: number
  energiaAdversarioAoVivo: number
  fadigaAdversarioAoVivo: number
  ajustandoPlanoSet: boolean
  setAjustandoPlanoSet: (v: boolean) => void
  contadorSet: number
  handleContinuarSet: () => void
  handleEscolherPlanoSet: (p: PlanoValor) => void
  simulando: boolean
}

export function BetweenSetsModal({
  fase,
  placar,
  energiaJogadorAoVivo,
  fadigaJogadorAoVivo,
  energiaAdversarioAoVivo,
  fadigaAdversarioAoVivo,
  ajustandoPlanoSet,
  setAjustandoPlanoSet,
  contadorSet,
  handleContinuarSet,
  handleEscolherPlanoSet,
  simulando,
  ...tactical
}: BetweenSetsModalProps) {
  return (
    <AnimatePresence>
      {fase === 'entre-sets' && (
        <motion.div key="entre-sets" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-40 flex items-center justify-center bg-black/70 backdrop-blur-[2px] p-4">
          <motion.div initial={{ opacity: 0, y: 18, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: 12, scale: 0.98 }} className="w-full max-w-3xl max-h-[88vh] overflow-y-auto border-2 border-neon-yellow bg-[#0f0c00] p-5" style={{ boxShadow: '0 0 32px rgba(255,230,0,0.24)' }}>
            <div className="pixel-font text-[24px] text-neon-yellow text-center mb-2">SET ENCERRADO</div>
            <div className="arcade-font text-[11px] text-[#d6c97f] text-center mb-5 tracking-widest">
              {placar.sets[0]} × {placar.sets[1]} — AJUSTE TÁTICO
            </div>

            <div className="grid grid-cols-2 gap-4 mb-5">
              <SetEnergyCard title="VOCÊ" energia={energiaJogadorAoVivo} fadiga={fadigaJogadorAoVivo} />
              <SetEnergyCard title="ADVERSÁRIO" energia={energiaAdversarioAoVivo} fadiga={fadigaAdversarioAoVivo} />
            </div>

            {!ajustandoPlanoSet && (
              <div className="mb-4">
                <div className="flex items-center justify-between mb-1">
                  <span className="arcade-font text-[8px] text-neon-yellow/60 tracking-widest">AUTO-CONTINUA EM</span>
                  <span className="arcade-font text-[11px]" style={{ color: contadorSet <= 3 ? 'var(--neon-pink)' : 'var(--neon-yellow)' }}>{contadorSet}s</span>
                </div>
                <div className="h-1 bg-white/10 w-full">
                  <motion.div className="h-full" style={{ background: contadorSet <= 3 ? 'var(--neon-pink)' : 'var(--neon-yellow)', width: `${(contadorSet / 10) * 100}%` }} transition={{ duration: 0.3 }} />
                </div>
              </div>
            )}

            {ajustandoPlanoSet ? (
              <div className="space-y-4 mb-5">
                <div className="border border-neon-yellow/24 bg-[#140f02] p-4">
                  <div className="arcade-font text-[10px] text-[#d8c46c] tracking-widest mb-3">MUDAR ESTRATÉGIA</div>
                  <TacticalPackageEditor {...tactical} compact />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <button onClick={() => setAjustandoPlanoSet(false)} className="py-3.5 border border-neon-yellow/25 arcade-font text-[11px] text-[#d6c97f] text-center transition-all hover:border-neon-yellow/50">
                    CANCELAR
                  </button>
                  <NeonButton variant="yellow" className="text-[12px] py-3.5" onClick={handleContinuarSet}>
                    APLICAR E CONTINUAR →
                  </NeonButton>
                </div>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-3 gap-2 mb-4">
                  {PLANOS.map((p) => (
                    <button key={p.valor} onClick={() => handleEscolherPlanoSet(p.valor)} disabled={simulando} className="flex flex-col items-center gap-1.5 py-3 px-2 border-2 transition-all disabled:opacity-40 hover:scale-[1.02]" style={{ borderColor: p.color + '60', background: p.color + '0f' }} onMouseEnter={(e) => {
                      ;(e.currentTarget as HTMLElement).style.borderColor = p.color
                      ;(e.currentTarget as HTMLElement).style.background = p.color + '20'
                    }} onMouseLeave={(e) => {
                      ;(e.currentTarget as HTMLElement).style.borderColor = p.color + '60'
                      ;(e.currentTarget as HTMLElement).style.background = p.color + '0f'
                    }}>
                      <span className="arcade-font text-[9px] font-bold tracking-widest" style={{ color: p.color }}>{p.label}</span>
                      <span className="text-[8px] text-white/50 text-center leading-relaxed">{p.desc}</span>
                    </button>
                  ))}
                </div>
                <div className="grid grid-cols-2 gap-2 mb-5">
                  <button onClick={handleContinuarSet} disabled={simulando} className="py-3.5 border border-neon-yellow/35 arcade-font text-[11px] text-[#e5d57b] text-center transition-all hover:text-neon-yellow hover:border-neon-yellow/60 disabled:opacity-30">
                    MANTER ESTRATÉGIA
                  </button>
                  <NeonButton variant="yellow" className="text-[12px] py-3.5" onClick={() => setAjustandoPlanoSet(true)}>
                    AJUSTE DETALHADO →
                  </NeonButton>
                </div>
              </>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

function SetEnergyCard({ title, energia, fadiga }: { title: string; energia: number; fadiga: number }) {
  return (
    <div className="border border-neon-yellow/24 bg-[#140f02] px-4 py-3">
      <div className="arcade-font text-[10px] text-[#d8c46c] tracking-widest mb-2">{title}</div>
      <div className="arcade-font text-[13px] text-[#fff1a8]">Energia {Math.round(energia)}%</div>
      <div className="arcade-font text-[13px] text-[#ffd86d] mt-1.5">Fadiga {Math.round(fadiga)}%</div>
    </div>
  )
}

interface StrategistActionPanelProps {
  fase: string
  modo: ModoAcomp
  simulando: boolean
  intencaoAtiva: string | null
  handleIntencao: (i: string) => void
  expandirPonto: boolean
  setExpandirPonto: (v: any) => void
  faixa: Faixa
  setFaixa: (v: Faixa) => void
  alvo: Alvo
  setAlvo: (v: Alvo) => void
}

export function StrategistActionPanel({
  fase,
  modo,
  simulando,
  intencaoAtiva,
  handleIntencao,
  expandirPonto,
  setExpandirPonto,
  faixa,
  setFaixa,
  alvo,
  setAlvo,
}: StrategistActionPanelProps) {
  if (fase === 'encerrada' || fase === 'entre-games' || fase === 'entre-sets' || modo !== 'estrategista') return null

  return (
    <div className="border border-neon-cyan/30 bg-[#04101b]">
      <div className="arcade-font text-[8px] text-neon-cyan px-3 py-2 border-b border-neon-cyan/20 tracking-widest">
        ESCOLHA SUA AÇÃO
      </div>
      <div className="space-y-2 p-3">
        {INTENCOES.map((int) => (
          <button key={int.valor} onClick={() => handleIntencao(int.valor)} disabled={fase !== 'aguardando' || simulando} className="w-full border px-3 py-3 text-left transition-all disabled:opacity-25 active:scale-95" style={{ borderColor: intencaoAtiva === int.valor ? int.color : '#1f3340', background: intencaoAtiva === int.valor ? `${int.color}16` : 'transparent' }}>
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="arcade-font text-[10px] font-bold" style={{ color: int.color }}>{int.label}</div>
                <div className="arcade-font text-[9px] text-[#9fb8c7] mt-1">{int.sub}</div>
              </div>
              <div className="text-lg">{int.emoji}</div>
            </div>
          </button>
        ))}
      </div>
      <div className="border-t border-neon-cyan/15 px-3 py-3">
        <div className="flex items-center justify-between gap-3">
          <div>
            <div className="arcade-font text-[8px] text-[#8aaac0] tracking-widest">AJUSTE FINO</div>
            <div className="arcade-font text-[9px] text-[#6f8798] mt-1">
              Se você não abrir, o jogo escolhe faixa e alvo compatíveis com a intenção.
            </div>
          </div>
          <button onClick={() => setExpandirPonto((prev: boolean) => !prev)} className="px-3 py-2 border arcade-font text-[8px] transition-all" style={{ borderColor: expandirPonto ? 'var(--neon-cyan)' : '#1a1a2e', color: expandirPonto ? 'var(--neon-cyan)' : '#66748d', background: expandirPonto ? '#00e5ff10' : 'transparent' }}>
            {expandirPonto ? 'OCULTAR' : 'AJUSTAR'}
          </button>
        </div>

        {expandirPonto && (
          <div className="mt-3 grid grid-cols-1 gap-3">
            <ChoiceGroup title="FAIXA" items={FAIXAS} value={faixa} activeColor="var(--neon-cyan)" inactiveColor="#7a8793" onChange={setFaixa} />
            <ChoiceGroup title="ALVO" items={ALVOS} value={alvo} activeColor="var(--neon-yellow)" inactiveColor="#8d8a6d" onChange={setAlvo} />
          </div>
        )}
      </div>
    </div>
  )
}

function ChoiceGroup<T extends string>({
  title,
  items,
  value,
  activeColor,
  inactiveColor,
  onChange,
}: {
  title: string
  items: Array<{ valor: T; label: string }>
  value: T
  activeColor: string
  inactiveColor: string
  onChange: (value: T) => void
}) {
  return (
    <div>
      <div className="arcade-font text-[8px] text-[#7e97a8] mb-2">{title}</div>
      <div className="space-y-2">
        {items.map((item) => (
          <button key={item.valor} onClick={() => onChange(item.valor)} className="w-full py-2 border text-left px-3 text-[8px] arcade-font transition-all" style={{ borderColor: value === item.valor ? activeColor : '#1a1a2e', color: value === item.valor ? activeColor : inactiveColor, background: value === item.valor ? `${activeColor}10` : 'transparent' }}>
            {item.label}
          </button>
        ))}
      </div>
    </div>
  )
}

export function SimulatingIndicator({ simulando }: { simulando: boolean }) {
  if (!simulando) return null
  return (
    <motion.div animate={{ opacity: [1, 0.4, 1] }} transition={{ duration: 0.6, repeat: Infinity }} className="text-center arcade-font text-[10px] text-neon-yellow py-2">
      ● SIMULANDO...
    </motion.div>
  )
}

export function PassiveModeStatus({
  fase,
  modo,
  simulando,
  trocarModoAcompanhamento,
}: {
  fase: string
  modo: ModoAcomp
  simulando: boolean
  trocarModoAcompanhamento: (m: ModoAcomp) => void
}) {
  if (fase === 'encerrada' || fase === 'entre-games' || fase === 'entre-sets' || (modo !== 'game' && modo !== 'auto')) return null

  return (
    <div className="border border-[#1a1a2e] bg-black px-3 py-4">
      {simulando ? (
        <motion.div animate={{ opacity: [1, 0.4, 1] }} transition={{ duration: 0.5, repeat: Infinity }} className="arcade-font text-[10px] text-neon-cyan text-center">
          ● SIMULANDO...
        </motion.div>
      ) : (
        <div className="space-y-2">
          <div className="arcade-font text-[9px] text-[#93a4b2] uppercase">{resumoModo(modo)}</div>
          <button onClick={() => trocarModoAcompanhamento('estrategista')} className="w-full border border-[#1f3340] px-3 py-2 arcade-font text-[9px] text-neon-cyan transition-all hover:bg-[#00e5ff10]">
            VOLTAR PARA O CONTROLE MANUAL
          </button>
        </div>
      )}
    </div>
  )
}
