import { useCallback, useEffect, useState } from 'react'

import { api, ApiError } from '../../../api/client'
import type {
  Patrocinio,
  PatrocinioContexto,
  PatrocinioDisponivel,
} from '../../../types'

type Feedback = { texto: string; ok: boolean } | null

const EMPTY_CONTEXTO: PatrocinioContexto = {
  ranking_atual: 0,
  seguidores_atuais: 0,
  patrocinios_ativos: 0,
  slots_menores_restantes: 0,
  slot_master_disponivel: true,
}

export function useSponsorContracts() {
  const [disponiveis, setDisponiveis] = useState<PatrocinioDisponivel[]>([])
  const [ativos, setAtivos] = useState<Patrocinio[]>([])
  const [contexto, setContexto] = useState<PatrocinioContexto>(EMPTY_CONTEXTO)
  const [loading, setLoading] = useState(true)
  const [mensagem, setMensagem] = useState<Feedback>(null)
  const [assinando, setAssinando] = useState<string | null>(null)

  const carregar = useCallback(async () => {
    try {
      const [disponiveisResp, ativosResp] = await Promise.all([
        api.patrocinio.disponiveis(),
        api.patrocinio.ativos(),
      ])
      setDisponiveis(disponiveisResp.patrocinadores)
      setContexto(disponiveisResp.contexto)
      setAtivos(ativosResp.patrocinios)
    } catch {
      setDisponiveis([])
      setAtivos([])
      setContexto(EMPTY_CONTEXTO)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    carregar()
  }, [carregar])

  const assinar = useCallback(
    async (id: string) => {
      setAssinando(id)
      setMensagem(null)
      try {
        const res = await api.patrocinio.assinar(id)
        setMensagem({ texto: res.mensagem, ok: res.ok })
        if (res.ok) {
          await carregar()
        }
      } catch (error) {
        const texto =
          error instanceof ApiError
            ? error.message
            : 'Erro ao assinar patrocínio.'
        setMensagem({ texto, ok: false })
      } finally {
        setAssinando(null)
      }
    },
    [carregar]
  )

  return {
    ativos,
    assinando,
    contexto,
    disponiveis,
    loading,
    mensagem,
    assinar,
  }
}
