'use client'

import React from 'react'
import { motion } from 'framer-motion'

interface GradientBlobProps {
  size?: number
  className?: string
}

export default function GradientBlob({ size = 175, className = '' }: GradientBlobProps) {
  return (
    <div className={`relative ${className}`} style={{ width: size, height: size }}>
      <motion.div
        className="absolute inset-0 rounded-full"
        style={{
          background: 'linear-gradient(135deg, rgba(58, 175, 143, 0.53) 0%, rgba(146, 91, 236, 0) 100%)',
          filter: 'blur(200px)',
        }}
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.5, 0.8, 0.5],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
      
      <motion.div
        className="absolute inset-0 rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(98, 98, 237, 1) 0%, rgba(98, 98, 237, 0) 100%)',
          filter: 'blur(200px)',
        }}
        animate={{
          scale: [1.2, 1, 1.2],
          opacity: [0.6, 0.4, 0.6],
        }}
        transition={{
          duration: 5,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
      
      {/* Additional gradient layers for depth */}
      <div
        className="absolute inset-0 rounded-full"
        style={{
          background: 'linear-gradient(135deg, rgba(114, 147, 250, 1) 0%, rgba(88, 58, 224, 1) 66.5%, rgba(82, 57, 237, 1) 91.1%)',
          mixBlendMode: 'normal',
        }}
      />
      
      <div
        className="absolute inset-0 rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(123, 98, 237, 1) 0%, rgba(123, 98, 237, 0) 100%)',
          mixBlendMode: 'linear-dodge',
        }}
      />
      
      {/* White highlight ellipses */}
      <motion.div
        className="absolute rounded-full"
        style={{
          width: '113px',
          height: '85px',
          background: 'conic-gradient(from 0deg, rgba(211, 186, 255, 1) 0.77%, rgba(146, 227, 255, 0) 25.8%, rgba(234, 227, 255, 0) 57%, rgba(79, 23, 151, 0) 73.2%)',
          filter: 'blur(1px)',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
        }}
        animate={{
          rotate: [0, 360],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: 'linear',
        }}
      />
      
      <motion.div
        className="absolute rounded-full"
        style={{
          width: '75px',
          height: '74px',
          background: 'radial-gradient(circle, rgba(255,255,255,1) 0%, rgba(255,255,255,1) 16.6%, rgba(207, 168, 255, 1) 33.5%, rgba(98, 98, 237, 0) 100%)',
          filter: 'blur(4px)',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
        }}
        animate={{
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
    </div>
  )
}

