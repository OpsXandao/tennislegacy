import type { RankingEntry } from '../../../types'
import type { JogadorState } from '../../../types'

export type Tour = 'atp' | 'wta' | 'davis'
export type Modalidade = 'simples' | 'duplas' | 'clay' | 'hard' | 'grass'
export type FiltroTab = 'nome' | 'nacionalidade' | 'idade' | 'pontos'

export const SUP_MAP: Partial<Record<Modalidade, string>> = {
  clay: 'clay',
  hard: 'hard',
  grass: 'grass',
}

export const SUPERFICIES_LABEL: Partial<Record<Modalidade, string>> = {
  clay: 'ARGILA',
  hard: 'DURO',
  grass: 'GRAMA',
}

export function formatDateLabel() {
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(new Date()).toUpperCase()
}

export function filtrarRanking(
  ranking: RankingEntry[],
  filtroTab: FiltroTab,
  filtroValor: string,
) {
  const termo = filtroValor.trim().toLowerCase()
  let lista = [...ranking]

  if (termo) {
    if (filtroTab === 'nome') {
      lista = lista.filter((player) => player.nome.toLowerCase().includes(termo))
    } else if (filtroTab === 'nacionalidade') {
      lista = lista.filter((player) =>
        String(player.nacionalidade ?? '').toLowerCase().includes(termo)
      )
    } else if (filtroTab === 'idade') {
      const min = Number(termo)
      if (Number.isFinite(min) && min > 0) {
        lista = lista.filter((player) => Number(player.idade ?? 0) >= min)
      }
    } else if (filtroTab === 'pontos') {
      const min = Number(termo.replace(/\./g, '').replace(',', '.'))
      if (Number.isFinite(min) && min > 0) {
        lista = lista.filter((player) => Number(player.pontos ?? 0) >= min)
      }
    }
  }

  if (filtroTab === 'idade') {
    lista.sort(
      (a, b) => Number(b.idade ?? 0) - Number(a.idade ?? 0) || a.posicao - b.posicao
    )
  } else if (filtroTab === 'pontos') {
    lista.sort(
      (a, b) => Number(b.pontos ?? 0) - Number(a.pontos ?? 0) || a.posicao - b.posicao
    )
  }

  return lista
}

export function construirStats(
  jogador: JogadorState | null,
  tour: Tour,
  modalidade: Modalidade,
  ranking: RankingEntry[],
) {
  const bestRanking =
    tour === 'davis'
      ? '-'
      : modalidade === 'simples'
        ? jogador?.ranking ?? ranking.find((player) => player.nome === jogador?.nome)?.posicao ?? '-'
        : ranking.find((player) => player.nome === jogador?.nome)?.posicao ?? '-'

  return [
    { label: 'SEU RANKING', value: `#${bestRanking}`, color: '#ffe600' },
    {
      label: 'PONTOS',
      value: String(
        (tour === 'davis'
          ? ranking[0]?.pontos ?? 0
          : modalidade === 'simples'
            ? jogador?.pontos
            : ranking.find((player) => player.nome === jogador?.nome)?.pontos ?? 0
        )?.toLocaleString('pt-BR') ?? '0'
      ),
      color: '#00ff88',
    },
    {
      label: 'TOUR',
      value: String((tour === 'davis' ? 'DAVIS' : jogador?.tour || tour).toUpperCase()),
      color: '#00e5ff',
    },
    { label: 'NÍVEL', value: String(jogador?.nivel ?? 1), color: '#ffe600' },
  ]
}
