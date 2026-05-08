interface RankingFiltersProps {
  filtroTab: string
  setFiltroTab: (tab: any) => void
  filtroValor: string
  setFiltroValor: (valor: string) => void
  filtroLabel: string
  rankingFiltradoCount: number
  totalCount: number
}

export function RankingFilters({
  filtroTab,
  setFiltroTab,
  filtroValor,
  setFiltroValor,
  filtroLabel,
  rankingFiltradoCount,
  totalCount,
}: RankingFiltersProps) {
  return (
    <div className="mb-4 border border-[#00e5ff]/30 bg-[#111927] p-3">
      <div className="mb-3 flex flex-wrap gap-2">
        {([
          ['nome', 'NOME'],
          ['nacionalidade', 'NAÇÃO'],
          ['idade', 'IDADE'],
          ['pontos', 'PONTOS'],
        ] as const).map(([valor, label]) => (
          <button
            key={valor}
            onClick={() => setFiltroTab(valor)}
            className="border px-3 py-2 text-[8px] arcade-font transition-all"
            style={{
              borderColor: filtroTab === valor ? '#00e5ff' : '#274050',
              background: filtroTab === valor ? '#00e5ff' : 'transparent',
              color: filtroTab === valor ? '#061118' : '#88bfd5',
            }}
          >
            {label}
          </button>
        ))}
      </div>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-[1fr_auto]">
        <input
          value={filtroValor}
          onChange={(e) => setFiltroValor(e.target.value)}
          placeholder={`Filtrar por ${filtroLabel.toLowerCase()}...`}
          className="border border-[#284657] bg-black px-3 py-3 arcade-font text-[10px] text-[#d8eef8] outline-none placeholder:text-[#5e7e8f]"
        />
        <div className="flex items-center justify-center border border-[#284657] bg-black px-3 py-3 arcade-font text-[9px] text-[#ffe600]">
          {rankingFiltradoCount} / {totalCount} jogadores
        </div>
      </div>
    </div>
  )
}
