import type { CapacitorConfig } from '@capacitor/cli'

const config: CapacitorConfig = {
  appId: 'com.tennislegacy.app',
  appName: 'Tennis Legacy',
  webDir: 'dist',
  server: {
    // Em desenvolvimento: aponta para a maquina host (10.0.2.2 = localhost no emulador Android)
    androidScheme: 'http',
    url: 'http://10.0.2.2:5173',
    cleartext: true,
  },
  android: {
    backgroundColor: '#0a0a0a',
  },
}

export default config
