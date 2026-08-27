import { useNavigate } from 'react-router'
import { useMatchController } from './match/useMatchController'
import { SetupView } from './match/views/SetupView'
import { PostMatchView } from './match/views/PostMatchView'
import { InGameView } from './match/views/InGameView'
import { LoadingScreen } from '../components/LoadingScreen'
import { getMatchThemeClass } from './match/uiUtils'

export function MatchScreen() {
  const navigate = useNavigate()
  const ctrl = useMatchController()
  const themeClass = getMatchThemeClass(ctrl.surface)
  const isFinal = ctrl.faseTorneio?.toLowerCase() === 'final'

  if (ctrl.fase === 'hype') return <LoadingScreen />

  if (ctrl.fase === 'setup') {
    return (
      <div className={isFinal ? 'final-glow-overlay' : ''}>
        <SetupView
          themeClass={themeClass}
          faseTorneio={ctrl.faseTorneio}
          nomeTorneio={ctrl.torneio?.nome}
          superficie={ctrl.superficie}
          surface={ctrl.surface}
          jogador={ctrl.jogador}
          adversario={ctrl.adversario}
          overallCardJogador={ctrl.overallCardJogador}
          rankingJogador={ctrl.rankingJogador}
          overallCardAdversario={ctrl.overallCardAdversario}
          rankingAdversario={ctrl.rankingAdversario}
          corCardRival={ctrl.corCardRival}
          leituraRival={ctrl.leituraRival}
          abaRival={ctrl.abaRival}
          setAbaRival={ctrl.setAbaRival}
          historicoRival={ctrl.historicoRival}
          titulosRival={ctrl.titulosRival}
          energiaAdversarioAoVivo={ctrl.energiaAdversarioAoVivo}
          fadigaAdversarioAoVivo={ctrl.fadigaAdversarioAoVivo}
          scoutRival={ctrl.scoutRival}
          nomeJogador={ctrl.nomeJogador}
          leituraJogador={ctrl.leituraJogador}
          abaJogador={ctrl.abaJogador}
          setAbaJogador={ctrl.setAbaJogador}
          historicoJogador={ctrl.historicoJogador}
          titulosJogador={ctrl.titulosJogador}
          energiaJogadorAoVivo={ctrl.energiaJogadorAoVivo}
          fadigaJogadorAoVivo={ctrl.fadigaJogadorAoVivo}
          metricsJogador={ctrl.metricsJogador}
          reportJogador={ctrl.reportJogador}
          planoExecutivo={ctrl.planoExecutivo}
          mentalidade={ctrl.mentalidade}
          abordagem={ctrl.abordagem}
          instrucao={ctrl.instrucao}
          segundoSaque={ctrl.segundoSaque}
          setMentalidade={ctrl.setMentalidade}
          setAbordagem={ctrl.setAbordagem}
          setInstrucao={ctrl.setInstrucao}
          setSegundoSaque={ctrl.setSegundoSaque}
          encaixeFisico={ctrl.encaixeFisico}
          riscoTatico={ctrl.riscoTatico}
          modo={ctrl.modo}
          trocarModoAcompanhamento={ctrl.trocarModoAcompanhamento}
          erroEntrada={ctrl.erroEntrada}
          handleIniciar={ctrl.handleIniciar}
          simulando={ctrl.simulando}
          confirmandoEntrada={ctrl.confirmandoEntrada}
          inferirEstilo={ctrl.inferirEstilo}
        />
      </div>
    )
  }

  if (ctrl.fase === 'pos-stats' || ctrl.fase === 'pos-consequencias') {
    return (
      <div className={isFinal ? 'final-glow-overlay' : ''}>
        <PostMatchView
          themeClass={themeClass}
          fase={ctrl.fase}
          placar={ctrl.placar}
          nomeJogador={ctrl.nomeJogador}
          adversario={ctrl.adversario}
          log={ctrl.log}
          jogadorPosjogo={ctrl.jogadorPosjogo}
          jogador={ctrl.jogador}
          jogadorAntesRef={ctrl.jogadorAntesRef}
          setFase={ctrl.setFase}
          handleContinuarPosJogo={ctrl.handleContinuarPosJogo}
          faseTorneio={ctrl.faseTorneio}
          nomeTorneio={ctrl.torneio?.nome}
          tipoTorneio={ctrl.torneio?.tipo}
          comentarioParceiro={ctrl.comentarioParceiro}
        />
      </div>
    )
  }

  return (
    <div className={isFinal ? 'final-glow-overlay' : ''}>
      <InGameView
        themeClass={themeClass}
        tipoTorneio={ctrl.torneio?.tipo}
        pontoCritico={ctrl.pontoCritico}
        isTiebreak={ctrl.isTiebreak}
        isComeback={ctrl.isComeback}
        crowdRoar={ctrl.crowdRoar}
        quimicaJogador={ctrl.quimicaJogador}
        quimicaAdversario={ctrl.quimicaAdversario}
        nomeJogador={ctrl.nomeJogador}
        adversario={ctrl.adversario}
        placar={ctrl.placar}
        superficie={ctrl.superficie}
      momentum={ctrl.momentum}
      destaqueMomento={ctrl.destaqueMomento}
      destaqueMomentoCor={ctrl.destaqueMomentoCor}
      pulsoNarrativo={ctrl.pulsoNarrativo}
      leituraJogador={ctrl.leituraJogador}
        leituraRival={ctrl.leituraRival}
        energiaJogadorAoVivo={ctrl.energiaJogadorAoVivo}
        fadigaJogadorAoVivo={ctrl.fadigaJogadorAoVivo}
        energiaAdversarioAoVivo={ctrl.energiaAdversarioAoVivo}
        fadigaAdversarioAoVivo={ctrl.fadigaAdversarioAoVivo}
        resumoEstrategiaJogador={ctrl.resumoEstrategiaJogador}
        resumoEstrategiaAdversario={ctrl.resumoEstrategiaAdversario}
        planoAtual={ctrl.planoAtual}
        segundoSaque={ctrl.segundoSaque}
        fase={ctrl.fase}
        modo={ctrl.modo}
        partidaId={ctrl.partidaId}
        simulando={ctrl.simulando}
        simulacaoPausada={ctrl.simulacaoPausada}
        velocidadeRapidaAtual={ctrl.velocidadeRapidaAtual}
        velocidadeRapida={ctrl.velocidadeRapida}
        ajustandoPlanoRapido={ctrl.ajustandoPlanoRapido}
        mentalidade={ctrl.mentalidade}
        abordagem={ctrl.abordagem}
        instrucao={ctrl.instrucao}
        gameResult={ctrl.gameResult}
        ajustandoPlanoGame={ctrl.ajustandoPlanoGame}
        ajustandoPlanoSet={ctrl.ajustandoPlanoSet}
        contadorSet={ctrl.contadorSet}
        intencaoAtiva={ctrl.intencaoAtiva}
        expandirPonto={ctrl.expandirPonto}
        pointInsights={ctrl.pointInsights}
        faixa={ctrl.faixa}
        alvo={ctrl.alvo}
        onBack={() => navigate('/tournament')}
        onSurrender={ctrl.handleDesistir}
        alternarPausaSimulacao={ctrl.alternarPausaSimulacao}
        setVelocidadeRapida={ctrl.setVelocidadeRapida}
        setAjustandoPlanoRapido={ctrl.setAjustandoPlanoRapido}
        setMentalidade={ctrl.setMentalidade}
        setAbordagem={ctrl.setAbordagem}
        setInstrucao={ctrl.setInstrucao}
        setSegundoSaque={ctrl.setSegundoSaque}
        handleAplicarPausaRapida={ctrl.handleAplicarPausaRapida}
        setAjustandoPlanoGame={ctrl.setAjustandoPlanoGame}
        handleContinuarGame={ctrl.handleContinuarGame}
        setAjustandoPlanoSet={ctrl.setAjustandoPlanoSet}
        handleContinuarSet={ctrl.handleContinuarSet}
        handleEscolherPlanoSet={ctrl.handleEscolherPlanoSet}
        handleIntencao={ctrl.handleIntencao}
        setExpandirPonto={ctrl.setExpandirPonto}
        setFaixa={ctrl.setFaixa}
        setAlvo={ctrl.setAlvo}
        trocarModoAcompanhamento={ctrl.trocarModoAcompanhamento}
      />
    </div>
  )
}
