'use client'

import React from 'react'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'

export default function IntegrationsPage() {
  const integrations = [
    { id: 'slack', name: 'Slack', description: 'Send messages and notifications', status: 'connected' },
    { id: 'github', name: 'GitHub', description: 'Code repository integration', status: 'available' },
    { id: 'notion', name: 'Notion', description: 'Notes and documentation', status: 'available' },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-text-primary">Integrations</h1>
        <p className="mt-2 text-text-secondary">Connect external services to enhance your workflow.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {integrations.map((integration) => (
          <Card key={integration.id} hover>
            <Card.Content>
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="font-semibold text-text-primary">{integration.name}</h3>
                  <p className="text-sm text-text-secondary mt-1">{integration.description}</p>
                </div>
                <Badge variant={integration.status === 'connected' ? 'success' : 'default'}>
                  {integration.status}
                </Badge>
              </div>
              <Button
                variant={integration.status === 'connected' ? 'secondary' : 'primary'}
                className="w-full"
              >
                {integration.status === 'connected' ? 'Manage' : 'Connect'}
              </Button>
            </Card.Content>
          </Card>
        ))}
      </div>
    </div>
  )
}

