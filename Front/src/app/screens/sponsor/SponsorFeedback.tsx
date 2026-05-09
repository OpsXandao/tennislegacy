import { motion } from 'motion/react'

interface SponsorFeedbackProps {
  mensagem: { texto: string; ok: boolean } | null
}

export function SponsorFeedback({ mensagem }: SponsorFeedbackProps) {
  if (!mensagem) {
    return null
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      className={`border-2 p-3 text-center text-[10px] ${
        mensagem.ok
          ? 'border-neon-green bg-neon-green/10 text-neon-green'
          : 'border-neon-pink bg-neon-pink/10 text-neon-pink'
      }`}
      style={{ fontFamily: 'var(--font-arcade)' }}
    >
      {mensagem.texto}
    </motion.div>
  )
}
