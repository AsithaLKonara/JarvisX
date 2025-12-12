'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'

export default function LandingPage() {
  return (
    <div className="min-h-screen gradient-bg">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <h1 className="text-6xl md:text-8xl font-bold mb-6 font-alata">
            <span className="text-white">JarvisX</span>
            <span className="text-primary-aqua"> V2</span>
          </h1>
          <p className="text-xl md:text-2xl text-white/80 mb-8 max-w-2xl mx-auto font-albert-sans">
            Ultra-optimized, intelligent AI assistant powered by a custom-trained Mistral 7B model 
            with 137,300 domain-specific examples.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link
              href="/login"
              className="glass-button px-8 py-4 text-lg font-semibold text-white hover:scale-105 transition-transform"
            >
              Get Started
            </Link>
            <Link
              href="/chat"
              className="glass-button px-8 py-4 text-lg font-semibold text-white hover:scale-105 transition-transform"
            >
              Try Demo
            </Link>
          </div>
        </motion.div>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          <div className="glass-panel p-6">
            <h3 className="text-2xl font-bold mb-3 text-primary-aqua">Multi-Platform</h3>
            <p className="text-white/70">
              Available on Web, Desktop (Windows/Linux/macOS), and Mobile (iOS/Android)
            </p>
          </div>
          
          <div className="glass-panel p-6">
            <h3 className="text-2xl font-bold mb-3 text-primary-purple">Smart AI</h3>
            <p className="text-white/70">
              Powered by custom-trained Mistral 7B with 137,300 domain-specific examples
            </p>
          </div>
          
          <div className="glass-panel p-6">
            <h3 className="text-2xl font-bold mb-3 text-primary-blue">Secure</h3>
            <p className="text-white/70">
              JWT authentication with Google, Apple, and Facebook OAuth support
            </p>
          </div>
        </motion.div>

        {/* Download Section */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="mt-20 text-center"
        >
          <h2 className="text-4xl font-bold mb-8 font-alata">Download Apps</h2>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="glass-button px-6 py-3 text-white">
              📱 Mobile App (iOS/Android)
            </button>
            <button className="glass-button px-6 py-3 text-white">
              💻 Desktop App (Windows/Linux/macOS)
            </button>
          </div>
        </motion.div>
      </section>
    </div>
  )
}

