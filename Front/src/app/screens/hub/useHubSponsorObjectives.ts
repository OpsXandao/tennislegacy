import { useEffect, useState } from 'react'

import { api } from '../../../api/client'
import type { Patrocinio } from '../../../types'

export function useHubSponsorObjectives() {
  const [contratos, setContratos] = useState<Patrocinio[]>([])

  useEffect(() => {
    let ativo = true
    api.patrocinio
      .ativos()
      .then((res) => {
        if (ativo) {
          setContratos(res.patrocinios)
        }
      })
      .catch(() => {
        if (ativo) {
          setContratos([])
        }
      })
    return () => {
      ativo = false
    }
  }, [])

  return {
    contratos,
    principal: contratos[0] ?? null,
  }
}
