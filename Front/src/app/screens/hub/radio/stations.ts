export interface HubRadioStation {
  id: string
  nome: string
  tagline: string
  bpm: number
  rootHz: number
  color: string
  bassPattern: Array<number | null>
  leadPattern: Array<number | null>
  kickPattern: boolean[]
  hatPattern: boolean[]
}

export const HUB_RADIO_STATIONS: HubRadioStation[] = [
  {
    id: 'centre-court-fm',
    nome: 'CENTRE COURT FM',
    tagline: 'synth-pop de pré-jogo',
    bpm: 106,
    rootHz: 220,
    color: 'var(--neon-green)',
    bassPattern: [0, null, 0, null, 3, null, 5, null, 7, null, 5, null, 3, null, 2, null],
    leadPattern: [12, 14, null, 12, 15, null, 14, null, 12, 14, null, 17, 15, null, 14, null],
    kickPattern: [true, false, false, false, true, false, false, false, true, false, false, false, true, false, false, false],
    hatPattern: [false, false, true, false, false, false, true, false, false, false, true, false, false, false, true, false],
  },
  {
    id: 'clay-pulse',
    nome: 'CLAY PULSE',
    tagline: 'groove quente de saibro',
    bpm: 94,
    rootHz: 196,
    color: '#ff8c42',
    bassPattern: [0, null, 0, null, 5, null, 3, null, 0, null, 7, null, 5, null, 3, null],
    leadPattern: [7, null, 10, null, 12, null, 10, null, 7, null, 5, null, 3, null, 2, null],
    kickPattern: [true, false, false, false, false, false, true, false, true, false, false, false, false, false, true, false],
    hatPattern: [false, true, false, true, false, true, false, true, false, true, false, true, false, true, false, true],
  },
  {
    id: 'tiebreak-night',
    nome: 'TIE-BREAK NIGHT',
    tagline: 'arcade club para decisão',
    bpm: 126,
    rootHz: 246.94,
    color: 'var(--neon-cyan)',
    bassPattern: [0, null, 7, null, 5, null, 3, null, 0, null, 7, null, 10, null, 5, null],
    leadPattern: [12, null, 15, 14, 17, null, 19, 17, 15, null, 14, 12, 10, null, 12, 14],
    kickPattern: [true, false, false, false, true, false, true, false, true, false, false, false, true, false, true, false],
    hatPattern: [false, true, true, true, false, true, true, true, false, true, true, true, false, true, true, true],
  },
]
