import type { Transaction } from '../../../types'

function fmt(v: number) {
  if (v >= 1_000_000) return `$${(v / 1_000_000).toFixed(1)}M`
  if (v >= 1_000) return `$${(v / 1_000).toFixed(0)}K`
  return `$${v}`
}

interface Props {
  financeiro: {
    saldo: number
    transacoes: Transaction[]
    resumo_categorias: Record<string, number>
  }
}

export function FinanceiroTab({ financeiro }: Props) {
  return (
    <div className="space-y-3">
      <div className="border-2 border-neon-green bg-[#111] p-4 text-center">
        <div className="arcade-font text-[8px] text-[#888] mb-1">SALDO ATUAL</div>
        <div className="pixel-font text-3xl text-neon-green">{fmt(financeiro.saldo)}</div>
      </div>

      {Object.keys(financeiro.resumo_categorias).length > 0 && (
        <div className="border border-[#333] bg-[#111]">
          <div className="border-b border-[#333] px-3 py-2 arcade-font text-[9px] text-neon-yellow">
            TOTAIS POR CATEGORIA
          </div>
          <div className="divide-y divide-[#1a1a1a]">
            {Object.entries(financeiro.resumo_categorias)
              .sort(([, a], [, b]) => b - a)
              .map(([cat, total]) => (
                <div key={cat} className="flex items-center justify-between px-3 py-2">
                  <span className="arcade-font text-[9px] text-[#888] capitalize">{cat}</span>
                  <span className={`pixel-font text-[10px] ${total >= 0 ? 'text-neon-green' : 'text-neon-pink'}`}>
                    {total >= 0 ? '+' : ''}{fmt(total)}
                  </span>
                </div>
              ))}
          </div>
        </div>
      )}

      <div className="border border-[#333] bg-[#111]">
        <div className="border-b border-[#333] px-3 py-2 arcade-font text-[9px] text-neon-cyan">
          ÚLTIMAS TRANSAÇÕES
        </div>
        <div className="divide-y divide-[#1a1a1a]">
          {financeiro.transacoes.length === 0 ? (
            <div className="px-3 py-4 text-center arcade-font text-[9px] text-[#444]">Sem transações</div>
          ) : (
            [...financeiro.transacoes].reverse().map((t, i) => (
              <div key={i} className="px-3 py-2">
                <div className="flex items-center justify-between mb-0.5">
                  <span className="arcade-font text-[9px] text-white truncate max-w-[180px]">{t.descricao}</span>
                  <span className={`pixel-font text-[10px] shrink-0 ml-2 ${t.valor >= 0 ? 'text-neon-green' : 'text-neon-pink'}`}>
                    {t.valor >= 0 ? '+' : ''}{fmt(t.valor)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="arcade-font text-[7px] text-[#444]">S{t.semana} • {t.categoria}</span>
                  {t.saldo_pos !== undefined && (
                    <span className="arcade-font text-[7px] text-[#444]">saldo: {fmt(t.saldo_pos)}</span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
