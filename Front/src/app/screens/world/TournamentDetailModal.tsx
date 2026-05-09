import { useEffect, useState } from 'react'
import { X, Trophy, Users } from 'lucide-react'
import { api } from '../../../api/client'
import { PixelFlag } from '../../components'

export function TournamentDetailModal({
  nome,
  tour,
  onClose,
}: {
  nome: string
  tour: string
  onClose: () => void
}) {
  const [loading, setLoading] = useState(true)
  const [estado, setEstado] = useState<any>(null)

  useEffect(() => {
    api.mundo
      .torneio(nome, tour)
      .then(setEstado)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [nome, tour])

  if (loading) {
    return (
      <div className="fixed inset-0 z-[100] bg-black/90 flex items-center justify-center p-6">
        <div className="pixel-font text-neon-green text-xs animate-pulse">CARREGANDO...</div>
      </div>
    )
  }

  if (!estado) return null

  const data = estado.tournament_data || {}

  return (
    <div className="fixed inset-0 z-[100] bg-black/95 flex flex-col p-4 overflow-y-auto">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          {data.codigo_pais && <PixelFlag countryCode={data.codigo_pais} size="md" />}
          <div className="arcade-font text-xs text-neon-yellow">{nome.toUpperCase()}</div>
        </div>
        <button
          onClick={onClose}
          className="p-2 border-2 border-white/20 text-white active:bg-white/10"
        >
          <X size={20} />
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-4">
        {[
          { label: 'LOCAL', value: `${data.local || '-'}, ${data.pais_sede || '-'}` },
          { label: 'CATEGORIA', value: data.tipo || '-' },
          { label: 'SUPERFÍCIE', value: data.quadra || '-', color: 'var(--neon-green)' },
          { label: 'PRÊMIO', value: data.premiacao ? `$${Number(data.premiacao).toLocaleString()}` : '-', color: 'var(--neon-yellow)' },
        ].map(({ label, value, color }) => (
          <div key={label} className="border border-white/10 bg-black/40 p-3">
            <div className="pixel-font text-[7px] text-[#888]">{label}</div>
            <div className="arcade-font text-[9px] mt-1" style={{ color: color || '#fff' }}>
              {String(value).toUpperCase()}
            </div>
          </div>
        ))}
      </div>

      <div className="space-y-2">
        {[
          { icon: Trophy, label: 'CAMPEÃO SIMPLES', value: estado.campeao_simples || data.ultimo_campeao || '---', color: 'var(--neon-yellow)' },
          { icon: Users, label: 'CAMPEÃO DUPLAS', value: estado.campeao_duplas || data.ultimo_campeao_duplas || '---', color: 'var(--neon-cyan)' },
        ].map(({ icon: Icon, label, value, color }) => (
          <div key={label} className="flex items-center justify-between border border-white/10 bg-black/40 p-3">
            <div className="flex items-center gap-2">
              <Icon size={14} style={{ color }} />
              <div className="pixel-font text-[8px] text-[#888]">{label}</div>
            </div>
            <div className="arcade-font text-[9px]" style={{ color }}>
              {String(value).toUpperCase()}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
