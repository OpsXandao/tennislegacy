import { useState } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import { PageHeader } from '../components'
import { AoVivoTab } from './world/AoVivoTab'
import { RaceTab } from './world/RaceTab'
import { ProximosTab } from './world/ProximosTab'

const TABS = [
  { id: 'proximos', label: 'PRÓXIMOS' },
  { id: 'ao-vivo', label: 'AO VIVO' },
  { id: 'race', label: 'RACE' },
] as const

type TabId = (typeof TABS)[number]['id']

export function WorldScreen() {
  const [activeTab, setActiveTab] = useState<TabId>('ao-vivo')

  return (
    <div className="app-shell min-h-screen font-mono pb-24">
      <PageHeader title="WORLD TOUR" subtitle="CIRCUITO MUNDIAL" color="yellow" backTo="/hub" />

      <div className="p-4 space-y-4">
        <div className="flex gap-1">
          {TABS.map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`flex-1 py-2 arcade-font text-[8px] border-2 transition-colors ${
                activeTab === t.id
                  ? 'bg-neon-yellow text-black border-neon-yellow'
                  : 'border-white/20 text-[#888]'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.15 }}
          >
            {activeTab === 'proximos' && <ProximosTab />}
            {activeTab === 'ao-vivo' && <AoVivoTab />}
            {activeTab === 'race' && <RaceTab />}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  )
}
