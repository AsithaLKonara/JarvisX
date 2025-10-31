/**
 * Lip-Sync Utility
 * Analyzes audio and generates mouth movement data for avatar
 */

export class LipSyncAnalyzer {
  constructor() {
    this.audioContext = null
    this.analyser = null
    this.dataArray = null
    this.animationFrame = null
    this.onUpdate = null
  }
  
  /**
   * Initialize Web Audio API
   */
  async init() {
    try {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)()
      this.analyser = this.audioContext.createAnalyser()
      this.analyser.fftSize = 256
      
      const bufferLength = this.analyser.frequencyBinCount
      this.dataArray = new Uint8Array(bufferLength)
      
      return true
    } catch (error) {
      console.error('Failed to initialize audio context:', error)
      return false
    }
  }
  
  /**
   * Analyze audio from a URL or blob
   * @param {string|Blob} audioSource - Audio URL or blob
   * @param {Function} onUpdate - Callback for amplitude updates
   */
  async analyze(audioSource, onUpdate) {
    if (!this.audioContext) {
      const initialized = await this.init()
      if (!initialized) return
    }
    
    this.onUpdate = onUpdate
    
    try {
      // Create audio element
      const audio = new Audio()
      
      if (typeof audioSource === 'string') {
        audio.src = audioSource
      } else {
        audio.src = URL.createObjectURL(audioSource)
      }
      
      // Create source node
      const source = this.audioContext.createMediaElementSource(audio)
      source.connect(this.analyser)
      this.analyser.connect(this.audioContext.destination)
      
      // Start playing
      await audio.play()
      
      // Start analyzing
      this.startAnalysis()
      
      // Cleanup when audio ends
      audio.onended = () => {
        this.stop()
        if (onUpdate) {
          onUpdate({ amplitude: 0, frequency: 0, speaking: false })
        }
      }
      
      return audio
    } catch (error) {
      console.error('Audio analysis error:', error)
      return null
    }
  }
  
  /**
   * Start continuous audio analysis
   */
  startAnalysis() {
    const analyze = () => {
      this.analyser.getByteFrequencyData(this.dataArray)
      
      // Calculate average amplitude
      let sum = 0
      for (let i = 0; i < this.dataArray.length; i++) {
        sum += this.dataArray[i]
      }
      const average = sum / this.dataArray.length
      
      // Normalize to 0-1
      const amplitude = Math.min(average / 128, 1)
      
      // Find dominant frequency
      let maxValue = 0
      let maxIndex = 0
      for (let i = 0; i < this.dataArray.length; i++) {
        if (this.dataArray[i] > maxValue) {
          maxValue = this.dataArray[i]
          maxIndex = i
        }
      }
      
      // Calculate frequency
      const nyquist = this.audioContext.sampleRate / 2
      const frequency = (maxIndex * nyquist) / this.dataArray.length
      
      // Determine if speaking (amplitude threshold)
      const speaking = amplitude > 0.1
      
      // Send update
      if (this.onUpdate) {
        this.onUpdate({
          amplitude,
          frequency,
          speaking,
          raw: Array.from(this.dataArray)
        })
      }
      
      this.animationFrame = requestAnimationFrame(analyze)
    }
    
    analyze()
  }
  
  /**
   * Stop analysis
   */
  stop() {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame)
      this.animationFrame = null
    }
  }
  
  /**
   * Cleanup resources
   */
  cleanup() {
    this.stop()
    if (this.audioContext) {
      this.audioContext.close()
      this.audioContext = null
    }
  }
}

/**
 * Simple mouth position calculator
 * Maps amplitude to mouth opening (0-1)
 */
export function calculateMouthOpening(amplitude) {
  // Apply some smoothing and scaling
  const scaled = Math.pow(amplitude, 0.7) // Power curve for more natural movement
  return Math.min(scaled * 1.2, 1)
}

/**
 * Get phoneme-based mouth shape (future enhancement)
 * For now, just use amplitude
 */
export function getPhonemeShape(frequency, amplitude) {
  // This can be enhanced with actual phoneme detection
  // For now, return simple open/closed based on amplitude
  return {
    open: amplitude > 0.3,
    wide: frequency > 1000,
    rounded: frequency < 500
  }
}

export default LipSyncAnalyzer

