import { motion } from 'motion/react'

interface StatItem {
  label: string
  value: string
  color: string
}

interface RankingStatsProps {
  stats: StatItem[]
}

export function RankingStats({ stats }: RankingStatsProps) {
  return (
    <div className="mb-6 border-2 border-[#00ff88] bg-[#1a1a2e] p-4" style={{ boxShadow: 'var(--glow-green)' }}>
      <div className="mb-4 text-[10px] tracking-wider text-[#00ff88]" style={{ fontFamily: 'var(--font-arcade)' }}>
        SUAS ESTATÍSTICAS
      </div>
      <div className="grid grid-cols-2 gap-3">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.08 }}
            className="border-2 border-[#00e5ff] bg-black p-3 text-center"
          >
            <div className="mb-1 text-[8px] text-[#888]">{stat.label}</div>
            <div className="text-2xl font-bold" style={{ color: stat.color, fontFamily: 'var(--font-arcade)' }}>
              {stat.value}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
