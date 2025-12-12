'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import GlassContainer from '../ui/GlassContainer'
import { initiateGoogleOAuth, initiateAppleOAuth, initiateFacebookOAuth } from '@/lib/auth/oauth'

export default function RegisterForm() {
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { register } = useAuth()
  const router = useRouter()
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }
    
    if (password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }
    
    setIsLoading(true)
    
    const result = await register(email, password, username || undefined)
    
    if (result.success) {
      router.push('/chat')
    } else {
      setError(result.error || 'Registration failed')
    }
    
    setIsLoading(false)
  }
  
  const handleGoogleLogin = () => {
    const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || ''
    const redirectUri = `${window.location.origin}/oauth/callback`
    initiateGoogleOAuth(clientId, redirectUri)
  }
  
  const handleAppleLogin = () => {
    const clientId = process.env.NEXT_PUBLIC_APPLE_CLIENT_ID || ''
    const redirectUri = `${window.location.origin}/oauth/callback`
    initiateAppleOAuth(clientId, redirectUri)
  }
  
  const handleFacebookLogin = () => {
    const appId = process.env.NEXT_PUBLIC_FACEBOOK_APP_ID || ''
    const redirectUri = `${window.location.origin}/oauth/callback`
    initiateFacebookOAuth(appId, redirectUri)
  }
  
  return (
    <GlassContainer variant="card" className="w-full max-w-md mx-auto">
      <h2 className="text-3xl font-bold mb-6 text-center font-alata">Sign Up</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2 text-white/80">
            Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full glass-panel px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-primary-aqua"
            placeholder="your@email.com"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2 text-white/80">
            Username (optional)
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full glass-panel px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-primary-aqua"
            placeholder="username"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2 text-white/80">
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            className="w-full glass-panel px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-primary-aqua"
            placeholder="••••••••"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2 text-white/80">
            Confirm Password
          </label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            minLength={8}
            className="w-full glass-panel px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-primary-aqua"
            placeholder="••••••••"
          />
        </div>
        
        {error && (
          <div className="text-red-400 text-sm">{error}</div>
        )}
        
        <button
          type="submit"
          disabled={isLoading}
          className="w-full glass-button py-3 text-white font-semibold disabled:opacity-50"
        >
          {isLoading ? 'Creating account...' : 'Sign Up'}
        </button>
      </form>
      
      <div className="mt-6">
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-white/20"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-black text-white/60">Or continue with</span>
          </div>
        </div>
        
        <div className="mt-4 grid grid-cols-3 gap-3">
          <button
            onClick={handleGoogleLogin}
            className="glass-button py-3 text-white text-sm font-medium"
          >
            Google
          </button>
          <button
            onClick={handleAppleLogin}
            className="glass-button py-3 text-white text-sm font-medium"
          >
            Apple
          </button>
          <button
            onClick={handleFacebookLogin}
            className="glass-button py-3 text-white text-sm font-medium"
          >
            Facebook
          </button>
        </div>
      </div>
      
      <p className="mt-6 text-center text-sm text-white/60">
        Already have an account?{' '}
        <a href="/login" className="text-primary-aqua hover:underline">
          Login
        </a>
      </p>
    </GlassContainer>
  )
}

