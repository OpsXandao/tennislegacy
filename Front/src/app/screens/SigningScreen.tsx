import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { useNavigate } from 'react-router'
import { PenTool as Pen, FileText, CheckCircle2, Star } from 'lucide-react'
import { useGameStore } from '../../store/gameStore'
import { TronGrid } from '../components/TronGrid'
import { NeonButton } from '../components/NeonButton'

export function SigningScreen() {
  const navigate = useNavigate()
  const { jogador } = useGameStore()
  const [step, setStep] = useState(0) // 0: Reveal, 1: Ready to Sign, 2: Signed
  const signTimeoutRef = useRef<number | null>(null)

  useEffect(() => {
    if (!jogador) {
      navigate('/')
      return
    }
    const t = setTimeout(() => setStep(1), 2000)
    return () => clearTimeout(t)
  }, [jogador, navigate])

  useEffect(() => () => { if (signTimeoutRef.current) clearTimeout(signTimeoutRef.current) }, [])

  const handleSign = () => {
    setStep(2)
    signTimeoutRef.current = window.setTimeout(() => {
      navigate('/hub')
    }, 3000)
  }

  if (!jogador) return null

  return (
    <div className="app-shell min-h-screen flex flex-col items-center justify-center p-6 relative overflow-hidden bg-[#050505]">
      <TronGrid />

      <AnimatePresence mode="wait">
        {step < 2 ? (
          <motion.div
            key="contract"
            initial={{ y: 100, opacity: 0, scale: 0.9 }}
            animate={{ y: 0, opacity: 1, scale: 1 }}
            exit={{ y: -100, opacity: 0 }}
            className="w-full max-w-lg bg-[#f0f0f0] text-[#111] p-8 shadow-[0_0_50px_rgba(255,255,255,0.1)] relative border-t-8 border-neon-green"
          >
            {/* Stamp/Seal Decor */}
            <div className="absolute top-4 right-4 opacity-10">
              <FileText size={80} />
            </div>

            <div className="text-center mb-8">
              <div className="arcade-font text-[10px] text-[#888] tracking-[0.3em] mb-2">OFFICIAL DOCUMENT</div>
              <h1 className="pixel-font text-xl border-b-2 border-[#ddd] pb-4">PROFESSIONAL TOUR CONTRACT</h1>
            </div>

            <div className="space-y-6 arcade-font text-[11px] leading-relaxed">
              <p>
                Este documento formaliza a entrada de <span className="text-neon-green font-bold">{jogador.nome.toUpperCase()}</span> no circuito profissional de tênis.
              </p>
              
              <div className="grid grid-cols-2 gap-4 bg-[#e8e8e8] p-4 border border-[#ddd]">
                <div>
                  <div className="text-[8px] text-[#888]">ATLETA</div>
                  <div>{jogador.nome}</div>
                </div>
                <div>
                  <div className="text-[8px] text-[#888]">NACIONALIDADE</div>
                  <div>{jogador.nacionalidade}</div>
                </div>
                <div>
                  <div className="text-[8px] text-[#888]">IDADE</div>
                  <div>{jogador.idade} ANOS</div>
                </div>
                <div>
                  <div className="text-[8px] text-[#888]">CATEGORIA</div>
                  <div>PRO DEBUT</div>
                </div>
              </div>

              <p className="italic text-[#666]">
                "Ao assinar, o atleta compromete-se a seguir os regulamentos do tour mundial, 
                zelar pela integridade do esporte e buscar a excelência em cada partida."
              </p>
            </div>

            <div className="mt-12 flex flex-col items-center">
              {step === 1 && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="w-full"
                >
                  <button
                    onClick={handleSign}
                    className="w-full group relative flex items-center justify-center gap-3 py-4 bg-[#111] text-white border-2 border-[#111] hover:bg-white hover:text-[#111] transition-all overflow-hidden"
                  >
                    <Pen size={18} className="group-hover:rotate-12 transition-transform" />
                    <span className="arcade-font text-xs">ASSINAR CONTRATO</span>
                    <div className="absolute inset-0 bg-neon-green/10 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                </motion.div>
              )}
            </div>

            <div className="mt-8 flex justify-between items-end opacity-40">
              <div className="text-[8px] arcade-font">
                REF: TL-2026-XPR
              </div>
              <div className="text-[14px] pixel-font">
                LEGACY TOUR
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="success"
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="text-center space-y-6 relative z-10"
          >
            <motion.div
              animate={{ rotate: [0, 10, -10, 0], scale: [1, 1.1, 1] }}
              transition={{ duration: 0.5, repeat: Infinity, repeatDelay: 1 }}
              className="w-24 h-24 bg-neon-green text-black flex items-center justify-center rounded-full mx-auto shadow-[0_0_30px_#00ff88]"
            >
              <CheckCircle2 size={48} />
            </motion.div>
            <h2 className="pixel-font text-2xl text-white">CONTRATO ASSINADO!</h2>
            <div className="flex justify-center gap-2">
              <Star className="text-neon-yellow fill-neon-yellow" size={16} />
              <div className="arcade-font text-xs text-neon-cyan tracking-widest">VOCÊ AGORA É UM PROFISSIONAL</div>
              <Star className="text-neon-yellow fill-neon-yellow" size={16} />
            </div>
            <div className="arcade-font text-[10px] text-[#555] animate-pulse">REDIRECIONANDO PARA O HUB...</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
