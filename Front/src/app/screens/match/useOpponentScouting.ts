import { useEffect, useState } from 'react'

import { api } from '../../../api/client'
import type { PartidaScout } from '../../../types'

export function useOpponentScouting(
  fase: string,
  nomeAdversario: string,
) {
  const [scout, setScout] = useState<PartidaScout | null>(null)

  useEffect(() => {
    if (fase !== 'setup' || !nomeAdversario) {
      return
    }

    let ativo = true
    api.partida
      .scout(nomeAdversario)
      .then((payload) => {
        if (ativo) {
          setScout(payload)
        }
      })
      .catch(() => {
        if (ativo) {
          setScout(null)
        }
      })

    return () => {
      ativo = false
    }
  }, [fase, nomeAdversario])

  return scout
}
