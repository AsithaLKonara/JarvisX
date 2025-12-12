'use client'

import React, { useEffect, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import Card from '@/components/ui/Card'

export default function OAuthCallbackPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const { oauthLogin } = useAuth()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code')
      const state = searchParams.get('state')
      const provider = state?.split('_')[0] || searchParams.get('provider') || 'google'
      const error = searchParams.get('error')

      if (error) {
        setError(`OAuth error: ${error}`)
        setStatus('error')
        return
      }

      if (!code) {
        setError('No authorization code received')
        setStatus('error')
        return
      }

      try {
        // Exchange code for token
        // In a real implementation, you'd exchange the code for a token server-side
        // For now, we'll use the code directly (this is a simplified version)
        const tokenResponse = await fetch('/api/oauth/exchange', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ code, provider, redirect_uri: window.location.origin + '/oauth/callback' }),
        })

        if (!tokenResponse.ok) {
          throw new Error('Failed to exchange code for token')
        }

        const { access_token } = await tokenResponse.json()

        // Login with OAuth token
        const result = await oauthLogin(provider, access_token)

        if (result.success) {
          setStatus('success')
          setTimeout(() => {
            router.push('/chat')
          }, 1500)
        } else {
          setError(result.error || 'OAuth login failed')
          setStatus('error')
        }
      } catch (err: any) {
        setError(err.message || 'An error occurred during OAuth callback')
        setStatus('error')
      }
    }

    handleCallback()
  }, [searchParams, router, oauthLogin])

  return (
    <div className="min-h-screen flex items-center justify-center bg-background-surface px-4 py-12">
      <Card className="w-full max-w-md">
        <Card.Content>
          {status === 'loading' && (
            <div className="text-center py-8">
              <div className="w-12 h-12 mx-auto border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
              <h2 className="text-xl font-semibold text-text-primary mb-2">Completing sign in...</h2>
              <p className="text-text-secondary">Please wait while we authenticate you.</p>
            </div>
          )}

          {status === 'success' && (
            <div className="text-center py-8">
              <div className="w-12 h-12 mx-auto bg-success/10 rounded-full flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-text-primary mb-2">Success!</h2>
              <p className="text-text-secondary">Redirecting to chat...</p>
            </div>
          )}

          {status === 'error' && (
            <div className="text-center py-8">
              <div className="w-12 h-12 mx-auto bg-error/10 rounded-full flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-text-primary mb-2">Authentication Failed</h2>
              <p className="text-text-secondary mb-4">{error}</p>
              <button
                onClick={() => router.push('/login')}
                className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-hover transition-colors"
              >
                Back to Login
              </button>
            </div>
          )}
        </Card.Content>
      </Card>
    </div>
  )
}
