import { motion } from 'motion/react'
import { X, Share2, Printer } from 'lucide-react'
import imprensaData from '../../data/imprensa.json'

interface Props {
  headline: string
  subheadline: string
  category?: string
  date?: string
  torneio?: string
  tipoTorneio?: string
  nacionalidadeJogador?: string | null
  onClose: () => void
}
type PressCountry = { outlets?: string[]; jornalistas?: string[] }

function stableIndex(seed: string, length: number) {
  if (length <= 0) return 0
  let hash = 0
  for (let i = 0; i < seed.length; i += 1) hash = (hash * 31 + seed.charCodeAt(i)) >>> 0
  return hash % length
}

function extrairCodigoPais(nacionalidade?: string | null) {
  const match = String(nacionalidade || "").match(/\[([A-Z]{2,3})\]/)
  return match?.[1] || String(nacionalidade || "").slice(0, 3).toUpperCase() || ""
}

function paisDoGrandSlam(torneio?: string, tipoTorneio?: string) {
  const nome = String(torneio || "").toLowerCase()
  const isGrandSlam = String(tipoTorneio || "").toLowerCase().includes("grand slam")
    || /australian|roland|wimbledon|us open/.test(nome)
  if (!isGrandSlam) return ""
  if (nome.includes("australian")) return "AU"
  if (nome.includes("roland")) return "FR"
  if (nome.includes("wimbledon")) return "GB"
  if (nome.includes("us open")) return "US"
  return ""
}

function escolherFonte(torneio?: string, tipoTorneio?: string, nacionalidadeJogador?: string | null) {
  const porPais = (imprensaData as { porPais?: Record<string, PressCountry> }).porPais || {}
  const codigo = paisDoGrandSlam(torneio, tipoTorneio) || extrairCodigoPais(nacionalidadeJogador) || "BR"
  const fonte = porPais[codigo] || porPais.BR || {}
  const seed = [torneio || "tour", nacionalidadeJogador || ""].join(":")
  const outlets = fonte.outlets || imprensaData.outlets || ["The Legacy Post"]
  const jornalistas = fonte.jornalistas || imprensaData.jornalistas || ["Redação"]
  return {
    outlet: outlets[stableIndex(seed, outlets.length)],
    jornalista: jornalistas[stableIndex(seed + ":byline", jornalistas.length)],
    codigo,
  }
}

export function NewspaperModal({
  headline,
  subheadline,
  category = "BREAKING NEWS",
  date,
  torneio,
  tipoTorneio,
  nacionalidadeJogador,
  onClose,
}: Props) {
  const currentDate = date || new Date().toLocaleDateString("pt-BR", { day: "2-digit", month: "long", year: "numeric" })
  const fonte = escolherFonte(torneio, tipoTorneio, nacionalidadeJogador)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4 backdrop-blur-md">
      <motion.div
        initial={{ scale: 0.8, rotate: -5, opacity: 0 }}
        animate={{ scale: 1, rotate: 0, opacity: 1 }}
        exit={{ scale: 1.1, rotate: 5, opacity: 0 }}
        className="w-full max-w-xl bg-[#e6e2d3] p-8 shadow-[20px_20px_0_rgba(0,0,0,0.5)] border-4 border-[#333] relative overflow-hidden"
      >
        {/* Newspaper Texture Decor */}
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none mix-blend-multiply bg-[url('https://www.transparenttextures.com/patterns/paper-fibers.png')]" />

        {/* Header */}
        <div className="border-b-4 border-[#333] pb-4 mb-6 text-center">
          <div className="flex justify-between items-center mb-2 arcade-font text-[9px] text-[#555]">
            <span>VOL. LXXXIV ... No. 29,482</span>
            <span className="font-bold text-[#111]">{currentDate.toUpperCase()}</span>
            <span>PRICE: $2.50</span>
          </div>
          <h2 className="pixel-font text-3xl text-[#111] tracking-tighter">{fonte.outlet.toUpperCase()}</h2>
        </div>

        {/* Category Badge */}
        <div className="inline-block bg-[#111] text-white px-3 py-1 arcade-font text-[8px] mb-4">
          {category.toUpperCase()}
        </div>

        {/* Main Content */}
        <div className="space-y-4">
          <h1 className="pixel-font text-4xl leading-none text-[#111] uppercase break-words">
            {headline}
          </h1>
          
          <div className="h-1 bg-[#333] w-full" />

          <p className="arcade-font text-sm text-[#333] leading-relaxed italic border-l-4 border-[#333] pl-4">
            "{subheadline}"
          </p>

          <div className="grid grid-cols-2 gap-4 pt-4 border-t border-[#333]/20">
            <div className="arcade-font text-[10px] text-[#555] leading-snug">
              Por {fonte.jornalista}. A cobertura vem de {fonte.codigo}, onde a final ganhou tratamento de manchete. Analistas já discutem o impacto deste título no circuito.
            </div>
            <div className="bg-[#dcd8c8] border-2 border-[#333]/10 p-3 flex flex-col justify-center items-center gap-2">
              <div className="w-12 h-12 border-2 border-[#333] flex items-center justify-center text-2xl">
                🏆
              </div>
              <div className="arcade-font text-[8px] text-[#111] text-center">WORLD TOUR EXCLUSIVE</div>
            </div>
          </div>
        </div>

        {/* Footer / Actions */}
        <div className="mt-10 flex justify-between items-center">
          <div className="flex gap-4">
            <button className="text-[#555] hover:text-[#111] transition-colors"><Share2 size={20} /></button>
            <button className="text-[#555] hover:text-[#111] transition-colors"><Printer size={20} /></button>
          </div>
          <button
            onClick={onClose}
            className="px-6 py-2 bg-[#111] text-white arcade-font text-[10px] hover:bg-neon-pink transition-colors"
          >
            [ CLOSE PAPER ]
          </button>
        </div>

        {/* Close Icon (Top Right) */}
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 text-[#333] hover:scale-110 transition-transform"
        >
          <X size={24} />
        </button>
      </motion.div>
    </div>
  )
}
