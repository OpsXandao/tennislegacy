import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Mail, Star, DollarSign, TrendingUp, X, Check } from 'lucide-react';

export default function StaffMarket() {
  const [selectedMessage, setSelectedMessage] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'market' | 'inbox'>('market');

  const coaches = [
    {
      name: 'CARLOS MOYA',
      specialty: 'CLAY SPECIALIST',
      rating: 5,
      cost: '$50K/mo',
      bonus: '+15% CLAY PERF',
      avatar: '🎾',
    },
    {
      name: 'BRAD GILBERT',
      specialty: 'MENTAL COACH',
      rating: 4,
      cost: '$35K/mo',
      bonus: '+10% MENTAL',
      avatar: '🧠',
    },
    {
      name: 'PATRICK M.',
      specialty: 'ALL-ROUNDER',
      rating: 5,
      cost: '$60K/mo',
      bonus: '+8% ALL STATS',
      avatar: '⭐',
    },
  ];

  const physios = [
    {
      name: 'DR. SMITH',
      specialty: 'RECOVERY PRO',
      rating: 4,
      cost: '$30K/mo',
      bonus: '-20% INJ. RISK',
      avatar: '💊',
    },
    {
      name: 'DR. MARTINEZ',
      specialty: 'ENDURANCE',
      rating: 5,
      cost: '$45K/mo',
      bonus: '+15% STAMINA',
      avatar: '💪',
    },
  ];

  const messages = [
    {
      from: 'ATP TOUR',
      subject: 'WILDCARD INVITATION',
      category: 'opportunity',
      date: '07/03/26',
      body: 'You have been offered a wildcard entry to the Madrid Masters 1000. This is a prestigious opportunity to compete against top-ranked players.',
      actions: true,
    },
    {
      from: 'NIKE SPORTS',
      subject: 'SPONSORSHIP DEAL',
      category: 'sponsor',
      date: '06/03/26',
      body: 'Nike is offering you a 3-year endorsement deal worth $500K annually. This includes equipment, apparel, and performance bonuses.',
      actions: true,
    },
    {
      from: 'FEDERATION',
      subject: 'DAVIS CUP CALL',
      category: 'team',
      date: '05/03/26',
      body: 'Your national team needs you for the upcoming Davis Cup tie. Represent your country in this historic competition.',
      actions: true,
    },
    {
      from: 'TOURNAMENT DESK',
      subject: 'SCHEDULE UPDATE',
      category: 'info',
      date: '04/03/26',
      body: 'Your match time has been changed to 18:00 local time. Please check in at least 2 hours before your scheduled match.',
      actions: false,
    },
  ];

  const categoryColors = {
    opportunity: '#ffe600',
    sponsor: '#00e5ff',
    team: '#00ff88',
    info: '#9ca3af',
  };

  return (
    <div className="min-h-screen bg-bg-main p-4 pt-6 font-mono pb-24">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-neon-pink text-[10px] tracking-[0.3em] mb-4"
            style={{ fontFamily: 'var(--font-arcade)', textShadow: 'var(--glow-pink)' }}>
          STAFF & INBOX
        </h1>

        {/* Tab Switcher */}
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('market')}
            className={`flex-1 py-2 text-[10px] border-2 transition-all ${
              activeTab === 'market'
                ? 'bg-neon-green text-black border-neon-green'
                : 'bg-black text-neon-green border-neon-green hover:bg-neon-green/20'
            }`}
            style={{ 
              fontFamily: 'var(--font-arcade)',
              boxShadow: activeTab === 'market' ? 'var(--glow-green)' : 'none',
            }}
          >
            MARKET
          </button>
          <button
            onClick={() => setActiveTab('inbox')}
            className={`flex-1 py-2 text-[10px] border-2 transition-all relative ${
              activeTab === 'inbox'
                ? 'bg-neon-pink text-black border-neon-pink'
                : 'bg-black text-neon-pink border-neon-pink hover:bg-neon-pink/20'
            }`}
            style={{ 
              fontFamily: 'var(--font-arcade)',
              boxShadow: activeTab === 'inbox' ? 'var(--glow-pink)' : 'none',
            }}
          >
            INBOX
            {messages.filter(m => m.actions).length > 0 && (
              <span className="absolute -top-2 -right-2 bg-neon-red text-white w-5 h-5 rounded-full text-[8px] flex items-center justify-center animate-pulse">
                {messages.filter(m => m.actions).length}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Market View */}
      {activeTab === 'market' && (
        <div className="space-y-6">
          {/* Coaches Section */}
          <div>
            <div className="bg-bg-card border-2 border-neon-green p-3 mb-3"
                 style={{ boxShadow: 'var(--glow-green)' }}>
              <h2 className="text-neon-green text-[10px] tracking-wider"
                  style={{ fontFamily: 'var(--font-arcade)' }}>
                COACHES AVAILABLE
              </h2>
            </div>

            <div className="space-y-3">
              {coaches.map((coach, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="bg-bg-card border-2 border-neon-green p-4"
                  style={{ boxShadow: '0 0 10px rgba(0, 255, 136, 0.2)' }}
                >
                  <div className="flex items-start gap-3">
                    {/* Avatar */}
                    <div className="w-16 h-16 bg-black border-2 border-neon-green flex items-center justify-center text-3xl"
                         style={{ boxShadow: 'var(--glow-green)' }}>
                      {coach.avatar}
                    </div>

                    {/* Info */}
                    <div className="flex-1">
                      <h3 className="text-neon-green text-[11px] mb-1"
                          style={{ fontFamily: 'var(--font-arcade)' }}>
                        {coach.name}
                      </h3>
                      <div className="text-[8px] text-neon-cyan mb-2">{coach.specialty}</div>

                      {/* Star Rating */}
                      <div className="flex gap-1 mb-2">
                        {[...Array(5)].map((_, starIdx) => (
                          <Star
                            key={starIdx}
                            size={10}
                            className={starIdx < coach.rating ? 'text-neon-gold' : 'text-muted-gray'}
                            fill={starIdx < coach.rating ? '#ffe600' : 'none'}
                          />
                        ))}
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <div className="flex items-center gap-1 text-neon-gold text-[10px] mb-1">
                            <TrendingUp size={10} />
                            <span>{coach.bonus}</span>
                          </div>
                          <div className="flex items-center gap-1 text-[9px] text-muted-gray">
                            <DollarSign size={10} />
                            <span>{coach.cost}</span>
                          </div>
                        </div>

                        <button className="bg-black border-2 border-neon-green text-neon-green px-4 py-2 text-[8px] hover:bg-neon-green hover:text-black transition-all"
                                style={{ fontFamily: 'var(--font-arcade)' }}>
                          HIRE
                        </button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Physios Section */}
          <div>
            <div className="bg-bg-card border-2 border-neon-cyan p-3 mb-3"
                 style={{ boxShadow: 'var(--glow-cyan)' }}>
              <h2 className="text-neon-cyan text-[10px] tracking-wider"
                  style={{ fontFamily: 'var(--font-arcade)' }}>
                PHYSIO SPECIALISTS
              </h2>
            </div>

            <div className="space-y-3">
              {physios.map((physio, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="bg-bg-card border-2 border-neon-cyan p-4"
                  style={{ boxShadow: '0 0 10px rgba(0, 229, 255, 0.2)' }}
                >
                  <div className="flex items-start gap-3">
                    {/* Avatar */}
                    <div className="w-16 h-16 bg-black border-2 border-neon-cyan flex items-center justify-center text-3xl"
                         style={{ boxShadow: 'var(--glow-cyan)' }}>
                      {physio.avatar}
                    </div>

                    {/* Info */}
                    <div className="flex-1">
                      <h3 className="text-neon-cyan text-[11px] mb-1"
                          style={{ fontFamily: 'var(--font-arcade)' }}>
                        {physio.name}
                      </h3>
                      <div className="text-[8px] text-neon-green mb-2">{physio.specialty}</div>

                      {/* Star Rating */}
                      <div className="flex gap-1 mb-2">
                        {[...Array(5)].map((_, starIdx) => (
                          <Star
                            key={starIdx}
                            size={10}
                            className={starIdx < physio.rating ? 'text-neon-gold' : 'text-muted-gray'}
                            fill={starIdx < physio.rating ? '#ffe600' : 'none'}
                          />
                        ))}
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <div className="flex items-center gap-1 text-neon-gold text-[10px] mb-1">
                            <TrendingUp size={10} />
                            <span>{physio.bonus}</span>
                          </div>
                          <div className="flex items-center gap-1 text-[9px] text-muted-gray">
                            <DollarSign size={10} />
                            <span>{physio.cost}</span>
                          </div>
                        </div>

                        <button className="bg-black border-2 border-neon-cyan text-neon-cyan px-4 py-2 text-[8px] hover:bg-neon-cyan hover:text-black transition-all"
                                style={{ fontFamily: 'var(--font-arcade)' }}>
                          HIRE
                        </button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Inbox View */}
      {activeTab === 'inbox' && (
        <div>
          {/* Message List */}
          <div className="space-y-3">
            {messages.map((message, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                onClick={() => setSelectedMessage(i)}
                className="bg-bg-card border-2 border-neon-pink p-4 cursor-pointer hover:bg-neon-pink/10 transition-all"
                style={{ 
                  boxShadow: message.actions 
                    ? '0 0 15px rgba(255, 0, 85, 0.4)' 
                    : '0 0 5px rgba(255, 0, 85, 0.2)',
                }}
              >
                <div className="flex items-start gap-3">
                  {/* Envelope Icon */}
                  <div 
                    className="w-12 h-12 border-2 flex items-center justify-center"
                    style={{ 
                      borderColor: categoryColors[message.category],
                      backgroundColor: `${categoryColors[message.category]}20`,
                    }}
                  >
                    <Mail 
                      size={20} 
                      style={{ color: categoryColors[message.category] }}
                    />
                  </div>

                  {/* Message Info */}
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-1">
                      <div>
                        <div className="text-[8px] text-muted-gray mb-1">{message.from}</div>
                        <h3 className="text-neon-pink text-[10px]"
                            style={{ fontFamily: 'var(--font-arcade)' }}>
                          {message.subject}
                        </h3>
                      </div>
                      <span className="text-[8px] text-neon-cyan">{message.date}</span>
                    </div>

                    {message.actions && (
                      <div className="mt-2 flex items-center gap-2">
                        <span className="text-[8px] text-neon-gold animate-pulse">
                          ● ACTION REQUIRED
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Category Badge */}
                  <div 
                    className="px-2 py-1 text-[7px] border"
                    style={{ 
                      borderColor: categoryColors[message.category],
                      color: categoryColors[message.category],
                    }}
                  >
                    {message.category.toUpperCase()}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Message Detail Modal */}
          <AnimatePresence>
            {selectedMessage !== null && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/95 z-50 flex items-center justify-center p-4"
                onClick={() => setSelectedMessage(null)}
              >
                <motion.div
                  initial={{ scale: 0.8, y: 50 }}
                  animate={{ scale: 1, y: 0 }}
                  exit={{ scale: 0.8, y: 50 }}
                  className="bg-bg-card border-4 border-neon-pink max-w-[360px] w-full relative crt-screen"
                  style={{ boxShadow: 'var(--glow-pink)' }}
                  onClick={(e) => e.stopPropagation()}
                >
                  {/* CRT Screen Effect */}
                  <div className="p-6 relative z-10">
                    {/* Close Button */}
                    <button
                      onClick={() => setSelectedMessage(null)}
                      className="absolute top-2 right-2 text-neon-pink hover:text-neon-red"
                    >
                      <X size={20} />
                    </button>

                    {/* Message Header */}
                    <div className="mb-4 pb-4 border-b-2 border-neon-pink">
                      <div className="text-[8px] text-muted-gray mb-2">
                        FROM: {messages[selectedMessage].from}
                      </div>
                      <h2 className="text-neon-pink text-[11px] mb-2"
                          style={{ fontFamily: 'var(--font-arcade)' }}>
                        {messages[selectedMessage].subject}
                      </h2>
                      <div className="text-[8px] text-neon-cyan">
                        DATE: {messages[selectedMessage].date}
                      </div>
                    </div>

                    {/* Message Body */}
                    <div className="mb-6 text-[10px] text-neon-green leading-relaxed bg-black p-3 border border-neon-green"
                         style={{ fontFamily: 'Share Tech Mono' }}>
                      {messages[selectedMessage].body}
                    </div>

                    {/* Action Buttons */}
                    {messages[selectedMessage].actions && (
                      <div className="flex gap-3">
                        <button
                          onClick={() => setSelectedMessage(null)}
                          className="flex-1 bg-neon-green text-black py-3 text-[10px] border-2 border-neon-green hover:bg-black hover:text-neon-green transition-all flex items-center justify-center gap-2"
                          style={{ fontFamily: 'var(--font-arcade)' }}
                        >
                          <Check size={14} />
                          ACCEPT
                        </button>
                        <button
                          onClick={() => setSelectedMessage(null)}
                          className="flex-1 bg-black text-neon-red py-3 text-[10px] border-2 border-neon-red hover:bg-neon-red hover:text-black transition-all flex items-center justify-center gap-2"
                          style={{ fontFamily: 'var(--font-arcade)' }}
                        >
                          <X size={14} />
                          DECLINE
                        </button>
                      </div>
                    )}

                    {!messages[selectedMessage].actions && (
                      <button
                        onClick={() => setSelectedMessage(null)}
                        className="w-full bg-neon-cyan text-black py-3 text-[10px] border-2 border-neon-cyan hover:bg-black hover:text-neon-cyan transition-all"
                        style={{ fontFamily: 'var(--font-arcade)' }}
                      >
                        CLOSE
                      </button>
                    )}
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
