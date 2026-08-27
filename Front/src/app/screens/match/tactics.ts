import type { MatchStrategySummary, PacoteTaticoState } from '../../../types'
import { ESTRATEGIA_PADRAO_UI, MATCH_AUTOSAVE_KEY, MATCH_SETTINGS_KEY, PLANOS } from './constants'
import type {
  AbordagemValor,
  Faixa,
  InstrucaoValor,
  MentalidadeValor,
  PlanoValor,
  SegundoSaqueModo,
} from './types'

export function derivarEstrategia(
  plano: PlanoValor,
  saqueOverride?: string,
  segundoSaque: SegundoSaqueModo = 'SEGURO',
): string {
  const p = PLANOS.find(x => x.valor === plano)!
  const estilo = p.estilo
  const saque = saqueOverride || p.saque
  let estrategiaBase = 'EQUILIBRADO'
  if (estilo === 'SERVE E VOLEIO') estrategiaBase = 'SERVE E VOLEIO'
  else if (estilo === 'BASELINE') estrategiaBase = saque === 'AGRESSIVO' ? 'AGRESSIVO' : 'BASELINE'
  return `${estrategiaBase}::${segundoSaque.toLowerCase()}`
}

export function inferirPlanoDoPacote(
  mentalidade: MentalidadeValor,
  abordagem: AbordagemValor,
  instrucao: InstrucaoValor,
): PlanoValor {
  if (mentalidade === 'OFENSIVA' || abordagem === 'SERVE_VOLLEY') return 'pressionar'
  if (mentalidade === 'DEFENSIVA' || abordagem === 'COUNTER' || instrucao === 'TROCAS_LONGAS') return 'consistencia'
  return 'variar'
}

export function carregarPacoteTaticoInicial(): PacoteTaticoState {
  const padrao: PacoteTaticoState = {
    mentalidade: 'EQUILIBRADA',
    abordagem: 'BASELINE',
    instrucao: 'PADRAO',
    segundoSaque: 'SEGURO',
    modo: 'detalhado',
  }
  if (typeof window === 'undefined') return padrao
  try {
    const bruto = window.localStorage.getItem(MATCH_SETTINGS_KEY)
    if (!bruto) return padrao
    const salvo = JSON.parse(bruto) as Partial<PacoteTaticoState>
    return {
      mentalidade: salvo.mentalidade === 'OFENSIVA' || salvo.mentalidade === 'DEFENSIVA' ? salvo.mentalidade : 'EQUILIBRADA',
      abordagem: salvo.abordagem === 'SERVE_VOLLEY' || salvo.abordagem === 'COUNTER' ? salvo.abordagem : 'BASELINE',
      instrucao:
        salvo.instrucao === 'FORCAR_BACKHAND' || salvo.instrucao === 'TROCAS_LONGAS' || salvo.instrucao === 'ATACAR_SAQUE'
          ? salvo.instrucao
          : 'PADRAO',
      segundoSaque: salvo.segundoSaque === 'FORCAR' ? 'FORCAR' : 'SEGURO',
      modo: salvo.modo === 'estrategista' || salvo.modo === 'auto' || salvo.modo === 'game' ? salvo.modo : 'detalhado',
    }
  } catch {
    return padrao
  }
}

export function carregarPreferenciaAutoSave(): boolean {
  if (typeof window === 'undefined') return false
  return window.localStorage.getItem(MATCH_AUTOSAVE_KEY) === 'true'
}

export function estrategiaPonto(intencao: string, faixa: Faixa): string {
  if (faixa === 'REDE') return 'rede'
  if (intencao === 'ARRISCAR') return 'agressivo'
  if (intencao === 'DEFENSIVO') return 'defensivo'
  if (faixa === 'MEIO') return 'variado'
  return 'baseline'
}

export function inferirEstilo(atributos?: Record<string, number>): string {
  if (!atributos) return 'Equilibrado'
  const saque = atributos.saque ?? atributos.vel_saque ?? 50
  const voleio = atributos.voleio ?? 50
  const winner = atributos.winner ?? 50
  const movimento = atributos.movimento ?? atributos.velocidade ?? 50
  if (saque >= 72 && voleio >= 66) return 'Serve & Voleio'
  if (winner >= 72 && saque >= 68) return 'Agressivo'
  if (movimento >= 70) return 'Baseline'
  return 'Equilibrado'
}

export function serializarPacoteTatico(
  mentalidade: MentalidadeValor,
  abordagem: AbordagemValor,
  instrucao: InstrucaoValor,
  segundoSaque: SegundoSaqueModo,
): string {
  return `fm|${mentalidade}|${abordagem}|${instrucao}|${segundoSaque}`
}

export function traduzirCampoEstrategia(valor?: string): string {
  const v = String(valor ?? '').trim().toLowerCase()
  if (v === 'atacar_na_rede') return 'Saque e rede'
  if (v === 'atacar_do_fundo') return 'Fundo agressivo'
  if (v === 'atacar_pelo_meio') return 'All court'
  if (v === 'forcar') return 'Forçar'
  if (v === 'seguro') return 'Seguro'
  if (v === 'agressivo') return 'Agressivo'
  if (v === 'variado') return 'Variado'
  if (v === 'arriscar') return 'Arriscar'
  if (v === 'paciente') return 'Paciente'
  if (v === 'defensivo') return 'Defensivo'
  if (v === 'ofensiva') return 'Ofensiva'
  if (v === 'equilibrada') return 'Equilibrada'
  if (v === 'serve_volley') return 'Saque e rede'
  if (v === 'baseline') return 'Baseline'
  if (v === 'counter') return 'Contra-ataque'
  if (v === 'padrao') return 'Padrão'
  if (v === 'forcar_backhand') return 'Forçar backhand'
  if (v === 'trocas_longas') return 'Trocas longas'
  if (v === 'atacar_saque') return 'Atacar 2º saque'
  return valor ? String(valor) : '--'
}

export function resumirEstrategiaLado(estrategia?: MatchStrategySummary): string[] {
  const dados = { ...ESTRATEGIA_PADRAO_UI, ...(estrategia ?? {}) }
  return [
    `Estilo: ${traduzirCampoEstrategia(dados.estilo)}`,
    `Intenção: ${traduzirCampoEstrategia(dados.intencao)}`,
    `1º saque: ${traduzirCampoEstrategia(dados.saque_tipo)}`,
    `2º saque: ${traduzirCampoEstrategia(dados.saque)}`,
  ]
}
