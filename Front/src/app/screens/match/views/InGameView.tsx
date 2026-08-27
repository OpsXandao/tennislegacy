import { ArrowLeft, Users, TrendingUp } from 'lucide-react'
import { BroadcastStatsCard } from './BroadcastStatsCard'
import { InlineMeter } from '../components'
import { corMomentum } from '../scoreUtils'
import { resumoModo } from '../scouting'
import { getContextoArena } from '../uiUtils'
import { MatchDramaOverlay } from '../MatchDramaOverlay'
import { MatchControls } from './MatchControls'
import type {
  AdversarioInfo,
  Alvo,
  Faixa,
  Fase,
  GameResult,
  InstrucaoValor,
  MentalidadeValor,
  ModoAcomp,
  PlanoValor,
  PlacarState,
  SegundoSaqueModo,
  VelocidadeRapida,
  AbordagemValor,
} from '../types'

interface InGameViewProps {
  themeClass: string
  nomeJogador: string
  adversario: AdversarioInfo
  placar: PlacarState
  superficie: string
  tipoTorneio?: string
  momentum: number
  destaqueMomento: string
  destaqueMomentoCor: string
  pulsoNarrativo: any
  leituraJogador: string
  leituraRival: string
  energiaJogadorAoVivo: number
  fadigaJogadorAoVivo: number
  energiaAdversarioAoVivo: number
  fadigaAdversarioAoVivo: number
  resumoEstrategiaJogador: string[]
  resumoEstrategiaAdversario: string[]
  planoAtual: { label: string; color: string; desc: string }
  segundoSaque: SegundoSaqueModo
  fase: Fase
  modo: ModoAcomp
  partidaId: string | null
  simulando: boolean
  simulacaoPausada: boolean
  velocidadeRapidaAtual: { label: string }
  velocidadeRapida: VelocidadeRapida
  ajustandoPlanoRapido: boolean
  mentalidade: MentalidadeValor
  abordagem: AbordagemValor
  instrucao: InstrucaoValor
  gameResult: GameResult | null
  ajustandoPlanoGame: boolean
  ajustandoPlanoSet: boolean
  contadorSet: number
  intencaoAtiva: string | null
  expandirPonto: boolean
  pointInsights: string[]
  faixa: Faixa
  alvo: Alvo
  pontoCritico: { label: string; color: string } | null
  isTiebreak: boolean
  isComeback: boolean
  crowdRoar?: boolean
  quimicaJogador?: { label: string; bonus_total: number; detalhes: string }
  quimicaAdversario?: { label: string; bonus_total: number; detalhes: string }
  onBack: () => void
  onSurrender: () => void
  alternarPausaSimulacao: () => void
  setVelocidadeRapida: (v: VelocidadeRapida) => void
  setAjustandoPlanoRapido: (v: boolean | ((current: boolean) => boolean)) => void
  setMentalidade: (v: MentalidadeValor) => void
  setAbordagem: (v: AbordagemValor) => void
  setInstrucao: (v: InstrucaoValor) => void
  setSegundoSaque: (v: SegundoSaqueModo) => void
  handleAplicarPausaRapida: () => void
  setAjustandoPlanoGame: (v: boolean) => void
  handleContinuarGame: () => void
  setAjustandoPlanoSet: (v: boolean) => void
  handleContinuarSet: () => void
  handleEscolherPlanoSet: (p: PlanoValor) => void
  handleIntencao: (i: string) => void
  setExpandirPonto: (v: boolean | ((current: boolean) => boolean)) => void
  setFaixa: (v: Faixa) => void
  setAlvo: (v: Alvo) => void
  trocarModoAcompanhamento: (m: ModoAcomp) => void
}

export function InGameView({
  themeClass,
  nomeJogador,
  adversario,
  placar,
  superficie,
  tipoTorneio,
  momentum,
  destaqueMomento,
  destaqueMomentoCor,
  pulsoNarrativo,
  leituraJogador,
  leituraRival,
  energiaJogadorAoVivo,
  fadigaJogadorAoVivo,
  energiaAdversarioAoVivo,
  fadigaAdversarioAoVivo,
  resumoEstrategiaJogador,
  resumoEstrategiaAdversario,
  planoAtual,
  segundoSaque,
  fase,
  modo,
  partidaId,
  simulando,
  simulacaoPausada,
  velocidadeRapidaAtual,
  velocidadeRapida,
  ajustandoPlanoRapido,
  mentalidade,
  abordagem,
  instrucao,
  gameResult,
  ajustandoPlanoGame,
  ajustandoPlanoSet,
  contadorSet,
  intencaoAtiva,
  expandirPonto,
  pointInsights,
  faixa,
  alvo,
  pontoCritico,
  isTiebreak,
  isComeback,
  crowdRoar,
  quimicaJogador,
  quimicaAdversario,
  onBack,
  onSurrender,
  alternarPausaSimulacao,
  setVelocidadeRapida,
  setAjustandoPlanoRapido,
  setMentalidade,
  setAbordagem,
  setInstrucao,
  setSegundoSaque,
  handleAplicarPausaRapida,
  setAjustandoPlanoGame,
  handleContinuarGame,
  setAjustandoPlanoSet,
  handleContinuarSet,
  handleEscolherPlanoSet,
  handleIntencao,
  setExpandirPonto,
  setFaixa,
  setAlvo,
  trocarModoAcompanhamento,
}: InGameViewProps) {
  const dramaColor = pontoCritico?.color ?? null
  const isFatigued = fadigaJogadorAoVivo > 75
  const hasHighMomentum = momentum > 80
  const arena = getContextoArena(tipoTorneio)
  const isGrandSlam = tipoTorneio?.toLowerCase().includes('grand') || tipoTorneio?.toLowerCase() === 'grand slam'

  return (
    <div className={[
      'app-shell match-theme-screen min-h-screen flex flex-col',
      themeClass,
      isFatigued ? 'fatigue-glitch' : '',
      crowdRoar ? 'crowd-roar-active' : '',
      isGrandSlam ? 'match-grandslam-final' : '',
    ].filter(Boolean).join(' ')}>
      <MatchDramaOverlay pontoCritico={pontoCritico} isTiebreak={isTiebreak} isComeback={isComeback} crowdRoar={crowdRoar} />

      {/* Arena Context Bar */}
      <div className="bg-black/40 px-3 py-1 flex items-center justify-between border-b border-white/5 relative z-30">
        <div className="flex items-center gap-1.5 arcade-font text-[7px] text-[#666]">
          <span>{arena.icon}</span>
          <span>{arena.estadio}</span>
        </div>
        
        {/* Química de Duplas (Link visual FIFA/FM style) */}
        <div className="flex-1 flex justify-center">
          {quimicaJogador?.label && (
             <div className="flex items-center gap-2 px-3 py-0.5 bg-black/60 border-x border-neon-cyan/20">
               <TrendingUp size={10} className="text-neon-cyan" />
               <span className="text-[7px] arcade-font text-white tracking-widest">
                LINK: <span className="text-neon-cyan">{quimicaJogador.label}</span>
               </span>
               <div className="flex gap-0.5 ml-1">
                 {[1, 2, 3].map(i => (
                   <div 
                    key={i} 
                    className={`w-1 h-1 rounded-full ${i <= (quimicaJogador.bonus_total / 3) ? 'bg-neon-cyan animate-pulse' : 'bg-white/10'}`} 
                   />
                 ))}
               </div>
             </div>
          )}
        </div>

        <div className="flex items-center gap-1.5 arcade-font text-[7px] text-[#666]">
          <Users size={8} />
          <span>ENERGIA: {arena.energia}</span>
        </div>
      </div>

      <div
        className="app-panel match-topbar sticky top-0 z-20 p-3 border-b-2 flex items-center gap-3 shrink-0 backdrop-blur-md transition-colors duration-300"
        style={{ 
          borderColor: dramaColor ?? (hasHighMomentum ? 'var(--neon-gold)' : 'var(--neon-green)'),
          boxShadow: hasHighMomentum ? '0 0 15px rgba(255, 230, 0, 0.4)' : 'none'
        }}
      >
        <button onClick={onBack} className="text-neon-green hover:scale-110 transition-transform">
          <ArrowLeft size={18} />
        </button>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <span className="arcade-font text-[9px] text-white truncate max-w-[100px]">{nomeJogador}</span>
            <div className="flex gap-2 arcade-font text-[10px]">
              <span className={placar.sets[0] > placar.sets[1] ? 'text-neon-green' : 'text-[#444]'}>{placar.sets[0]}</span>
              <span className="text-[#222]">|</span>
              <span className={placar.sets[1] > placar.sets[0] ? 'text-[#ff4466]' : 'text-[#444]'}>{placar.sets[1]}</span>
            </div>
            <span className="arcade-font text-[9px] text-white truncate max-w-[100px] text-right">{adversario.nome}</span>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3 pb-4">
        <div
          className={`match-card match-card-player border p-3 transition-all duration-300 ${hasHighMomentum ? 'momentum-glow' : ''}`}
          style={{
            borderColor: dramaColor ? dramaColor : (hasHighMomentum ? 'var(--neon-gold)' : 'rgba(0,255,136,0.30)'),
            boxShadow: dramaColor ? `0 0 10px ${dramaColor}33, 0 0 20px ${dramaColor}18` : 'none',
          }}
        >
          <div className="mb-2 flex items-center justify-between arcade-font text-[8px] tracking-widest text-[#6f8b77]">
            <span>PLACAR AO VIVO</span>
            <span style={{ color: dramaColor ?? undefined }}>{superficie ? superficie.toUpperCase() : 'PARTIDA'}</span>
          </div>
          <div className="mb-2 grid grid-cols-[1fr_auto_auto_auto] gap-2 border-b border-white/5 pb-2 arcade-font text-[7px] text-[#4b5d52]">
            <span />
            <span>SETS</span>
            <span>GAMES</span>
            <span>PTS</span>
          </div>
          <div className="grid grid-cols-[1fr_auto_auto_auto] items-center gap-2 arcade-font text-[12px]">
            <span className="truncate text-neon-green">{nomeJogador}</span>
            <span className="text-neon-green">{placar.sets[0]}</span>
            <span className="text-neon-green">{placar.games[0]}</span>
            <span className="text-neon-green">{placar.pontos[0]}</span>
            <span className="truncate text-[#ff8d6d]">{adversario.nome}</span>
            <span className="text-[#ff8d6d]">{placar.sets[1]}</span>
            <span className="text-[#ff8d6d]">{placar.games[1]}</span>
            <span className="text-[#ff8d6d]">{placar.pontos[1]}</span>
          </div>
        </div>

        <div className="match-card match-card-soft border border-[#2a3440] p-3">
          <div className="flex items-center justify-between mb-2 arcade-font text-[8px] tracking-widest text-[#8292a1]">
            <span>MOMENTUM / EMOCIONAL</span>
            <span style={{ color: corMomentum(momentum) }}>{destaqueMomento}</span>
          </div>
          <InlineMeter value={momentum} color={corMomentum(momentum)} />
          
          {/* Insights Táticos */}
          {pointInsights.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {pointInsights.map((insight, idx) => (
                <div 
                  key={idx} 
                  className="px-1.5 py-0.5 border border-neon-cyan/40 bg-neon-cyan/5 arcade-font text-[6px] text-neon-cyan tracking-tight animate-in fade-in zoom-in duration-300"
                >
                  ⚡ {insight.toUpperCase()}
                </div>
              ))}
            </div>
          )}

          <div className="mt-2 arcade-font text-[10px] leading-relaxed" style={{ color: destaqueMomentoCor }}>
            {destaqueMomento}
          </div>
          {pulsoNarrativo && (
            <div className="mt-3 border px-2.5 py-2" style={{ borderColor: `${pulsoNarrativo.color}55`, background: `${pulsoNarrativo.color}12` }}>
              <div className="arcade-font text-[8px] tracking-widest uppercase" style={{ color: pulsoNarrativo.color }}>
                {pulsoNarrativo.headline}
              </div>
              <div className="mt-1 arcade-font text-[9px] text-white/80 leading-relaxed">
                {pulsoNarrativo.subline}
              </div>
              <div className="mt-2 arcade-font text-[8px] leading-relaxed text-white/72">
                {pulsoNarrativo.recommendation}
              </div>
            </div>
          )}
          <div className="mt-2 arcade-font text-[9px] text-[#b8c6d1]">{resumoModo(modo)}</div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="match-card match-card-player border border-neon-green/20 p-3">
            <div className="arcade-font text-[8px] tracking-widest text-[#77d39e] mb-2">VOCÊ</div>
            <div className="space-y-2 arcade-font text-[10px] text-white">
              <div>
                <div className="mb-1 flex items-center justify-between text-[#9fe5bb]">
                  <span>Energia</span>
                  <span>{Math.round(energiaJogadorAoVivo)}%</span>
                </div>
                <InlineMeter value={Math.round(energiaJogadorAoVivo)} color="var(--neon-green)" />
              </div>
              <div>
                <div className="mb-1 flex items-center justify-between text-[#ffe07a]">
                  <span>Fadiga</span>
                  <span>{Math.round(fadigaJogadorAoVivo)}%</span>
                </div>
                <InlineMeter value={Math.round(fadigaJogadorAoVivo)} color="var(--neon-yellow)" />
              </div>
              <div className="text-[#8fbea1] leading-relaxed">{leituraJogador}</div>
              <div className="border-t border-[#1d3525] pt-2 space-y-1">
                {resumoEstrategiaJogador.map((linha) => (
                  <div key={linha} className="text-[#8fbea1] leading-relaxed">{linha}</div>
                ))}
              </div>
            </div>
          </div>

          <div className="match-card match-card-rival border border-[#ff4466]/20 p-3">
            <div className="arcade-font text-[8px] tracking-widest text-[#ff8ca3] mb-2">RIVAL</div>
            <div className="space-y-2 arcade-font text-[10px] text-white">
              <div>
                <div className="mb-1 flex items-center justify-between text-[#ffb7c6]">
                  <span>Energia</span>
                  <span>{Math.round(energiaAdversarioAoVivo)}%</span>
                </div>
                <InlineMeter value={Math.round(energiaAdversarioAoVivo)} color="#ff4466" />
              </div>
              <div>
                <div className="mb-1 flex items-center justify-between text-[#ffe07a]">
                  <span>Fadiga</span>
                  <span>{Math.round(fadigaAdversarioAoVivo)}%</span>
                </div>
                <InlineMeter value={Math.round(fadigaAdversarioAoVivo)} color="var(--neon-yellow)" />
              </div>
              <div className="text-[#d7a7b2] leading-relaxed">{leituraRival}</div>
              <div className="border-t border-[#35202a] pt-2 space-y-1">
                {resumoEstrategiaAdversario.map((linha) => (
                  <div key={linha} className="text-[#d7a7b2] leading-relaxed">{linha}</div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {(placar.stats_j || placar.stats_a) && (
          <BroadcastStatsCard
            nomeJogador={nomeJogador}
            nomeAdversario={adversario.nome}
            rankingJogador={undefined}
            rankingAdversario={adversario.ranking}
            statsJ={placar.stats_j ?? {
              aces: 0, duplas_faltas: 0, primeiro_saque_pct: '0%',
              winners: 0, erros_nao_forcados: 0, pontos_saque_pct: '0%',
              pontos_devolucao_pct: '0%', break_points: '0/0',
              rallies_curtos: 0, rallies_medios: 0, rallies_longos: 0,
            }}
            statsA={placar.stats_a ?? {
              aces: 0, duplas_faltas: 0, primeiro_saque_pct: '0%',
              winners: 0, erros_nao_forcados: 0, pontos_saque_pct: '0%',
              pontos_devolucao_pct: '0%', break_points: '0/0',
              rallies_curtos: 0, rallies_medios: 0, rallies_longos: 0,
            }}
            setAtual={placar.sets[0] + placar.sets[1] + 1}
          />
        )}

        <div className="border border-white/10 bg-[#0a0a0a] p-3 space-y-3">
          <div>
            <div className="arcade-font text-[8px] tracking-widest text-[#7f8b96] mb-1">PLANO ATUAL</div>
            <div className="arcade-font text-[12px]" style={{ color: planoAtual.color }}>
              {planoAtual.label}
            </div>
            <div className="arcade-font text-[9px] text-[#b9c4cd] mt-1">{planoAtual.desc}</div>
            <div className="arcade-font text-[9px] text-[#8da6b7] mt-2">
              2º saque: {segundoSaque === 'FORCAR' ? 'forçar' : 'seguro'}
            </div>
          </div>
        </div>

        <MatchControls
          fase={fase}
          modo={modo}
          partidaId={partidaId}
          simulando={simulando}
          simulacaoPausada={simulacaoPausada}
          alternarPausaSimulacao={alternarPausaSimulacao}
          velocidadeRapidaAtual={velocidadeRapidaAtual}
          velocidadeRapida={velocidadeRapida}
          setVelocidadeRapida={setVelocidadeRapida}
          ajustandoPlanoRapido={ajustandoPlanoRapido}
          setAjustandoPlanoRapido={setAjustandoPlanoRapido}
          mentalidade={mentalidade}
          abordagem={abordagem}
          instrucao={instrucao}
          segundoSaque={segundoSaque}
          setMentalidade={setMentalidade}
          setAbordagem={setAbordagem}
          setInstrucao={setInstrucao}
          setSegundoSaque={setSegundoSaque}
          handleAplicarPausaRapida={handleAplicarPausaRapida}
          placar={placar}
          gameResult={gameResult}
          momentum={momentum}
          planoAtual={planoAtual}
          ajustandoPlanoGame={ajustandoPlanoGame}
          setAjustandoPlanoGame={setAjustandoPlanoGame}
          handleContinuarGame={handleContinuarGame}
          energiaJogadorAoVivo={energiaJogadorAoVivo}
          fadigaJogadorAoVivo={fadigaJogadorAoVivo}
          energiaAdversarioAoVivo={energiaAdversarioAoVivo}
          fadigaAdversarioAoVivo={fadigaAdversarioAoVivo}
          ajustandoPlanoSet={ajustandoPlanoSet}
          setAjustandoPlanoSet={setAjustandoPlanoSet}
          contadorSet={contadorSet}
          handleContinuarSet={handleContinuarSet}
          handleEscolherPlanoSet={handleEscolherPlanoSet}
          intencaoAtiva={intencaoAtiva}
          handleIntencao={handleIntencao}
          expandirPonto={expandirPonto}
          setExpandirPonto={setExpandirPonto}
          faixa={faixa}
          setFaixa={setFaixa}
          alvo={alvo}
          setAlvo={setAlvo}
          trocarModoAcompanhamento={trocarModoAcompanhamento}
        />
      </div>

      <div className="p-3 app-panel border-t border-[#1a1a2e] shrink-0 space-y-2">
        {fase === 'encerrada' ? (
          <div className="border border-[#1f3340] bg-[#09111a] px-4 py-3 text-center">
            <div className="arcade-font text-[8px] text-[#5b7182] tracking-widest">FECHANDO A PARTIDA</div>
          </div>
        ) : (
          <button
            onClick={onSurrender}
            className="w-full py-2 border border-[#3a1020] text-[8px] arcade-font text-[#3a1020] hover:text-neon-pink hover:border-neon-pink transition-colors"
          >
            DESISTIR DA PARTIDA (W.O.)
          </button>
        )}
      </div>
    </div>
  )
}
