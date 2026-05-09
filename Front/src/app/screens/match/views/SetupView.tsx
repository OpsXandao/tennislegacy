import { useNavigate } from 'react-router'
import { ArrowLeft } from 'lucide-react'
import { NeonButton } from '../../../components/NeonButton'
import { FutCard } from '../../../components/FutCard'
import {
  CircularGauge,
  TacticalPackageEditor,
} from '../components'
import { OpponentScoutingCard } from '../scouting/OpponentScoutingCard'
import { ScoutingReportCard } from '../scouting/ScoutingReportCard'
import {
  COURT_COLORS,
  MODOS_VISIVEIS,
  MODOS_ACOMP,
  alpha,
  formatarNacionalidade,
} from '../model'
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
  faseTorneio: string
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
  faseTorneio,
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

  return (
    <div className="app-shell min-h-screen flex flex-col bg-[#0a0a0f]">
      {/* Header Vestiário */}
      <div className="app-panel p-4 border-b-2 border-neon-green flex items-center justify-between shrink-0 bg-black/40">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/tournament')} className="text-neon-green hover:scale-110 transition-transform">
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
              <div className="h-2 w-6 border border-white/20" style={{ background: COURT_COLORS[surface as keyof typeof COURT_COLORS] }} />
              <span className="arcade-font text-[10px] text-white">{superficie.toUpperCase()}</span>
            </div>
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6 pb-32">
        
        {/* Cartas FIFA (Pré-Match) */}
        <div className="flex flex-col lg:flex-row gap-6 items-center justify-center py-4 bg-gradient-to-b from-[#0a0a0f] to-transparent">
          <div className="flex flex-col items-center gap-2">
            <div className="arcade-font text-[10px] text-neon-green tracking-widest uppercase mb-2">SEU JOGADOR</div>
            <FutCard
              nome={jogador?.nome ?? 'VOCÊ'}
              nacionalidade={jogador?.nacionalidade ?? ''}
              overall={overallCardJogador}
              tour={(jogador?.tour ?? 'atp').toLowerCase() as 'atp' | 'wta'}
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
              tour={(jogador?.tour ?? 'atp').toLowerCase() as 'atp' | 'wta'}
              ranking={rankingAdversario ?? 0}
              nivel={1} // Adversário NPC costuma ser nível 1 ou não mostrado
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
        
        {/* Match Analysis (FM Style) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-3">
            <div className="flex items-center gap-2 mb-1">
              <div className="w-1 h-4" style={{ background: corCardRival }} />
              <span className="arcade-font text-[12px] tracking-widest" style={{ color: corCardRival }}>ANÁLISE DO RIVAL</span>
            </div>
            <div className="app-panel border-2 p-4 relative overflow-hidden" style={{ borderColor: alpha(corCardRival, '66') }}>
              <div className="absolute top-0 right-0 p-2 opacity-5">
                <div className="text-6xl">🎾</div>
              </div>
              <div className="flex justify-between items-start mb-4">
                <div>
                  <div className="arcade-font text-xl text-white mb-1">{adversario.nome}</div>
                  <div className="arcade-font text-[10px] text-[#d49aac] mb-1">
                    {formatarNacionalidade(adversario.nacionalidade)}
                  </div>
                  <div className="arcade-font text-[11px] text-[#888]">
                    {rankingAdversario ? `#${rankingAdversario} MUNDIAL` : 'SEM RANKING'}
                  </div>
                </div>
                <div className="text-right">
                  <div className="arcade-font text-[10px] mb-1" style={{ color: corCardRival }}>
                    OVR {overallCardAdversario}
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-[0.9fr_1.1fr] gap-3 mb-4">
                <div className="p-3 border" style={{ background: alpha(corCardRival, '0d'), borderColor: alpha(corCardRival, '33') }}>
                  <div className="arcade-font text-[10px] tracking-widest mb-1 uppercase" style={{ color: alpha(corCardRival, 'cc') }}>Leitura</div>
                  <div className="arcade-font text-[12px] text-white leading-relaxed">{leituraRival}</div>
                </div>
                <div className="p-3 border" style={{ background: alpha(corCardRival, '0d'), borderColor: alpha(corCardRival, '33') }}>
                  <div className="mb-2 flex items-center justify-between gap-2">
                    <div className="arcade-font text-[10px] tracking-widest uppercase" style={{ color: alpha(corCardRival, 'cc') }}>
                      {abaRival === 'registros' ? 'Últimos Registros' : 'História'}
                    </div>
                    <div className="flex gap-1">
                      <button
                        onClick={() => setAbaRival('registros')}
                        className="border px-2 py-1 arcade-font text-[8px]"
                        style={{
                          borderColor: abaRival === 'registros' ? corCardRival : alpha(corCardRival, '55'),
                          color: abaRival === 'registros' ? '#12060b' : '#ff9bb4',
                          background: abaRival === 'registros' ? corCardRival : 'transparent',
                        }}
                      >
                        REGISTROS
                      </button>
                      <button
                        onClick={() => setAbaRival('historia')}
                        className="border px-2 py-1 arcade-font text-[8px]"
                        style={{
                          borderColor: abaRival === 'historia' ? 'var(--neon-yellow)' : '#6c5f2b',
                          color: abaRival === 'historia' ? '#1b1803' : '#ffe27a',
                          background: abaRival === 'historia' ? 'var(--neon-yellow)' : 'transparent',
                        }}
                      >
                        TÍTULOS
                      </button>
                    </div>
                  </div>
                  {abaRival === 'registros' ? (
                    historicoRival.length > 0 ? (
                      <div className="space-y-1.5">
                        {historicoRival.map(item => (
                          <div key={item} className="arcade-font text-[10px] text-[#ffd7e2] leading-relaxed">
                            {item}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="arcade-font text-[10px] text-[#c18a9d] leading-relaxed">
                        Sem histórico recente salvo para este adversário.
                      </div>
                    )
                  ) : titulosRival.length > 0 ? (
                    <div className="space-y-1.5">
                      {titulosRival.map(item => (
                        <div key={item} className="arcade-font text-[10px] text-[#fff0a6] leading-relaxed">
                          {item}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="arcade-font text-[10px] text-[#c9bc7c] leading-relaxed">
                      Nenhum título registrado para este adversário.
                    </div>
                  )}
                  <button
                    onClick={() => navigate(`/player/${(jogador?.tour ?? 'atp').toLowerCase()}/${encodeURIComponent(adversario.nome)}`)}
                    className="mt-3 arcade-font text-[9px] uppercase underline underline-offset-4"
                    style={{ color: corCardRival }}
                  >
                    Ver dossiê completo
                  </button>
                </div>
              </div>
              <div className="flex items-center justify-end gap-6 mb-4">
                <CircularGauge label="ENERGIA" value={energiaAdversarioAoVivo} color={corCardRival} />
                <CircularGauge label="FADIGA" value={fadigaAdversarioAoVivo} color="var(--neon-yellow)" track="#26131b" />
              </div>
              <OpponentScoutingCard
                adv={adversario}
                scout={scoutRival}
                accent={corCardRival}
                superficie={superficie}
              />
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center gap-2 mb-1">
              <div className="w-1 h-4 bg-neon-green" />
              <span className="arcade-font text-[12px] text-neon-green tracking-widest">SUA CONDIÇÃO</span>
            </div>
            <div className="app-panel border-2 border-neon-green/40 p-4 relative overflow-hidden">
              <div className="absolute top-0 right-0 p-2 opacity-5">
                <div className="text-6xl">🫀</div>
              </div>
              <div className="flex justify-between items-start mb-4">
                <div>
                  <div className="arcade-font text-xl text-white mb-1">{nomeJogador}</div>
                  <div className="arcade-font text-[10px] text-[#92ffd1] mb-1">
                    {formatarNacionalidade(jogador?.nacionalidade)}
                  </div>
                  <div className="arcade-font text-[11px] text-[#888]">
                    #{rankingJogador || '---'} · OVR {overallCardJogador} · {inferirEstilo(jogador?.atributos)}
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-[0.9fr_1.1fr] gap-3 mb-4">
                <div className="bg-neon-green/5 border border-neon-green/20 p-3">
                  <div className="arcade-font text-[10px] text-[#73ffbb] tracking-widest mb-1 uppercase">Leitura</div>
                  <div className="arcade-font text-[12px] text-white leading-relaxed">{leituraJogador}</div>
                </div>
                <div className="bg-neon-green/5 border border-neon-green/20 p-3">
                  <div className="mb-2 flex items-center justify-between gap-2">
                    <div className="arcade-font text-[10px] text-[#73ffbb] tracking-widest uppercase">
                      {abaJogador === 'registros' ? 'Últimos Registros' : 'História'}
                    </div>
                    <div className="flex gap-1">
                      <button
                        onClick={() => setAbaJogador('registros')}
                        className="border px-2 py-1 arcade-font text-[8px]"
                        style={{
                          borderColor: abaJogador === 'registros' ? 'var(--neon-green)' : '#245843',
                          color: abaJogador === 'registros' ? '#02120b' : '#9cf6ce',
                          background: abaJogador === 'registros' ? 'var(--neon-green)' : 'transparent',
                        }}
                      >
                        REGISTROS
                      </button>
                      <button
                        onClick={() => setAbaJogador('historia')}
                        className="border px-2 py-1 arcade-font text-[8px]"
                        style={{
                          borderColor: abaJogador === 'historia' ? 'var(--neon-yellow)' : '#6c5f2b',
                          color: abaJogador === 'historia' ? '#1b1803' : '#ffe27a',
                          background: abaJogador === 'historia' ? 'var(--neon-yellow)' : 'transparent',
                        }}
                      >
                        TÍTULOS
                      </button>
                    </div>
                  </div>
                  {abaJogador === 'registros' ? (
                    historicoJogador.length > 0 ? (
                      <div className="space-y-1.5">
                        {historicoJogador.map(item => (
                          <div key={item} className="arcade-font text-[10px] text-[#d7fff0] leading-relaxed">
                            {item}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="arcade-font text-[10px] text-[#8dbda8] leading-relaxed">
                        Sem histórico recente salvo para o seu jogador.
                      </div>
                    )
                  ) : titulosJogador.length > 0 ? (
                    <div className="space-y-1.5">
                      {titulosJogador.map(item => (
                        <div key={item} className="arcade-font text-[10px] text-[#fff0a6] leading-relaxed">
                          {item}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="arcade-font text-[10px] text-[#c9bc7c] leading-relaxed">
                      Nenhum título registrado para o seu jogador.
                    </div>
                  )}
                </div>
              </div>
              <div className="flex items-center justify-end gap-6 mb-4">
                <CircularGauge label="ENERGIA" value={energiaJogadorAoVivo} color="var(--neon-green)" />
                <CircularGauge label="FADIGA" value={fadigaJogadorAoVivo} color="var(--neon-yellow)" track="#102319" />
              </div>
              <ScoutingReportCard
                titulo="Scouting Report"
                overall={overallCardJogador}
                metrics={{ saque: metricsJogador.saque, fundo: metricsJogador.fundo, mental: metricsJogador.mental }}
                report={reportJogador}
                accent="var(--neon-green)"
              />
            </div>
          </div>
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

        {/* Modo de Acompanhamento (Compacto) */}
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

      </div>

      {/* Botão de Ação Sticky */}
      <div className="sticky bottom-0 z-30 p-4 border-t border-white/10 bg-black/80 backdrop-blur-md">
        {erroEntrada && (
          <div className="mb-3 border border-[#ff4466] bg-[#22040d] px-3 py-2 arcade-font text-[10px] text-[#ff9bb4]">
            {erroEntrada.toUpperCase()}
          </div>
        )}
        <NeonButton 
          variant="green" 
          className="w-full py-5 text-sm" 
          onClick={handleIniciar} 
          blink={simulando}
        >
          {simulando ? 'CALCULANDO ESTRATÉGIAS...' : confirmandoEntrada ? 'CONFIRMAR E ENTRAR EM QUADRA' : 'DEFINIR PLANO E JOGAR'}
        </NeonButton>
      </div>
    </div>
  )
}
