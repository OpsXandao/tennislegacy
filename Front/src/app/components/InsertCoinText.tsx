import { motion } from 'motion/react';

interface InsertCoinTextProps {
  text?: string;
}

export function InsertCoinText({ text = 'INSERT COIN TO CONTINUE' }: InsertCoinTextProps) {
  return (
    <motion.div
      animate={{ opacity: [1, 0.3, 1] }}
      transition={{ duration: 2, repeat: Infinity }}
      className="arcade-font text-xs text-[#888] text-center"
    >
      {text}
    </motion.div>
  );
}
