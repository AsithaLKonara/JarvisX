import { useState, useEffect, useRef } from 'react'

export default function Avatar({ ttsActive, currentEmotion = 'neutral', audioData }) {
  const [blinking, setBlinking] = useState(false)
  const [mouthOpen, setMouthOpen] = useState(0) // 0-1, lip-sync value
  const [thinking, setThinking] = useState(false)
  
  // Blink animation
  useEffect(() => {
    const blinkInterval = setInterval(() => {
      setBlinking(true)
      setTimeout(() => setBlinking(false), 150)
    }, 3000 + Math.random() * 2000) // Random blink every 3-5 seconds
    
    return () => clearInterval(blinkInterval)
  }, [])
  
  // Thinking pulse when TTS is active
  useEffect(() => {
    setThinking(ttsActive)
  }, [ttsActive])
  
  // Lip-sync based on audio data
  useEffect(() => {
    if (audioData && ttsActive) {
      // Map audio amplitude to mouth opening (0-1)
      const amplitude = audioData.amplitude || 0
      setMouthOpen(Math.min(amplitude * 1.5, 1))
    } else {
      setMouthOpen(0)
    }
  }, [audioData, ttsActive])
  
  // Calculate mouth path based on opening
  const getMouthPath = () => {
    const baseY = 120
    const openAmount = mouthOpen * 15 // Max 15px opening
    return `M 70 ${baseY} Q 100 ${baseY + openAmount} 130 ${baseY}`
  }
  
  // Eye size for blinking
  const eyeRadius = blinking ? 2 : 8
  
  return (
    <svg 
      className="avatar-svg"
      width="240" 
      height="240" 
      viewBox="0 0 200 200"
      style={{
        filter: thinking ? 'drop-shadow(0 0 30px var(--glow-primary))' : 'drop-shadow(0 0 15px var(--glow-primary))'
      }}>
      
      <defs>
        {/* Gradient for avatar head */}
        <radialGradient id="avatarGradient">
          <stop offset="0%" stopColor="var(--glow-primary)" stopOpacity="0.2" />
          <stop offset="100%" stopColor="var(--glow-secondary)" stopOpacity="0.4" />
        </radialGradient>
        
        {/* Glow filter */}
        <filter id="glow">
          <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      {/* Background glow circle */}
      <circle 
        cx="100" 
        cy="100" 
        r="85" 
        fill="url(#avatarGradient)"
        opacity={thinking ? "0.8" : "0.4"}
        className="transition-opacity duration-300">
        {thinking && (
          <animate 
            attributeName="r" 
            values="85;90;85" 
            dur="2s" 
            repeatCount="indefinite" 
          />
        )}
      </circle>
      
      {/* Head circle */}
      <circle 
        cx="100" 
        cy="100" 
        r="70" 
        fill="transparent"
        stroke="var(--glow-primary)"
        strokeWidth="2"
        filter="url(#glow)"
      />
      
      {/* Left eye */}
      <circle 
        cx="75" 
        cy="85" 
        r={eyeRadius}
        fill="var(--glow-primary)"
        filter="url(#glow)"
        className="transition-all duration-150">
        {!blinking && (
          <animate 
            attributeName="opacity" 
            values="1;0.7;1" 
            dur="3s" 
            repeatCount="indefinite" 
          />
        )}
      </circle>
      
      {/* Right eye */}
      <circle 
        cx="125" 
        cy="85" 
        r={eyeRadius}
        fill="var(--glow-primary)"
        filter="url(#glow)"
        className="transition-all duration-150">
        {!blinking && (
          <animate 
            attributeName="opacity" 
            values="1;0.7;1" 
            dur="3s" 
            repeatCount="indefinite" 
          />
        )}
      </circle>
      
      {/* Mouth - animated with lip-sync */}
      <path 
        d={getMouthPath()}
        stroke="var(--glow-primary)"
        strokeWidth="3"
        strokeLinecap="round"
        fill="none"
        filter="url(#glow)"
        className="transition-all duration-100"
      />
      
      {/* Outer glow ring */}
      <circle 
        cx="100" 
        cy="100" 
        r="80" 
        fill="none"
        stroke="var(--glow-primary)"
        strokeWidth="1"
        opacity="0.3">
        <animate 
          attributeName="r" 
          values="80;82;80" 
          dur="4s" 
          repeatCount="indefinite" 
        />
        <animate 
          attributeName="opacity" 
          values="0.3;0.5;0.3" 
          dur="4s" 
          repeatCount="indefinite" 
        />
      </circle>
      
      {/* Thinking indicator particles */}
      {thinking && (
        <>
          <circle cx="60" cy="60" r="3" fill="var(--glow-secondary)" opacity="0.8">
            <animate attributeName="cy" values="60;40;60" dur="2s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="0.8;0;0.8" dur="2s" repeatCount="indefinite" />
          </circle>
          <circle cx="140" cy="60" r="3" fill="var(--glow-secondary)" opacity="0.8">
            <animate attributeName="cy" values="60;40;60" dur="2.2s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="0.8;0;0.8" dur="2.2s" repeatCount="indefinite" />
          </circle>
          <circle cx="100" cy="50" r="3" fill="var(--glow-secondary)" opacity="0.8">
            <animate attributeName="cy" values="50;30;50" dur="1.8s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="0.8;0;0.8" dur="1.8s" repeatCount="indefinite" />
          </circle>
        </>
      )}
      
      {/* Emotion indicator (color shift) */}
      {currentEmotion === 'happy' && (
        <path 
          d="M 75 95 Q 100 105 125 95"
          stroke="var(--success)"
          strokeWidth="2"
          fill="none"
          opacity="0.5"
        />
      )}
    </svg>
  )
}

