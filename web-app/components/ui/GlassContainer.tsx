'use client'

import React from 'react'
import { motion } from 'framer-motion'

interface GlassContainerProps {
  children: React.ReactNode
  className?: string
  onClick?: () => void
  variant?: 'panel' | 'button' | 'card'
}

export default function GlassContainer({
  children,
  className = '',
  onClick,
  variant = 'panel'
}: GlassContainerProps) {
  const baseStyles = 'backdrop-blur-[20px] border border-white/10 rounded-xl'
  
  const variantStyles = {
    panel: 'bg-black/[0.001] shadow-[0_4px_12px_rgba(0,0,0,0.25),inset_3px_3px_9.8px_rgba(255,255,255,0.19),inset_-4px_-4px_5.7px_rgba(0,0,0,0.25)]',
    button: 'bg-black/[0.001] shadow-[0_4px_12px_rgba(0,0,0,0.25),inset_3px_3px_9.8px_rgba(255,255,255,0.19)] rounded-[20px] transition-all duration-300 hover:bg-white/5 hover:shadow-[0_6px_16px_rgba(0,0,0,0.3),inset_3px_3px_9.8px_rgba(255,255,255,0.25)]',
    card: 'bg-black/[0.001] shadow-[0_4px_12px_rgba(0,0,0,0.25),inset_3px_3px_9.8px_rgba(255,255,255,0.19)] p-6'
  }
  
  return (
    <motion.div
      className={`${baseStyles} ${variantStyles[variant]} ${className}`}
      onClick={onClick}
      whileHover={variant === 'button' ? { scale: 1.05 } : {}}
      whileTap={variant === 'button' ? { scale: 0.95 } : {}}
    >
      {children}
    </motion.div>
  )
}

