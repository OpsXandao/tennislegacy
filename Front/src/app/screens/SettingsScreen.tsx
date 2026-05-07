import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';
import { Volume2, VolumeX, Vibrate, Sun, Moon, Monitor } from 'lucide-react';
import { NeonCard, NeonButton, PageHeader } from '../components';

type ThemeMode = 'system' | 'light' | 'dark'

type SettingsState = {
  sound: boolean
  music: boolean
  vibration: boolean
  scanlines: boolean
  themeMode: ThemeMode
  difficulty: 'easy' | 'medium' | 'hard'
}

const SETTINGS_KEY = 'tennislegacy.settings'

const DEFAULT_SETTINGS: SettingsState = {
  sound: true,
  music: true,
  vibration: true,
  scanlines: true,
  themeMode: 'system',
  difficulty: 'medium',
}

function normalizeSettings(rawSettings: Partial<SettingsState> & { lightMode?: boolean }): SettingsState {
  const themeMode = rawSettings.themeMode ?? (rawSettings.lightMode ? 'light' : 'system')
  return {
    ...DEFAULT_SETTINGS,
    ...rawSettings,
    themeMode,
  }
}

function resolveThemeMode(themeMode: ThemeMode) {
  if (themeMode !== 'system') return themeMode
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function applySettings(settings: SettingsState) {
  const effectiveTheme = resolveThemeMode(settings.themeMode)
  document.body.classList.toggle('scanlines-off', !settings.scanlines)
  document.body.classList.toggle('light-mode', effectiveTheme === 'light')
  document.body.classList.toggle('dark-mode', effectiveTheme === 'dark')
  document.body.dataset.themeMode = settings.themeMode
  document.body.dataset.themeResolved = effectiveTheme
  document.documentElement.style.colorScheme = effectiveTheme
}

export function SettingsScreen() {
  const navigate = useNavigate();
  const [settings, setSettings] = useState<SettingsState>(DEFAULT_SETTINGS);
  const [saved, setSaved] = useState('')

  useEffect(() => {
    const raw = window.localStorage.getItem(SETTINGS_KEY)
    if (!raw) {
      applySettings(DEFAULT_SETTINGS)
      return
    }
    try {
      const parsed = normalizeSettings(JSON.parse(raw))
      setSettings(parsed)
      applySettings(parsed)
    } catch {
      applySettings(DEFAULT_SETTINGS)
    }
  }, [])

  useEffect(() => {
    applySettings(settings)
    window.localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings))
  }, [settings])

  useEffect(() => {
    if (settings.themeMode !== 'system') return

    const media = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = () => applySettings(settings)
    media.addEventListener('change', handleChange)
    return () => media.removeEventListener('change', handleChange)
  }, [settings])

  const toggleSetting = (key: keyof Omit<SettingsState, 'difficulty' | 'themeMode'>) => {
    setSettings(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
    setSaved('')
  };

  function handleSaveAndBack() {
    window.localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings))
    setSaved('CONFIGURAÇÕES SALVAS LOCALMENTE')
    window.setTimeout(() => navigate('/hub'), 250)
  }

  return (
    <div className="app-shell min-h-screen">
      <PageHeader title="CONFIG" subtitle="PERSISTÊNCIA LOCAL NO CLIENTE" color="green" backTo="/hub" />

      <div className="p-4 space-y-4">
        <NeonCard variant="cyan" hover={false}>
          <div className="arcade-font text-xs text-[#00e5ff] mb-4">
            ÁUDIO
          </div>
          <div className="space-y-3">
            <button
              onClick={() => toggleSetting('sound')}
              className="w-full flex items-center justify-between p-3 bg-black/50 border border-[#00e5ff]/30 hover:bg-[#00e5ff]/10 transition-colors"
            >
              <div className="flex items-center gap-3">
                {settings.sound ? <Volume2 size={20} /> : <VolumeX size={20} />}
                <span className="arcade-font text-sm">SFX</span>
              </div>
              <Toggle on={settings.sound} color="#00e5ff" />
            </button>

            <button
              onClick={() => toggleSetting('music')}
              className="w-full flex items-center justify-between p-3 bg-black/50 border border-[#00e5ff]/30 hover:bg-[#00e5ff]/10 transition-colors"
            >
              <div className="flex items-center gap-3">
                {settings.music ? <Volume2 size={20} /> : <VolumeX size={20} />}
                <span className="arcade-font text-sm">MÚSICA</span>
              </div>
              <Toggle on={settings.music} color="#00e5ff" />
            </button>

            <button
              onClick={() => toggleSetting('vibration')}
              className="w-full flex items-center justify-between p-3 bg-black/50 border border-[#00e5ff]/30 hover:bg-[#00e5ff]/10 transition-colors"
            >
              <div className="flex items-center gap-3">
                <Vibrate size={20} />
                <span className="arcade-font text-sm">VIBRAÇÃO</span>
              </div>
              <Toggle on={settings.vibration} color="#00e5ff" />
            </button>
          </div>
        </NeonCard>

        <NeonCard variant="pink" hover={false}>
          <div className="arcade-font text-xs text-[#ff0055] mb-4">
            VISUAL
          </div>
          <div className="space-y-3">
            <button
              onClick={() => toggleSetting('scanlines')}
              className="w-full flex items-center justify-between p-3 bg-black/50 border border-[#ff0055]/30 hover:bg-[#ff0055]/10 transition-colors"
            >
              <span className="arcade-font text-sm">SCANLINES</span>
              <Toggle on={settings.scanlines} color="#ff0055" />
            </button>
            <div className="border border-[#ff0055]/30 bg-black/40 p-3">
              <div className="mb-3 flex items-center gap-3">
                {settings.themeMode === 'system' ? <Monitor size={20} /> : settings.themeMode === 'light' ? <Sun size={20} /> : <Moon size={20} />}
                <span className="arcade-font text-sm">TEMA</span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                {([
                  { value: 'system', label: 'SISTEMA', icon: <Monitor size={16} /> },
                  { value: 'light', label: 'CLARO', icon: <Sun size={16} /> },
                  { value: 'dark', label: 'ESCURO', icon: <Moon size={16} /> },
                ] as const).map((option) => (
                  <button
                    key={option.value}
                    onClick={() => {
                      setSettings(prev => ({ ...prev, themeMode: option.value }))
                      setSaved('')
                    }}
                    className={`
                      flex min-h-[52px] items-center justify-center gap-2 border px-2 py-3 transition-all
                      ${settings.themeMode === option.value
                        ? 'bg-[#ff0055] text-black border-[#ff0055] shadow-[var(--glow-pink-sm)]'
                        : 'bg-transparent text-white border-[#ff0055]/30 hover:bg-[#ff0055]/10'
                      }
                    `}
                  >
                    {option.icon}
                    <span className="arcade-font text-[10px]">{option.label}</span>
                  </button>
                ))}
              </div>
              <div className="mt-3 arcade-font text-[10px] text-[#888]">
                ATIVO: {settings.themeMode === 'system' ? `SISTEMA (${resolveThemeMode(settings.themeMode).toUpperCase()})` : settings.themeMode.toUpperCase()}
              </div>
            </div>
          </div>
        </NeonCard>

        <NeonCard variant="yellow" hover={false}>
          <div className="arcade-font text-xs text-[#ffe600] mb-4">
            DIFICULDADE
          </div>
          <div className="grid grid-cols-3 gap-2">
            {(['easy', 'medium', 'hard'] as const).map((level) => (
              <button
                key={level}
                onClick={() => {
                  setSettings(prev => ({ ...prev, difficulty: level }))
                  setSaved('')
                }}
                className={`
                  p-3 border-2 arcade-font text-xs uppercase transition-all
                  ${settings.difficulty === level
                    ? 'bg-[#ffe600] text-black border-[#ffe600]'
                    : 'bg-transparent text-white border-[#ffe600]/30'
                  }
                `}
              >
                {level}
              </button>
            ))}
          </div>
        </NeonCard>

        <NeonCard variant="green" hover={false}>
          <div className="arcade-font text-xs text-[#00ff88] mb-4">
            SOBRE
          </div>
          <div className="space-y-2 text-sm arcade-font text-[#888]">
            <div className="flex justify-between">
              <span>VERSÃO:</span>
              <span className="text-[#00ff88]">1.0.0</span>
            </div>
            <div className="flex justify-between">
              <span>BUILD:</span>
              <span className="text-[#00ff88]">2026.03</span>
            </div>
            <div className="flex justify-between">
              <span>CONFIG BACKEND:</span>
              <span className="text-[#ffe600]">NÃO EXPOSO</span>
            </div>
          </div>
        </NeonCard>

        {saved && <div className="arcade-font text-[10px] text-center text-[#00ff88]">{saved}</div>}

        <div className="space-y-3 pt-4">
          <NeonButton variant="green" className="w-full" onClick={handleSaveAndBack}>
            SALVAR E VOLTAR
          </NeonButton>
          <NeonButton
            variant="pink"
            className="w-full"
            onClick={() => {
              setSettings(DEFAULT_SETTINGS)
              setSaved('CONFIGURAÇÕES RESETADAS')
            }}
          >
            RESETAR CONFIG
          </NeonButton>
        </div>
      </div>
    </div>
  );
}

function Toggle({ on, color = '#00ff88' }: { on: boolean; color?: string }) {
  return (
    <div
      className="relative h-6 w-12 border-2 transition-colors"
      style={{ borderColor: on ? color : '#333' }}
    >
      <div
        className="absolute top-0 h-full w-1/2 transition-all"
        style={{ left: on ? '50%' : '0', background: on ? color : '#333' }}
      />
    </div>
  )
}
