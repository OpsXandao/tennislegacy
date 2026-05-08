import { PageHeader } from '../components'
import { ActiveSponsorList } from './sponsor/ActiveSponsorList'
import { SponsorFeedback } from './sponsor/SponsorFeedback'
import { SponsorOverview } from './sponsor/SponsorOverview'
import { SponsorSection } from './sponsor/SponsorSection'
import { useSponsorContracts } from './sponsor/useSponsorContracts'

export function SponsorScreen() {
  const { ativos, assinando, contexto, disponiveis, loading, mensagem, assinar } =
    useSponsorContracts()

  const elegiveis = disponiveis.filter((p) => p.elegivel)
  const bloqueados = disponiveis.filter((p) => !p.elegivel)

  return (
    <div className="app-shell min-h-screen font-mono pb-24">
      <PageHeader title="PATROCÍNIOS" color="gold" backTo="/player">
        <p className="text-[9px] text-[#ffe600]/60 mt-1" style={{ fontFamily: 'var(--font-mono)' }}>
          GERENCIE CONTRATOS E ASSINE NOVOS PATROCINADORES
        </p>
      </PageHeader>

      <div className="p-4 space-y-6">
        <SponsorFeedback mensagem={mensagem} />
        <SponsorOverview contexto={contexto} />
        <ActiveSponsorList ativos={ativos} />

        {loading ? (
          <div
            className="text-[10px] text-[#ffe600]/60 text-center py-8"
            style={{ fontFamily: 'var(--font-arcade)' }}
          >
            CARREGANDO...
          </div>
        ) : (
          <>
            <SponsorSection
              titulo="DISPONÍVEIS"
              colorClass="text-[#00ff88]"
              icon="money"
              itens={elegiveis}
              assinando={assinando}
              onAssinar={assinar}
            />
            <SponsorSection
              titulo="BLOQUEADOS"
              colorClass="text-white/30"
              icon="lock"
              itens={bloqueados}
              assinando={assinando}
              onAssinar={assinar}
            />

            {disponiveis.length === 0 && (
              <div
                className="text-[10px] text-white/30 text-center py-12"
                style={{ fontFamily: 'var(--font-arcade)' }}
              >
                NENHUM PATROCINADOR DISPONÍVEL
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
