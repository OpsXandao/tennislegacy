import type {
  Alvo,
  Faixa,
  Fase,
  GameResult,
  ModoAcomp,
  AbordagemValor,
  InstrucaoValor,
  MentalidadeValor,
  PlanoValor,
  SegundoSaqueModo,
  VelocidadeRapida,
} from '../types'
import type { PlacarState } from '../../../../types'
import {
  BetweenGamesPanel,
  BetweenSetsModal,
  FinishedResultCard,
  PassiveModeStatus,
  RapidSimulationPanel,
  SimulatingIndicator,
  StrategistActionPanel,
} from './MatchControlPanels'

export interface TacticalPackageControls {
  mentalidade: MentalidadeValor
  abordagem: AbordagemValor
  instrucao: InstrucaoValor
  segundoSaque: SegundoSaqueModo
  setMentalidade: (v: MentalidadeValor) => void
  setAbordagem: (v: AbordagemValor) => void
  setInstrucao: (v: InstrucaoValor) => void
  setSegundoSaque: (v: SegundoSaqueModo) => void
}

interface MatchControlsProps extends TacticalPackageControls {
  fase: Fase
  modo: ModoAcomp
  partidaId: string | null
  simulando: boolean
  simulacaoPausada: boolean
  alternarPausaSimulacao: () => void
  velocidadeRapidaAtual: { label: string }
  velocidadeRapida: VelocidadeRapida
  setVelocidadeRapida: (v: VelocidadeRapida) => void
  ajustandoPlanoRapido: boolean
  setAjustandoPlanoRapido: (v: any) => void
  handleAplicarPausaRapida: () => void
  placar: PlacarState
  gameResult: GameResult | null
  momentum: number
  planoAtual: { color: string; label: string }
  ajustandoPlanoGame: boolean
  setAjustandoPlanoGame: (v: boolean) => void
  handleContinuarGame: () => void
  energiaJogadorAoVivo: number
  fadigaJogadorAoVivo: number
  energiaAdversarioAoVivo: number
  fadigaAdversarioAoVivo: number
  ajustandoPlanoSet: boolean
  setAjustandoPlanoSet: (v: boolean) => void
  contadorSet: number
  handleContinuarSet: () => void
  handleEscolherPlanoSet: (p: PlanoValor) => void
  intencaoAtiva: string | null
  handleIntencao: (i: string) => void
  expandirPonto: boolean
  setExpandirPonto: (v: any) => void
  faixa: Faixa
  setFaixa: (v: Faixa) => void
  alvo: Alvo
  setAlvo: (v: Alvo) => void
  trocarModoAcompanhamento: (m: ModoAcomp) => void
}

export function MatchControls({
  fase,
  modo,
  partidaId,
  simulando,
  simulacaoPausada,
  alternarPausaSimulacao,
  velocidadeRapidaAtual,
  velocidadeRapida,
  setVelocidadeRapida,
  ajustandoPlanoRapido,
  setAjustandoPlanoRapido,
  mentalidade,
  abordagem,
  instrucao,
  segundoSaque,
  setMentalidade,
  setAbordagem,
  setInstrucao,
  setSegundoSaque,
  handleAplicarPausaRapida,
  placar,
  gameResult,
  momentum,
  planoAtual,
  ajustandoPlanoGame,
  setAjustandoPlanoGame,
  handleContinuarGame,
  energiaJogadorAoVivo,
  fadigaJogadorAoVivo,
  energiaAdversarioAoVivo,
  fadigaAdversarioAoVivo,
  ajustandoPlanoSet,
  setAjustandoPlanoSet,
  contadorSet,
  handleContinuarSet,
  handleEscolherPlanoSet,
  intencaoAtiva,
  handleIntencao,
  expandirPonto,
  setExpandirPonto,
  faixa,
  setFaixa,
  alvo,
  setAlvo,
  trocarModoAcompanhamento,
}: MatchControlsProps) {
  const tacticalControls: TacticalPackageControls = {
    mentalidade,
    abordagem,
    instrucao,
    segundoSaque,
    setMentalidade,
    setAbordagem,
    setInstrucao,
    setSegundoSaque,
  }

  return (
    <>
      <RapidSimulationPanel
        fase={fase}
        modo={modo}
        partidaId={partidaId}
        simulacaoPausada={simulacaoPausada}
        alternarPausaSimulacao={alternarPausaSimulacao}
        velocidadeRapidaAtual={velocidadeRapidaAtual}
        velocidadeRapida={velocidadeRapida}
        setVelocidadeRapida={setVelocidadeRapida}
        ajustandoPlanoRapido={ajustandoPlanoRapido}
        setAjustandoPlanoRapido={setAjustandoPlanoRapido}
        handleAplicarPausaRapida={handleAplicarPausaRapida}
        {...tacticalControls}
      />

      <FinishedResultCard fase={fase} placar={placar} />

      <BetweenGamesPanel
        fase={fase}
        gameResult={gameResult}
        momentum={momentum}
        planoAtual={planoAtual}
        ajustandoPlanoGame={ajustandoPlanoGame}
        setAjustandoPlanoGame={setAjustandoPlanoGame}
        handleContinuarGame={handleContinuarGame}
        simulando={simulando}
        {...tacticalControls}
      />

      <BetweenSetsModal
        fase={fase}
        placar={placar}
        energiaJogadorAoVivo={energiaJogadorAoVivo}
        fadigaJogadorAoVivo={fadigaJogadorAoVivo}
        energiaAdversarioAoVivo={energiaAdversarioAoVivo}
        fadigaAdversarioAoVivo={fadigaAdversarioAoVivo}
        ajustandoPlanoSet={ajustandoPlanoSet}
        setAjustandoPlanoSet={setAjustandoPlanoSet}
        contadorSet={contadorSet}
        handleContinuarSet={handleContinuarSet}
        handleEscolherPlanoSet={handleEscolherPlanoSet}
        simulando={simulando}
        {...tacticalControls}
      />

      <SimulatingIndicator simulando={simulando} />

      <StrategistActionPanel
        fase={fase}
        modo={modo}
        simulando={simulando}
        intencaoAtiva={intencaoAtiva}
        handleIntencao={handleIntencao}
        expandirPonto={expandirPonto}
        setExpandirPonto={setExpandirPonto}
        faixa={faixa}
        setFaixa={setFaixa}
        alvo={alvo}
        setAlvo={setAlvo}
      />

      <PassiveModeStatus
        fase={fase}
        modo={modo}
        simulando={simulando}
        trocarModoAcompanhamento={trocarModoAcompanhamento}
      />
    </>
  )
}
