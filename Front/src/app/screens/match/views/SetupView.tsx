import { useNavigate } from 'react-router'
import { TacticalPackageEditor } from '../components'
import { OpponentScoutingCard } from '../scouting/OpponentScoutingCard'
import { ScoutingReportCard } from '../scouting/ScoutingReportCard'
import { ExperienceModePanel, MatchBriefingPanel, MatchupCards, SetupHeader, StickyStartBar } from './SetupViewSections'
import { MatchAnalysisCard } from './MatchAnalysisCard'
import { gerarBriefingNarrativo, gerarContextoPartida } from '../matchNarrative'
import type {
  PartidaScout,
} from '../../../../types'
import type {
  AdversarioInfo,
  JogadorState,
  ModoAcomp,
  MentalidadeValor,
  AbordagemValor,
  InstrucaoValor,
  SegundoSaqueModo,
} from '../types'

interface SetupViewProps {
  themeClass: string
  faseTorneio: string
  nomeTorneio?: string
  superficie: string
  surface: string
  jogador: JogadorState | null
  adversario: AdversarioInfo
  overallCardJogador: number
  rankingJogador: number | null
  overallCardAdversario: number
  rankingAdversario: number | null
  corCardRival: string
  leituraRival: string
  abaRival: 'registros' | 'historia'
  setAbaRival: (aba: 'registros' | 'historia') => void
  historicoRival: string[]
  titulosRival: string[]
  energiaAdversarioAoVivo: number
  fadigaAdversarioAoVivo: number
  scoutRival: PartidaScout | null
  nomeJogador: string
  leituraJogador: string
  abaJogador: 'registros' | 'historia'
  setAbaJogador: (aba: 'registros' | 'historia') => void
  historicoJogador: string[]
  titulosJogador: string[]
  energiaJogadorAoVivo: number
  fadigaJogadorAoVivo: number
  metricsJogador: any
  reportJogador: any
  planoExecutivo: string
  mentalidade: MentalidadeValor
  abordagem: AbordagemValor
  instrucao: InstrucaoValor
  segundoSaque: SegundoSaqueModo
  setMentalidade: (v: MentalidadeValor) => void
  setAbordagem: (v: AbordagemValor) => void
  setInstrucao: (v: InstrucaoValor) => void
  setSegundoSaque: (v: SegundoSaqueModo) => void
  encaixeFisico: string
  riscoTatico: string
  modo: ModoAcomp
  trocarModoAcompanhamento: (m: ModoAcomp) => void
  erroEntrada: string
  handleIniciar: () => void
  simulando: boolean
  confirmandoEntrada: boolean
  inferirEstilo: (attrs: any) => string
}

export function SetupView({
  themeClass,
  faseTorneio,
  nomeTorneio,
  superficie,
  surface,
  jogador,
  adversario,
  overallCardJogador,
  rankingJogador,
  overallCardAdversario,
  rankingAdversario,
  corCardRival,
  leituraRival,
  abaRival,
  setAbaRival,
  historicoRival,
  titulosRival,
  energiaAdversarioAoVivo,
  fadigaAdversarioAoVivo,
  scoutRival,
  nomeJogador,
  leituraJogador,
  abaJogador,
  setAbaJogador,
  historicoJogador,
  titulosJogador,
  energiaJogadorAoVivo,
  fadigaJogadorAoVivo,
  metricsJogador,
  reportJogador,
  planoExecutivo,
  mentalidade,
  abordagem,
  instrucao,
  segundoSaque,
  setMentalidade,
  setAbordagem,
  setInstrucao,
  setSegundoSaque,
  encaixeFisico,
  riscoTatico,
  modo,
  trocarModoAcompanhamento,
  erroEntrada,
  handleIniciar,
  simulando,
  confirmandoEntrada,
  inferirEstilo,
}: SetupViewProps) {
  const navigate = useNavigate()

  const vitorias = scoutRival?.h2h?.vitorias_jogador ?? 0
  const derrotas = scoutRival?.h2h?.vitorias_adversario ?? 0
  const contexto = gerarContextoPartida(
    adversario.nome,
    rankingAdversario ?? 999,
    faseTorneio,
    nomeTorneio ?? '',
    { vitorias, derrotas, confrontos: vitorias + derrotas },
  )
  const briefing = gerarBriefingNarrativo({
    nomeJogador,
    nomeAdversario: adversario.nome,
    superficie,
    planoExecutivo,
    reportJogador,
    scoutRival,
  })

  return (
    <div className={`app-shell match-theme-screen ${themeClass} min-h-screen flex flex-col`}>
      <SetupHeader faseTorneio={faseTorneio} superficie={superficie} surface={surface} onBack={() => navigate('/tournament')} />

      <div className="flex-1 overflow-y-auto p-4 space-y-6 pb-32">
        <MatchBriefingPanel contexto={contexto} briefing={briefing} nomeTorneio={nomeTorneio} />

        <MatchupCards
          jogador={jogador}
          adversario={adversario}
          overallCardJogador={overallCardJogador}
          rankingJogador={rankingJogador}
          overallCardAdversario={overallCardAdversario}
          rankingAdversario={rankingAdversario}
        />

        {/* Match Analysis (FM Style) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <MatchAnalysisCard
            title="ANÁLISE DO RIVAL"
            accentColor={corCardRival}
            nome={adversario.nome}
            nacionalidade={adversario.nacionalidade}
            ranking={rankingAdversario}
            overall={overallCardAdversario}
            leitura={leituraRival}
            aba={abaRival}
            setAba={setAbaRival}
            historico={historicoRival}
            titulos={titulosRival}
            historicoTextColor="#ffd7e2"
            energia={energiaAdversarioAoVivo}
            fadiga={fadigaAdversarioAoVivo}
            dossieRoute={`/player/${(jogador?.tour ?? 'atp').toLowerCase()}/${encodeURIComponent(adversario.nome)}`}
          >
            <OpponentScoutingCard adv={adversario} scout={scoutRival} accent={corCardRival} superficie={superficie} />
          </MatchAnalysisCard>

          <MatchAnalysisCard
            title="SUA CONDIÇÃO"
            accentColor="var(--neon-green)"
            nome={nomeJogador}
            nacionalidade={jogador?.nacionalidade}
            ranking={rankingJogador}
            overall={overallCardJogador}
            infoExtra={`#${rankingJogador || '---'} · OVR ${overallCardJogador} · ${inferirEstilo(jogador?.atributos)}`}
            leitura={leituraJogador}
            aba={abaJogador}
            setAba={setAbaJogador}
            historico={historicoJogador}
            titulos={titulosJogador}
            historicoTextColor="#d7fff0"
            energia={energiaJogadorAoVivo}
            fadiga={fadigaJogadorAoVivo}
          >
            <ScoutingReportCard
              titulo="Scouting Report"
              overall={overallCardJogador}
              metrics={{ saque: metricsJogador.saque, fundo: metricsJogador.fundo, mental: metricsJogador.mental }}
              report={reportJogador}
              accent="var(--neon-green)"
            />
          </MatchAnalysisCard>
        </div>

        {/* FM TACTICAL PANEL */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <div className="w-1 h-4 bg-neon-yellow" />
            <span className="arcade-font text-[12px] text-neon-yellow tracking-widest uppercase">Instruções Táticas</span>
          </div>

          <div className="grid grid-cols-1 gap-4">
            <div className="grid grid-cols-1 md:grid-cols-[1.5fr_0.8fr_0.8fr] gap-4">
              <div className="app-panel border border-neon-yellow/20 p-4 bg-[#ffe60008]">
                <div className="arcade-font text-[11px] text-neon-yellow mb-2 tracking-widest uppercase">Resumo do Plano</div>
                <div className="arcade-font text-[13px] text-white leading-relaxed">
                  {planoExecutivo}
                </div>
                <div className="arcade-font text-[11px] text-[#c8d5df] mt-3 leading-relaxed">
                  {mentalidade === 'OFENSIVA'
                    ? 'A equipe técnica espera um jogo de imposição e tomada rápida da iniciativa.'
                    : mentalidade === 'DEFENSIVA'
                      ? 'A ideia central é absorver pressão, alongar rallies e baixar o risco.'
                      : 'O plano busca estabilidade, leitura do rival e ajustes durante a partida.'}
                </div>
              </div>

              <div className="app-panel border border-neon-green/20 p-4 bg-[#00ff8808]">
                <div className="arcade-font text-[11px] text-neon-green mb-2 tracking-widest uppercase">Encaixe Físico</div>
                <div
                  className="pixel-font text-xl"
                  style={{ color: encaixeFisico === 'ALTO' ? 'var(--neon-green)' : encaixeFisico === 'MÉDIO' ? 'var(--neon-yellow)' : '#ff4466' }}
                >
                  {encaixeFisico}
                </div>
                <div className="arcade-font text-[11px] text-[#c7ddd0] mt-2 leading-relaxed">
                  {encaixeFisico === 'ALTO'
                    ? 'Seu estado atual sustenta esse plano com conforto.'
                    : encaixeFisico === 'MÉDIO'
                      ? 'Dá para executar, mas precisa dosar intensidade.'
                      : 'Seu físico pede um plano mais conservador.'}
                </div>
              </div>

              <div className="app-panel border border-[#ff4466]/20 p-4 bg-[#ff446608]">
                <div className="arcade-font text-[11px] text-[#ff4466] mb-2 tracking-widest uppercase">Risco Tático</div>
                <div
                  className="pixel-font text-xl"
                  style={{ color: riscoTatico === 'BAIXO' ? 'var(--neon-green)' : riscoTatico === 'MÉDIO' ? 'var(--neon-yellow)' : '#ff4466' }}
                >
                  {riscoTatico}
                </div>
                <div className="arcade-font text-[11px] text-[#dfc6cc] mt-2 leading-relaxed">
                  {riscoTatico === 'ALTO'
                    ? 'Plano agressivo. Erros cedo podem virar pressão contra você.'
                    : riscoTatico === 'MÉDIO'
                      ? 'Existe bom potencial, mas com trade-off claro.'
                      : 'Estrutura segura para entrar no jogo e ajustar depois.'}
                </div>
              </div>
            </div>

            <div className="app-panel border border-white/10 p-4 bg-white/5">
              <div className="arcade-font text-[11px] text-[#b7c4d1] mb-3 tracking-widest uppercase">Pacote Tático</div>
              <TacticalPackageEditor
                mentalidade={mentalidade}
                abordagem={abordagem}
                instrucao={instrucao}
                segundoSaque={segundoSaque}
                setMentalidade={setMentalidade}
                setAbordagem={setAbordagem}
                setInstrucao={setInstrucao}
                setSegundoSaque={setSegundoSaque}
              />
            </div>
          </div>
        </div>
        <ExperienceModePanel modo={modo} trocarModoAcompanhamento={trocarModoAcompanhamento} />

      </div>

      <StickyStartBar
        erroEntrada={erroEntrada}
        handleIniciar={handleIniciar}
        simulando={simulando}
        confirmandoEntrada={confirmandoEntrada}
      />
    </div>
  )
}
