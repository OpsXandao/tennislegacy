import { Mail, Check, X, Trash2 } from 'lucide-react'
import { NeonCard } from '../../components'

interface Props {
  emails: any[]
  processandoId: string | null
  onAcao: (id: string, acao: 'aceitar' | 'recusar' | 'deletar') => Promise<void>
}

function isEmailAcionavel(tipo?: string) {
  return ['proposta_patrocinio', 'convite_duplas', 'patrocinio', 'empresario', 'proposta_empresario'].includes(tipo || '')
}

export function EmailTab({ emails, processandoId, onAcao }: Props) {
  if (emails.length === 0) {
    return (
      <div className="text-center py-12 arcade-font text-[10px] text-[#444]">CAIXA VAZIA</div>
    )
  }

  return (
    <div className="space-y-3">
      {emails.map((email, i) => (
        <NeonCard
          key={email.id || i}
          variant="pink"
          hover={false}
          className={processandoId === email.id ? 'opacity-50' : ''}
        >
          <div className="flex items-start gap-3">
            <Mail className="text-neon-pink shrink-0 mt-0.5" size={16} />
            <div className="flex-1 min-w-0">
              <div className="arcade-font text-[10px] text-white font-bold mb-1 uppercase">
                {email.assunto || email.titulo || 'PROPOSTA DE CARREIRA'}
              </div>
              <p className="arcade-font text-[9px] text-[#888] mb-3 leading-relaxed">{email.corpo || email.mensagem}</p>
              <div className="flex gap-2">
                {isEmailAcionavel(email.tipo) ? (
                  <>
                    <button
                      onClick={() => onAcao(email.id, 'aceitar')}
                      className="bg-neon-green/20 border border-neon-green text-neon-green px-3 py-1 arcade-font text-[8px] flex items-center gap-1"
                    >
                      <Check size={10} /> ACEITAR
                    </button>
                    <button
                      onClick={() => onAcao(email.id, 'recusar')}
                      className="bg-neon-pink/20 border border-neon-pink text-neon-pink px-3 py-1 arcade-font text-[8px] flex items-center gap-1"
                    >
                      <X size={10} /> RECUSAR
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => onAcao(email.id, 'deletar')}
                    className="bg-[#444] border border-[#666] text-white px-3 py-1 arcade-font text-[8px] flex items-center gap-1"
                  >
                    <Trash2 size={10} /> APAGAR
                  </button>
                )}
              </div>
            </div>
          </div>
        </NeonCard>
      ))}
    </div>
  )
}
