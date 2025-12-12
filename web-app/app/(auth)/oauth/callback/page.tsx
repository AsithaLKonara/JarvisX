'use client'

import { useEffect, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { handleOAuthCallback } from '@/lib/auth/oauth'
import { tokenManager } from '@/lib/auth/jwt'
import apiClient from '@/lib/api/client'

export default function OAuthCallbackPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [error, setError] = useState<string>('')
  
  useEffect(() => {
    const processCallback = async () => {
      const code = searchParams.get('code')
      const state = searchParams.get('state')
      const provider = localStorage.getItem('oauth_provider') as 'google' | 'apple' | 'facebook'
      
      if (!code || !state || !provider) {
        setStatus('error')
        setError('Missing OAuth parameters')
        return
      }
      
      try {
        // Exchange code for token
        const { access_token, refresh_token } = await handleOAuthCallback(code, state, provider)
        
        // Store tokens
        tokenManager.setTokens(access_token, refresh_token)
        
        // Clear OAuth state
        localStorage.removeItem('oauth_state')
        localStorage.removeItem('oauth_provider')
        
        // Get user info
        const userResponse = await apiClient.get('/user/me')
        // User info will be stored by useAuth hook
        
        setStatus('success')
        
        // Redirect to chat
        setTimeout(() => {
          router.push('/chat')
        }, 1000)
      } catch (err: any) {
        setStatus('error')
        setError(err.message || 'OAuth callback failed')
      }
    }
    
    processCallback()
  }, [searchParams, router])
  
  return (
    <div className="min-h-screen gradient-bg flex items-center justify-center p-4">
      <div className="glass-panel p-8 text-center">
        {status === 'loading' && (
          <>
            <div className="w-12 h-12 border-4 border-primary-aqua border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-white">Completing authentication...</p>
          </>
        )}
        
        {status === 'success' && (
          <>
            <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <p className="text-white">Authentication successful! Redirecting...</p>
          </>
        )}
        
        {status === 'error' && (
          <>
            <div className="w-12 h-12 bg-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <p className="text-red-400 mb-4">{error}</p>
            <a href="/login" className="text-primary-aqua hover:underline">
              Return to login
            </a>
          </>
        )}
      </div>
    </div>
  )
}

