import { useEffect, useState } from 'react'

export function useTheme() {
  const [isLight, setIsLight] = useState(() =>
    typeof document !== 'undefined' && document.body.classList.contains('light-mode'),
  )

  useEffect(() => {
    const obs = new MutationObserver(() => {
      setIsLight(document.body.classList.contains('light-mode'))
    })
    obs.observe(document.body, { attributes: true, attributeFilter: ['class'] })
    return () => obs.disconnect()
  }, [])

  return { isLight }
}
