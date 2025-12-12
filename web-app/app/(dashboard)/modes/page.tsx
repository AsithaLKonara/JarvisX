'use client'

import React, { useState } from 'react'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import { cn } from '@/lib/utils'

interface Mode {
  id: string
  name: string
  description: string
  icon: React.ReactNode
  enabled: boolean
  usageCount: number
  lastUsed?: string
}

const modes: Mode[] = [
  {
    id: 'engineer',
    name: 'Engineer Mode',
    description: 'Code review, debugging, and development assistance',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
      </svg>
    ),
    enabled: true,
    usageCount: 1245,
    lastUsed: '2 hours ago',
  },
  {
    id: 'system_monitor',
    name: 'System Monitor',
    description: 'PC performance monitoring and optimization',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    enabled: true,
    usageCount: 856,
    lastUsed: '5 hours ago',
  },
  {
    id: 'designer',
    name: 'Designer Mode',
    description: 'Design workflows, color theory, and visual guidance',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
      </svg>
    ),
    enabled: true,
    usageCount: 623,
    lastUsed: '1 day ago',
  },
  {
    id: 'editor',
    name: 'Editor Mode',
    description: 'Content editing, proofreading, and writing assistance',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
      </svg>
    ),
    enabled: true,
    usageCount: 987,
    lastUsed: '3 hours ago',
  },
  {
    id: 'business',
    name: 'Business Mode',
    description: 'Invoice generation, finance tracking, client management',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
      </svg>
    ),
    enabled: true,
    usageCount: 542,
    lastUsed: '6 hours ago',
  },
  {
    id: 'casual',
    name: 'Casual/Sinhala',
    description: 'Casual conversations and Sinhala language support',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
    ),
    enabled: true,
    usageCount: 423,
    lastUsed: '1 day ago',
  },
  {
    id: 'career',
    name: 'Career Assistant',
    description: 'Career guidance, resume help, and interview preparation',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    enabled: true,
    usageCount: 312,
    lastUsed: '2 days ago',
  },
]

export default function ModesPage() {
  const [modeStates, setModeStates] = useState<Record<string, boolean>>(
    Object.fromEntries(modes.map((m) => [m.id, m.enabled]))
  )

  const toggleMode = (modeId: string) => {
    setModeStates((prev) => ({
      ...prev,
      [modeId]: !prev[modeId],
    }))
    // TODO: Update mode via API
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-text-primary">Operational Modes</h1>
        <p className="mt-2 text-text-secondary">Manage and configure your AI operational modes.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {modes.map((mode) => (
          <Card key={mode.id} hover>
            <Card.Content>
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={cn(
                    'p-2 rounded-lg',
                    modeStates[mode.id] ? 'bg-primary/10 text-primary' : 'bg-gray-100 text-gray-400'
                  )}>
                    {mode.icon}
                  </div>
                  <div>
                    <h3 className="font-semibold text-text-primary">{mode.name}</h3>
                  </div>
                </div>
                <Badge variant={modeStates[mode.id] ? 'success' : 'default'}>
                  {modeStates[mode.id] ? 'Enabled' : 'Disabled'}
                </Badge>
              </div>
              <p className="text-sm text-text-secondary mb-4">{mode.description}</p>
              <div className="flex items-center justify-between text-sm text-text-secondary mb-4">
                <span>Used {mode.usageCount.toLocaleString()} times</span>
                {mode.lastUsed && <span>Last used {mode.lastUsed}</span>}
              </div>
              <div className="flex gap-2">
                <Button
                  variant={modeStates[mode.id] ? 'secondary' : 'primary'}
                  className="flex-1"
                  onClick={() => toggleMode(mode.id)}
                >
                  {modeStates[mode.id] ? 'Disable' : 'Enable'}
                </Button>
                <Button variant="ghost" size="sm">
                  Configure
                </Button>
              </div>
            </Card.Content>
          </Card>
        ))}
      </div>
    </div>
  )
}

