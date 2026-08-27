import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'

interface DramaSignal {
  label: string
  sublabel?: string
  color: string
}

interface Props {
  pontoCritico: { label: string; color: string } | null
  isTiebreak: boolean
  isComeback: boolean
  crowdRoar?: boolean
}

export function MatchDramaOverlay({ pontoCritico, isTiebreak, isComeback, crowdRoar }: Props) {
  const [signal, setSignal] = useState<DramaSignal | null>(null)
  const timerRef = useRef<number | null>(null)
  const lastKeyRef = useRef<string | null>(null)

  useEffect(() => {
    let newSignal: DramaSignal | null = null
    let key: string | null = null

    if (pontoCritico) {
      key = pontoCritico.label
      newSignal = { label: pontoCritico.label, color: pontoCritico.color }
    } else if (isTiebreak) {
      key = 'TIEBREAK'
      newSignal = { label: 'TIEBREAK', sublabel: '6 × 6', color: 'var(--neon-yellow)' }
    } else if (isComeback) {
      key = 'COMEBACK'
      newSignal = { label: 'COMEBACK!', sublabel: 'você virou o set', color: 'var(--neon-green)' }
    } else if (crowdRoar) {
      key = 'CROWD'
      newSignal = { label: 'CROWD ROARS!', sublabel: 'CLAP CLAP CLAP', color: 'var(--neon-gold)' }
    }

    if (key && key !== lastKeyRef.current) {
      lastKeyRef.current = key
      setSignal(newSignal)
      if (timerRef.current) window.clearTimeout(timerRef.current)
      timerRef.current = window.setTimeout(() => setSignal(null), 1800)
    }
    if (!key) lastKeyRef.current = null
  }, [pontoCritico, isTiebreak, isComeback])

  useEffect(() => () => { if (timerRef.current) window.clearTimeout(timerRef.current) }, [])

  return (
    <AnimatePresence>
      {signal && (
        <motion.div
          key={signal.label}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.18 }}
          className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none"
          style={{ background: `radial-gradient(ellipse at center, ${signal.color}1a 0%, transparent 65%)` }}
        >
          <motion.div
            initial={{ scale: 1.3, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            transition={{ duration: 0.22, ease: 'easeOut' }}
            className="text-center px-8"
          >
            <div
              className="pixel-font tracking-wider"
              style={{
                fontSize: 'clamp(1.4rem, 6vw, 2.2rem)',
                color: signal.color,
                textShadow: `0 0 10px ${signal.color}, 0 0 22px ${signal.color}66`,
              }}
            >
              {signal.label}
            </div>
            {signal.sublabel && (
              <div
                className="arcade-font text-[10px] mt-2 tracking-widest uppercase"
                style={{ color: signal.color, opacity: 0.7 }}
              >
                {signal.sublabel}
              </div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
