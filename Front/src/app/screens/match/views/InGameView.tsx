import { ArrowLeft } from 'lucide-react'
import { InlineMeter } from '../components'
import { corMomentum, resumoModo } from '../model'
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
  nomeJogador: string
  adversario: AdversarioInfo
  placar: PlacarState
  superficie: string
  momentum: number
  destaqueMomento: string
  destaqueMomentoCor: string
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
  faixa: Faixa
  alvo: Alvo
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
  nomeJogador,
  adversario,
  placar,
  superficie,
  momentum,
  destaqueMomento,
  destaqueMomentoCor,
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
  faixa,
  alvo,
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
  return (
    <div className="app-shell min-h-screen flex flex-col bg-[#050505]">
      <div className="app-panel sticky top-0 z-20 p-3 border-b-2 border-[#00ff88] flex items-center gap-3 shrink-0 bg-black/80 backdrop-blur-md">
        <button onClick={onBack} className="text-[#00ff88] hover:scale-110 transition-transform">
          <ArrowLeft size={18} />
        </button>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <span className="arcade-font text-[9px] text-white truncate max-w-[100px]">{nomeJogador}</span>
            <div className="flex gap-2 arcade-font text-[10px]">
              <span className={placar.sets[0] > placar.sets[1] ? 'text-[#00ff88]' : 'text-[#444]'}>{placar.sets[0]}</span>
              <span className="text-[#222]">|</span>
              <span className={placar.sets[1] > placar.sets[0] ? 'text-[#ff4466]' : 'text-[#444]'}>{placar.sets[1]}</span>
            </div>
            <span className="arcade-font text-[9px] text-white truncate max-w-[100px] text-right">{adversario.nome}</span>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3 pb-4">
        <div className="border border-[#00ff88]/30 bg-[#08110b] p-3">
          <div className="mb-2 flex items-center justify-between arcade-font text-[8px] tracking-widest text-[#6f8b77]">
            <span>PLACAR AO VIVO</span>
            <span>{superficie ? superficie.toUpperCase() : 'PARTIDA'}</span>
          </div>
          <div className="mb-2 grid grid-cols-[1fr_auto_auto_auto] gap-2 border-b border-white/5 pb-2 arcade-font text-[7px] text-[#4b5d52]">
            <span />
            <span>SETS</span>
            <span>GAMES</span>
            <span>PTS</span>
          </div>
          <div className="grid grid-cols-[1fr_auto_auto_auto] items-center gap-2 arcade-font text-[12px]">
            <span className="truncate text-[#00ff88]">{nomeJogador}</span>
            <span className="text-[#00ff88]">{placar.sets[0]}</span>
            <span className="text-[#00ff88]">{placar.games[0]}</span>
            <span className="text-[#00ff88]">{placar.pontos[0]}</span>
            <span className="truncate text-[#ff8d6d]">{adversario.nome}</span>
            <span className="text-[#ff8d6d]">{placar.sets[1]}</span>
            <span className="text-[#ff8d6d]">{placar.games[1]}</span>
            <span className="text-[#ff8d6d]">{placar.pontos[1]}</span>
          </div>
        </div>

        <div className="border border-[#2a3440] bg-[#071019] p-3">
          <div className="flex items-center justify-between mb-2 arcade-font text-[8px] tracking-widest text-[#8292a1]">
            <span>MOMENTUM / EMOCIONAL</span>
            <span style={{ color: corMomentum(momentum) }}>{destaqueMomento}</span>
          </div>
          <InlineMeter value={momentum} color={corMomentum(momentum)} />
          <div className="mt-2 arcade-font text-[10px] leading-relaxed" style={{ color: destaqueMomentoCor }}>
            {destaqueMomento}
          </div>
          <div className="mt-2 arcade-font text-[9px] text-[#b8c6d1]">{resumoModo(modo)}</div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="border border-[#00ff88]/20 bg-[#07110a] p-3">
            <div className="arcade-font text-[8px] tracking-widest text-[#77d39e] mb-2">VOCÊ</div>
            <div className="space-y-2 arcade-font text-[10px] text-white">
              <div>
                <div className="mb-1 flex items-center justify-between text-[#9fe5bb]">
                  <span>Energia</span>
                  <span>{Math.round(energiaJogadorAoVivo)}%</span>
                </div>
                <InlineMeter value={Math.round(energiaJogadorAoVivo)} color="#00ff88" />
              </div>
              <div>
                <div className="mb-1 flex items-center justify-between text-[#ffe07a]">
                  <span>Fadiga</span>
                  <span>{Math.round(fadigaJogadorAoVivo)}%</span>
                </div>
                <InlineMeter value={Math.round(fadigaJogadorAoVivo)} color="#ffe600" />
              </div>
              <div className="text-[#8fbea1] leading-relaxed">{leituraJogador}</div>
              <div className="border-t border-[#1d3525] pt-2 space-y-1">
                {resumoEstrategiaJogador.map((linha) => (
                  <div key={linha} className="text-[#8fbea1] leading-relaxed">{linha}</div>
                ))}
              </div>
            </div>
          </div>

          <div className="border border-[#ff4466]/20 bg-[#14090d] p-3">
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
                <InlineMeter value={Math.round(fadigaAdversarioAoVivo)} color="#ffe600" />
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
          <div className="overflow-hidden border border-[#36505d] bg-[#0b160f]">
            <div className="flex items-center justify-between bg-[#4b2c63] px-3 py-2">
              <div className="arcade-font text-[10px] tracking-widest text-white">MATCH SUMMARY</div>
              <div className="arcade-font text-[8px] text-[#d6c3e7]">AO VIVO</div>
            </div>
            <div className="grid grid-cols-[1fr_auto_1fr] items-center bg-[#24462c] px-3 py-2 arcade-font text-[9px]">
              <div className="truncate text-left text-[#d8f5df]">{nomeJogador.toUpperCase()}</div>
              <div className="text-center text-[#aac7ac]">STAT</div>
              <div className="truncate text-right text-[#ffe0d6]">{adversario.nome.toUpperCase()}</div>
            </div>
            <div className="divide-y divide-[#28402f]">
              {[
                { label: 'Aces', j: placar.stats_j?.aces ?? 0, a: placar.stats_a?.aces ?? 0 },
                { label: 'Double Faults', j: placar.stats_j?.duplas_faltas ?? 0, a: placar.stats_a?.duplas_faltas ?? 0 },
                { label: '1st Serves In', j: placar.stats_j?.primeiro_saque_pct ?? '0%', a: placar.stats_a?.primeiro_saque_pct ?? '0%' },
                { label: 'Winners', j: placar.stats_j?.winners ?? 0, a: placar.stats_a?.winners ?? 0 },
                { label: 'Unforced Errors', j: placar.stats_j?.erros_nao_forcados ?? 0, a: placar.stats_a?.erros_nao_forcados ?? 0 },
                { label: 'Break Points', j: placar.stats_j?.break_points ?? '0/0', a: placar.stats_a?.break_points ?? '0/0' },
              ].map((item, index) => (
                <div
                  key={item.label}
                  className="grid grid-cols-[1fr_auto_1fr] items-center gap-3 px-3 py-2 arcade-font text-[10px]"
                  style={{ background: index % 2 === 0 ? '#17331f' : '#12281a' }}
                >
                  <div className="text-left text-[#f0fff4]">{item.j}</div>
                  <div className="text-center text-[#c9dfc9]">{item.label}</div>
                  <div className="text-right text-[#ffe9dc]">{item.a}</div>
                </div>
              ))}
            </div>
          </div>
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
            className="w-full py-2 border border-[#3a1020] text-[8px] arcade-font text-[#3a1020] hover:text-[#ff0055] hover:border-[#ff0055] transition-colors"
          >
            DESISTIR DA PARTIDA (W.O.)
          </button>
        )}
      </div>
    </div>
  )
}
