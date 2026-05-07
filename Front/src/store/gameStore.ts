import { create } from 'zustand'
import { api, setApiSaveName } from '../api/client'
import type { JogadorState, TorneioState } from '../types'

interface GameStore {
  // Sessão
  saveAtivo: string | null
  setSaveAtivo: (nome: string | null) => void

  // Jogador
  jogador: JogadorState | null
  setJogador: (j: JogadorState | null) => void
  patchJogador: (parcial: Partial<JogadorState>) => void
  fetchJogador: () => Promise<JogadorState>

  // Semana/temporada
  semana: number
  ano: number
  setSemana: (s: number, a: number) => void

  // Torneio ativo
  torneio: TorneioState | null
  setTorneio: (t: TorneioState | null) => void

  // Partida em andamento
  partidaId: string | null
  setPartidaId: (id: string | null) => void

  // Loading global
  loading: boolean
  setLoading: (v: boolean) => void

  // Reset ao sair/trocar de save
  reset: () => void
}

const defaults = {
  saveAtivo: null,
  jogador: null,
  semana: 1,
  ano: 2025,
  torneio: null,
  partidaId: null,
  loading: false,
}

export const useGameStore = create<GameStore>((set, get) => ({
  ...defaults,

  setSaveAtivo: (nome) => {
    setApiSaveName(nome)
    set({ saveAtivo: nome })
  },

  setJogador: (j) => set({ jogador: j }),

  patchJogador: (parcial) =>
    set((s) => ({ jogador: s.jogador ? { ...s.jogador, ...parcial } : null })),

  fetchJogador: async () => {
    const j = await api.jogador.get()
    set({ jogador: j })
    return j
  },

  setSemana: (semana, ano) => set({ semana, ano }),

  setTorneio: (torneio) => set({ torneio }),

  setPartidaId: (partidaId) => set({ partidaId }),

  setLoading: (loading) => set({ loading }),

  reset: () => {
    setApiSaveName(null)
    set(defaults)
  },
}))
