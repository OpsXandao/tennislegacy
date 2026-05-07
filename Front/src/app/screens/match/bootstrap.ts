import type {
  AdversarioInfo as ApiAdversarioInfo,
  MatchPointRuntime,
  MatchStrategySummary,
  PlacarState,
  TorneioState,
} from '../../../types'
import { inferirEstilo } from './model'
import type { AdversarioInfo, ModoAcomp } from './types'

export function modoAcompanhamentoDaApi(modo?: string): ModoAcomp {
  return modo === 'estrategista' || modo === 'auto' || modo === 'game'
    ? modo
    : 'detalhado'
}

export function mapApiAdversarioParaMatch(
  adv: ApiAdversarioInfo,
): AdversarioInfo {
  return {
    nome: adv.nome || 'ADVERSÁRIO',
    nacionalidade: adv.nacionalidade ?? null,
    idade: Number(adv.idade ?? 0) || null,
    altura: Number(adv.altura ?? 0) || null,
    peso: Number(adv.peso ?? 0) || null,
    maoDominante: adv.mao_dominante ?? null,
    reves: adv.reves ?? null,
    energia: Number(adv.energia ?? 100),
    fadiga: Number(adv.fadiga ?? 0),
    ranking: adv.ranking ?? adv.ranking_pos ?? null,
    overall: Number(adv.overall ?? adv.atributos?.overall ?? 0) || null,
    trofeus: Array.isArray(adv.trofeus) ? adv.trofeus : [],
    atributos: adv.atributos,
    atributosPsicologicos: adv.atributos_psicologicos,
    historicoTorneios: Array.isArray(adv.historico_torneios)
      ? adv.historico_torneios
      : [],
    historicoPartidas: Array.isArray(adv.historico_partidas)
      ? adv.historico_partidas
      : [],
    resumoFifa: adv.resumo_fifa,
    carta: adv.carta,
    overallBoosted: adv.carta?.overall_boosted,
    atributosBoosted: adv.carta?.atributos_boosted,
    estilo: adv.estilo_jogo ?? inferirEstilo(adv.atributos),
  }
}

export function extrairAdversarioInfoPartida(
  torneio: TorneioState,
  nomeJogador: string,
): ApiAdversarioInfo | null {
  const infoPartida = torneio.info_partida
  if (!infoPartida) return null
  if (infoPartida.adversario) return infoPartida.adversario

  const meu = nomeJogador.trim().toLowerCase()
  const j1 = infoPartida.jogador1
  const j2 = infoPartida.jogador2
  const nomeAdv = j1.trim().toLowerCase() === meu ? j2 : j1
  return nomeAdv ? { nome: nomeAdv } : null
}

export interface RuntimeStateUpdate {
  placar: PlacarState
  energiaJogador: number | null
  fadigaJogador: number | null
  energiaAdversario: number | null
  fadigaAdversario: number | null
  estrategiaJogador: MatchStrategySummary | null
  estrategiaAdversario: MatchStrategySummary | null
}

export function extrairAtualizacaoRuntime(
  estado: PlacarState | MatchPointRuntime,
): RuntimeStateUpdate {
  const runtime = estado as Partial<MatchPointRuntime>
  return {
    placar: estado,
    energiaJogador:
      typeof runtime.energia_j === 'number' ? Number(runtime.energia_j) : null,
    fadigaJogador:
      typeof runtime.fadiga_j === 'number' ? Number(runtime.fadiga_j) : null,
    energiaAdversario:
      typeof runtime.energia_a === 'number' ? Number(runtime.energia_a) : null,
    fadigaAdversario:
      typeof runtime.fadiga_a === 'number' ? Number(runtime.fadiga_a) : null,
    estrategiaJogador: runtime.estrategia_j ?? null,
    estrategiaAdversario: runtime.estrategia_a ?? null,
  }
}
