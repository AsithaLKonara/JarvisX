'use client'

import React, { useEffect, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/hooks/useAuth'
import Button from '@/components/ui/Button'
import Card from '@/components/ui/Card'

export default function VerifyEmailPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const { verifyEmail } = useAuth()
  const [isLoading, setIsLoading] = useState(true)
  const [isSuccess, setIsSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const token = searchParams.get('token')
    if (!token) {
      setError('Verification token is missing')
      setIsLoading(false)
      return
    }

    const verify = async () => {
      const result = await verifyEmail(token)
      
      if (result.success) {
        setIsSuccess(true)
      } else {
        setError(result.error || 'Failed to verify email')
      }
      
      setIsLoading(false)
    }

    verify()
  }, [searchParams, verifyEmail])

  return (
    <div className="min-h-screen flex items-center justify-center bg-background-surface py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <Card.Header>
          <Card.Title className="text-2xl font-bold text-center">Email Verification</Card.Title>
        </Card.Header>
        <Card.Content>
          {isLoading ? (
            <div className="text-center py-8">
              <div className="w-12 h-12 mx-auto border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
              <p className="text-text-secondary">Verifying your email...</p>
            </div>
          ) : isSuccess ? (
            <div className="text-center space-y-4">
              <div className="w-12 h-12 mx-auto bg-success/10 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-text-primary">Email Verified</h3>
              <p className="text-text-secondary">
                Your email has been successfully verified. You can now use all features.
              </p>
              <Link href="/dashboard">
                <Button variant="primary" className="w-full mt-4">
                  Go to Dashboard
                </Button>
              </Link>
            </div>
          ) : (
            <div className="text-center space-y-4">
              <div className="w-12 h-12 mx-auto bg-error/10 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-text-primary">Verification Failed</h3>
              <p className="text-text-secondary">
                {error || 'The verification link is invalid or has expired.'}
              </p>
              <div className="space-y-2">
                <Link href="/login">
                  <Button variant="primary" className="w-full">
                    Back to Login
                  </Button>
                </Link>
                <Link href="/signup">
                  <Button variant="secondary" className="w-full">
                    Create New Account
                  </Button>
                </Link>
              </div>
            </div>
          )}
        </Card.Content>
      </Card>
    </div>
  )
}

