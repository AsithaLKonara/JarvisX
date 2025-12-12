'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'

interface MicrophoneButtonProps {
  onRecordStart?: () => void
  onRecordStop?: () => void
  size?: number
  className?: string
}

export default function MicrophoneButton({
  onRecordStart,
  onRecordStop,
  size = 54,
  className = ''
}: MicrophoneButtonProps) {
  const [isRecording, setIsRecording] = useState(false)
  
  const handleClick = () => {
    if (isRecording) {
      setIsRecording(false)
      onRecordStop?.()
    } else {
      setIsRecording(true)
      onRecordStart?.()
    }
  }
  
  return (
    <motion.button
      className={`glass-button rounded-full flex items-center justify-center ${className}`}
      style={{ width: size, height: size }}
      onClick={handleClick}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      animate={isRecording ? {
        boxShadow: [
          '0 0 0 0 rgba(58, 175, 143, 0.7)',
          '0 0 0 10px rgba(58, 175, 143, 0)',
          '0 0 0 0 rgba(58, 175, 143, 0.7)',
        ],
      } : {}}
      transition={{
        duration: 1.5,
        repeat: isRecording ? Infinity : 0,
      }}
    >
      <svg
        width="32"
        height="32"
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Microphone body */}
        <path
          d="M16 2C14.34 2 13 3.34 13 5V15C13 16.66 14.34 18 16 18C17.66 18 19 16.66 19 15V5C19 3.34 17.66 2 16 2Z"
          stroke="white"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* Microphone stand */}
        <path
          d="M16 18V22"
          stroke="white"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* Microphone base lines */}
        <line
          x1="12"
          y1="22"
          x2="20"
          y2="22"
          stroke="white"
          strokeWidth="3"
          strokeLinecap="round"
        />
        <line
          x1="14"
          y1="26"
          x2="18"
          y2="26"
          stroke="white"
          strokeWidth="3"
          strokeLinecap="round"
        />
      </svg>
    </motion.button>
  )
}

