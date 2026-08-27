import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { Newspaper } from 'lucide-react'
import { api } from '../../api/client'

export function NewsTicker() {
  const [noticias, setNoticias] = useState<string[]>([])
  const [index, setIndex] = useState(0)

  useEffect(() => {
    api.mundo.noticias()
      .then(res => {
        const textos = res.feed?.length ? res.feed.map(item => item.texto || item.titulo) : res.noticias
        if (textos.length > 0) {
          setNoticias(textos)
        } else {
          setNoticias(["BEM-VINDO AO TENNIS LEGACY - O CIRCUITO MUNDIAL ESTÁ COMEÇANDO!"])
        }
      })
      .catch(() => setNoticias(["CONECTANDO AO SERVIDOR DE NOTÍCIAS..."]))
  }, [])

  useEffect(() => {
    if (noticias.length <= 1) return
    const interval = setInterval(() => {
      setIndex(prev => (prev + 1) % noticias.length)
    }, 6000)
    return () => clearInterval(interval)
  }, [noticias])

  return (
    <div className="bg-black border-y-2 border-neon-green/30 py-1 overflow-hidden relative flex items-center h-8">
      <div className="absolute left-0 top-0 bottom-0 bg-black z-10 px-2 flex items-center border-r border-neon-green/30">
        <Newspaper size={14} className="text-neon-green" />
        <span className="arcade-font text-[8px] text-neon-green ml-1">NEWS</span>
      </div>
      
      <div className="flex-1 ml-16">
        <AnimatePresence mode="wait">
          <motion.div
            key={index}
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -20, opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="arcade-font text-[9px] text-neon-yellow whitespace-nowrap"
          >
            {noticias[index]}
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-black to-transparent z-10" />
    </div>
  )
}
