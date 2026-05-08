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
          ? 'border-[#00ff88] bg-[#00ff88]/10 text-[#00ff88]'
          : 'border-[#ff0055] bg-[#ff0055]/10 text-[#ff0055]'
      }`}
      style={{ fontFamily: 'var(--font-arcade)' }}
    >
      {mensagem.texto}
    </motion.div>
  )
}
