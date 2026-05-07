import { motion, AnimatePresence } from 'motion/react';
import { useEffect, useState } from 'react';

interface ArcadeNotificationProps {
  message: string;
  type?: 'success' | 'error' | 'info' | 'warning';
  duration?: number;
  onClose?: () => void;
}

export function ArcadeNotification({
  message,
  type = 'info',
  duration = 3000,
  onClose
}: ArcadeNotificationProps) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      onClose?.();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const typeStyles = {
    success: {
      border: '#00ff88',
      bg: '#1a1a2e',
      icon: '✓',
      glow: 'shadow-[0_0_20px_#00ff88]'
    },
    error: {
      border: '#ff0055',
      bg: '#1a1a2e',
      icon: '✗',
      glow: 'shadow-[0_0_20px_#ff0055]'
    },
    info: {
      border: '#00e5ff',
      bg: '#1a1a2e',
      icon: 'i',
      glow: 'shadow-[0_0_20px_#00e5ff]'
    },
    warning: {
      border: '#ffe600',
      bg: '#1a1a2e',
      icon: '!',
      glow: 'shadow-[0_0_20px_#ffe600]'
    }
  };

  const style = typeStyles[type];

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -50 }}
          className={`
            fixed top-4 left-4 right-4 z-50
            border-2 p-4 ${style.glow}
          `}
          style={{
            borderColor: style.border,
            backgroundColor: style.bg
          }}
        >
          <div className="flex items-center gap-3">
            <div
              className="pixel-font text-2xl"
              style={{ color: style.border }}
            >
              {style.icon}
            </div>
            <div
              className="arcade-font text-sm flex-1"
              style={{ color: style.border }}
            >
              {message}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
