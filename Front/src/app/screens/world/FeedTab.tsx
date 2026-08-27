import { useEffect, useState } from 'react'
import { motion } from 'motion/react'
import { Heart, MessageCircle, Share2, MoreHorizontal } from 'lucide-react'
import { api } from '../../../api/client'

interface Post {
  id: string
  user: {
    name: string
    handle: string
    avatar: string
    verified: boolean
  }
  content: string
  likes: number
  comments: number
  time: string
  liked?: boolean
}

const PERSONAS = [
  { name: 'ATP Media', handle: '@atptour', avatar: '🎾', verified: true },
  { name: 'Tennis Insider', handle: '@tennis_insider', avatar: '🕵️', verified: true },
  { name: 'Sponsor World', handle: '@sponsor_global', avatar: '💰', verified: false },
  { name: 'Fan Zone', handle: '@tennis_fan_1', avatar: '🧢', verified: false },
  { name: 'WTA Official', handle: '@wta', avatar: '🚺', verified: true },
]

export function FeedTab() {
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState(false)

  useEffect(() => {
    api.mundo.noticias()
      .then(res => {
        const newsPosts: Post[] = res.noticias.map((n, i) => {
          const persona = PERSONAS[i % PERSONAS.length]
          return {
            id: `post-${i}`,
            user: persona,
            content: n,
            likes: Math.floor(Math.random() * 500) + 50,
            comments: Math.floor(Math.random() * 50) + 5,
            time: `${i + 1}h ago`,
            liked: false
          }
        })
        setPosts(newsPosts)
      })
      .catch(() => setErro(true))
      .finally(() => setLoading(false))
  }, [])

  const toggleLike = (id: string) => {
    setPosts(prev => prev.map(p => {
      if (p.id === id) {
        return { ...p, liked: !p.liked, likes: p.liked ? p.likes - 1 : p.likes + 1 }
      }
      return p
    }))
  }

  if (loading) {
    return (
      <div className="py-16 text-center pixel-font text-[10px] text-neon-yellow animate-pulse">
        SINCRONIZANDO TENNIS-GRAM...
      </div>
    )
  }

  if (erro) {
    return (
      <div className="py-16 text-center pixel-font text-[10px] text-neon-pink">
        Erro ao carregar feed
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {posts.map((post, i) => (
        <motion.div
          key={post.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
          className="border border-white/10 bg-[#111] overflow-hidden"
        >
          {/* Header */}
          <div className="p-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-[#222] flex items-center justify-center text-lg rounded-full border border-white/5">
                {post.user.avatar}
              </div>
              <div>
                <div className="flex items-center gap-1">
                  <span className="arcade-font text-[10px] text-white">{post.user.name}</span>
                  {post.user.verified && <span className="text-neon-cyan text-[8px]">✓</span>}
                </div>
                <div className="arcade-font text-[8px] text-[#666]">{post.user.handle}</div>
              </div>
            </div>
            <button className="text-[#444]">
              <MoreHorizontal size={16} />
            </button>
          </div>

          {/* Content */}
          <div className="px-3 pb-4 pt-1">
            <p className="arcade-font text-[10px] text-[#ddd] leading-relaxed">
              {post.content}
            </p>
          </div>

          {/* Engagement */}
          <div className="p-3 border-t border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button 
                onClick={() => toggleLike(post.id)}
                className={`flex items-center gap-1.5 transition-colors ${post.liked ? 'text-neon-pink' : 'text-[#888]'}`}
              >
                <Heart size={14} fill={post.liked ? 'currentColor' : 'none'} />
                <span className="arcade-font text-[8px]">{post.likes}</span>
              </button>
              <button className="flex items-center gap-1.5 text-[#888]">
                <MessageCircle size={14} />
                <span className="arcade-font text-[8px]">{post.comments}</span>
              </button>
              <button className="text-[#888]">
                <Share2 size={14} />
              </button>
            </div>
            <div className="arcade-font text-[8px] text-[#444]">
              {post.time}
            </div>
          </div>
        </motion.div>
      ))}

      {posts.length === 0 && (
        <div className="py-12 text-center arcade-font text-[10px] text-[#444]">
          SEM ATIVIDADE RECENTE NO FEED
        </div>
      )}
    </div>
  )
}
