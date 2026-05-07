// Haptic feedback utilities for mobile devices

export function triggerHaptic(type: 'light' | 'medium' | 'heavy' = 'medium') {
  // Check if the Vibration API is available
  if ('vibrate' in navigator) {
    const patterns = {
      light: 10,
      medium: 20,
      heavy: 30
    };
    navigator.vibrate(patterns[type]);
  }
}

export function triggerSuccess() {
  if ('vibrate' in navigator) {
    navigator.vibrate([10, 50, 10]);
  }
}

export function triggerError() {
  if ('vibrate' in navigator) {
    navigator.vibrate([50, 30, 50]);
  }
}

// Arcade-style sound effect placeholders
export function playArcadeSound(sound: 'coin' | 'select' | 'back' | 'win' | 'lose') {
  // In a real implementation, this would play actual sound effects
  // For now, we'll use haptic feedback as a substitute
  
  const feedbackMap = {
    coin: () => triggerHaptic('light'),
    select: () => triggerHaptic('medium'),
    back: () => triggerHaptic('light'),
    win: () => triggerSuccess(),
    lose: () => triggerError()
  };

  feedbackMap[sound]?.();
}
