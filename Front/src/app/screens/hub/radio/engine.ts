import type { HubRadioStation } from './stations'

function semitoneToFrequency(rootHz: number, semitone: number) {
  return rootHz * Math.pow(2, semitone / 12)
}

function createNoiseBuffer(ctx: AudioContext) {
  const buffer = ctx.createBuffer(1, ctx.sampleRate * 0.15, ctx.sampleRate)
  const data = buffer.getChannelData(0)
  for (let i = 0; i < data.length; i += 1) {
    data[i] = Math.random() * 2 - 1
  }
  return buffer
}

export class HubRadioEngine {
  private ctx: AudioContext | null = null
  private master: GainNode | null = null
  private timer: number | null = null
  private step = 0
  private station: HubRadioStation | null = null
  private volume = 0.45
  private noiseBuffer: AudioBuffer | null = null

  private ensureContext() {
    if (this.ctx && this.master) return
    const AudioCtor = window.AudioContext || (window as typeof window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext
    if (!AudioCtor) {
      throw new Error('Web Audio indisponível neste navegador.')
    }
    this.ctx = new AudioCtor()
    this.master = this.ctx.createGain()
    this.master.gain.value = this.volume
    this.master.connect(this.ctx.destination)
    this.noiseBuffer = createNoiseBuffer(this.ctx)
  }

  async start(station: HubRadioStation, volume?: number) {
    this.ensureContext()
    this.station = station
    this.step = 0
    if (typeof volume === 'number') {
      this.setVolume(volume)
    }
    if (!this.ctx || !this.master) return
    await this.ctx.resume()
    this.stopLoop()
    const intervalMs = ((60 / station.bpm) / 4) * 1000
    this.timer = window.setInterval(() => this.tick(), intervalMs)
    this.tick()
  }

  stop() {
    this.stopLoop()
    if (this.master && this.ctx) {
      this.master.gain.cancelScheduledValues(this.ctx.currentTime)
      this.master.gain.setTargetAtTime(0.0001, this.ctx.currentTime, 0.04)
    }
  }

  async resume() {
    if (!this.station) return
    await this.start(this.station, this.volume)
  }

  setVolume(volume: number) {
    this.volume = volume
    if (this.master && this.ctx) {
      this.master.gain.cancelScheduledValues(this.ctx.currentTime)
      this.master.gain.setTargetAtTime(volume, this.ctx.currentTime, 0.04)
    }
  }

  private stopLoop() {
    if (this.timer !== null) {
      window.clearInterval(this.timer)
      this.timer = null
    }
  }

  private tick() {
    if (!this.ctx || !this.master || !this.station || this.ctx.state !== 'running') {
      return
    }

    const step = this.step % 16
    const station = this.station
    const when = this.ctx.currentTime + 0.01

    if (station.kickPattern[step]) {
      this.playKick(when)
    }
    if (station.hatPattern[step]) {
      this.playHat(when)
    }

    const bass = station.bassPattern[step]
    if (typeof bass === 'number') {
      this.playTone(semitoneToFrequency(station.rootHz / 2, bass), when, 0.19, 'sawtooth', 0.12)
    }

    const lead = station.leadPattern[step]
    if (typeof lead === 'number') {
      this.playTone(semitoneToFrequency(station.rootHz, lead), when, 0.14, 'triangle', 0.08)
    }

    this.step += 1
  }

  private playTone(
    frequency: number,
    when: number,
    duration: number,
    type: OscillatorType,
    gainValue: number,
  ) {
    if (!this.ctx || !this.master) return
    const osc = this.ctx.createOscillator()
    const gain = this.ctx.createGain()
    const filter = this.ctx.createBiquadFilter()
    osc.type = type
    osc.frequency.setValueAtTime(frequency, when)
    filter.type = 'lowpass'
    filter.frequency.setValueAtTime(type === 'sawtooth' ? 900 : 1800, when)
    gain.gain.setValueAtTime(0.0001, when)
    gain.gain.exponentialRampToValueAtTime(gainValue, when + 0.02)
    gain.gain.exponentialRampToValueAtTime(0.0001, when + duration)
    osc.connect(filter)
    filter.connect(gain)
    gain.connect(this.master)
    osc.start(when)
    osc.stop(when + duration + 0.02)
  }

  private playKick(when: number) {
    if (!this.ctx || !this.master) return
    const osc = this.ctx.createOscillator()
    const gain = this.ctx.createGain()
    osc.type = 'sine'
    osc.frequency.setValueAtTime(140, when)
    osc.frequency.exponentialRampToValueAtTime(48, when + 0.16)
    gain.gain.setValueAtTime(0.22, when)
    gain.gain.exponentialRampToValueAtTime(0.0001, when + 0.16)
    osc.connect(gain)
    gain.connect(this.master)
    osc.start(when)
    osc.stop(when + 0.18)
  }

  private playHat(when: number) {
    if (!this.ctx || !this.master || !this.noiseBuffer) return
    const source = this.ctx.createBufferSource()
    const filter = this.ctx.createBiquadFilter()
    const gain = this.ctx.createGain()
    source.buffer = this.noiseBuffer
    filter.type = 'highpass'
    filter.frequency.setValueAtTime(5000, when)
    gain.gain.setValueAtTime(0.05, when)
    gain.gain.exponentialRampToValueAtTime(0.0001, when + 0.05)
    source.connect(filter)
    filter.connect(gain)
    gain.connect(this.master)
    source.start(when)
    source.stop(when + 0.06)
  }
}
