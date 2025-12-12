'use client'

import React from 'react'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'

export default function BillingPage() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-text-primary">Billing</h1>
        <p className="mt-2 text-text-secondary">Manage your subscription and billing information.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <Card.Header>
            <h2 className="text-lg font-semibold text-text-primary">Current Plan</h2>
          </Card.Header>
          <Card.Content>
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-text-primary">Pro</span>
                  <Badge variant="success">Active</Badge>
                </div>
                <p className="text-text-secondary mt-1">$29/month</p>
              </div>
              <Button variant="secondary" className="w-full">Change Plan</Button>
            </div>
          </Card.Content>
        </Card>

        <Card>
          <Card.Header>
            <h2 className="text-lg font-semibold text-text-primary">Usage</h2>
          </Card.Header>
          <Card.Content>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-text-secondary">Messages</span>
                  <span className="text-text-primary">1,234 / 10,000</span>
                </div>
                <div className="w-full bg-background-surface rounded-full h-2">
                  <div className="bg-primary h-2 rounded-full" style={{ width: '12.34%' }}></div>
                </div>
              </div>
            </div>
          </Card.Content>
        </Card>
      </div>
    </div>
  )
}

