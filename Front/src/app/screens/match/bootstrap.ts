import type {
  AdversarioInfo as ApiAdversarioInfo,
  JogadorState,
  MatchPointRuntime,
  PlacarState,
  TorneioState,
} from '../../../types'
import { inferirEstilo } from './model'
import type { AdversarioInfo, ModoAcomp } from './types'

export interface MatchSyntheticEvent extends PlacarState {
  tipo: 'setup' | 'set' | 'fim'
  descricao: string
}

export type MatchScreenState = PlacarState | MatchPointRuntime | MatchSyntheticEvent

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
  tipo: MatchPointRuntime['tipo'] | MatchSyntheticEvent['tipo'] | ''
  descricao: string
  energiaJogador: number | null
  fadigaJogador: number | null
  energiaAdversario: number | null
  fadigaAdversario: number | null
  estrategiaJogador: MatchPointRuntime['estrategia_j'] | null
  estrategiaAdversario: MatchPointRuntime['estrategia_a'] | null
}

function isMatchRuntime(estado: MatchScreenState): estado is MatchPointRuntime {
  return 'energia_j' in estado && 'energia_a' in estado
}

export function extrairAtualizacaoRuntime(
  estado: MatchScreenState,
): RuntimeStateUpdate {
  const runtime = isMatchRuntime(estado) ? estado : null
  return {
    placar: estado,
    tipo: 'tipo' in estado ? estado.tipo : '',
    descricao: 'descricao' in estado ? estado.descricao : '',
    energiaJogador:
      runtime && typeof runtime.energia_j === 'number'
        ? Number(runtime.energia_j)
        : null,
    fadigaJogador:
      runtime && typeof runtime.fadiga_j === 'number'
        ? Number(runtime.fadiga_j)
        : null,
    energiaAdversario:
      runtime && typeof runtime.energia_a === 'number'
        ? Number(runtime.energia_a)
        : null,
    fadigaAdversario:
      runtime && typeof runtime.fadiga_a === 'number'
        ? Number(runtime.fadiga_a)
        : null,
    estrategiaJogador: runtime?.estrategia_j ?? null,
    estrategiaAdversario: runtime?.estrategia_a ?? null,
  }
}

export function criarEventoLocalDePlacar(
  placar: PlacarState,
  tipo: MatchSyntheticEvent['tipo'],
  descricao = '',
): MatchSyntheticEvent {
  return {
    ...placar,
    tipo,
    descricao,
  }
}

export function extrairHistoricoJogador(
  jogador: JogadorState | null | undefined,
): Array<Record<string, unknown>> {
  return Array.isArray(jogador?.historico_partidas)
    ? jogador.historico_partidas
    : []
}

export function extrairHistoricoTorneiosJogador(
  jogador: JogadorState | null | undefined,
): Array<Record<string, unknown>> {
  return Array.isArray(jogador?.historico_torneios)
    ? jogador.historico_torneios
    : []
}

export function extrairTrofeusJogador(
  jogador: JogadorState | null | undefined,
): Array<Record<string, unknown>> {
  return Array.isArray(jogador?.trofeus) ? jogador.trofeus : []
}
