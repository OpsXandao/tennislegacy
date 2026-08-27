import type { MatchStrategySummary, PlacarState } from '../../../types'
import type {
  Faixa,
  ModoAcomp,
  PlanoValor,
  Alvo,
  VelocidadeRapida,
} from './types'

export const ESTRATEGIA_PADRAO_UI: MatchStrategySummary = {
  estilo: 'atacar_do_fundo',
  saque: 'seguro',
  saque_tipo: 'variado',
  intencao: 'paciente',
}

export const PLANOS = [
  {
    valor: 'pressionar' as PlanoValor,
    label: 'PRESSIONAR',
    desc: 'Saque forte · atacar à rede',
    estilo: 'SERVE E VOLEIO',
    saque: 'AGRESSIVO',
    color: 'var(--neon-pink)',
    forca: 'Encurta pontos e força erros sob pressão.',
    risco: 'Gasta mais energia e pune mal posicionamento.',
  },
  {
    valor: 'consistencia' as PlanoValor,
    label: 'CONSISTÊNCIA',
    desc: 'Rally longo · errar pouco',
    estilo: 'BASELINE',
    saque: 'SEGURO',
    color: 'var(--neon-cyan)',
    forca: 'Controla o ritmo e reduz erros não forçados.',
    risco: 'Dá menos pontos grátis e depende de paciência.',
  },
  {
    valor: 'variar' as PlanoValor,
    label: 'VARIAR',
    desc: 'Mudanças de ritmo · surpresas',
    estilo: 'EQUILIBRADO',
    saque: 'VARIADO',
    color: 'var(--neon-yellow)',
    forca: 'Quebra padrão do rival e mistura alturas e zonas.',
    risco: 'Se executado mal, entrega iniciativa ao adversário.',
  },
] as const

export const MODOS_ACOMP = [
  {
    valor: 'estrategista' as ModoAcomp,
    label: 'MANUAL',
    desc: 'Você decide ponto a ponto.',
  },
  {
    valor: 'detalhado' as ModoAcomp,
    label: 'RÁPIDA',
    desc: 'A partida avança sozinha, mas você ainda pode retomar o controle.',
  },
  {
    valor: 'auto' as ModoAcomp,
    label: 'ATÉ O FIM',
    desc: 'Simula a partida inteira no ritmo máximo.',
  },
] as const

export const MODOS_VISIVEIS = MODOS_ACOMP.filter((m) => m.valor !== 'game')

export const VELOCIDADES_RAPIDAS = [
  { valor: 'lenta' as VelocidadeRapida, label: '1X', desc: 'Leitura confortável', delay: 1200 },
  { valor: 'normal' as VelocidadeRapida, label: '2X', desc: 'Ritmo padrão', delay: 700 },
  { valor: 'rapida' as VelocidadeRapida, label: '4X', desc: 'Clima Brasfoot', delay: 350 },
  { valor: 'turbo' as VelocidadeRapida, label: '8X', desc: 'Máxima velocidade', delay: 150 },
] as const

export const FAIXAS: { valor: Faixa; label: string }[] = [
  { valor: 'FUNDO', label: 'FND' },
  { valor: 'MEIO', label: 'MIO' },
  { valor: 'REDE', label: 'RDE' },
]

export const ALVOS: { valor: Alvo; label: string }[] = [
  { valor: 'ESQUERDA', label: 'ESQ' },
  { valor: 'CENTRO', label: 'CTR' },
  { valor: 'DIREITA', label: 'DIR' },
]

export const PLACAR_INICIAL: PlacarState = {
  sets: [0, 0],
  games: [0, 0],
  pontos: ['0', '0'],
  servindo: 'jogador',
  log: [],
  encerrado: false,
}

export const COURT_COLORS = { hard: '#1e3a5f', clay: '#8b3a1e', grass: '#1a4a25' } as const
export const MATCH_SETTINGS_KEY = 'tennislegacy.match.tactical-package'
export const MATCH_AUTOSAVE_KEY = 'tennislegacy.match.autosave'
