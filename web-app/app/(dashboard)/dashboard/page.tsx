'use client'

import React from 'react'
import Card from '@/components/ui/Card'
// Using inline SVG icons

export default function DashboardPage() {
  const stats = [
    {
      name: 'Total Conversations',
      value: '142',
      icon: (props: { className?: string }) => (
        <svg className={props.className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      ),
      change: '+12%',
      changeType: 'positive',
    },
    {
      name: 'Messages Sent',
      value: '1,234',
      icon: (props: { className?: string }) => (
        <svg className={props.className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      ),
      change: '+8%',
      changeType: 'positive',
    },
    {
      name: 'Usage This Month',
      value: '89%',
      icon: (props: { className?: string }) => (
        <svg className={props.className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      change: '+5%',
      changeType: 'positive',
    },
    {
      name: 'Active Modes',
      value: '7',
      icon: (props: { className?: string }) => (
        <svg className={props.className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      change: 'All',
      changeType: 'neutral',
    },
  ]

  const recentConversations = [
    { id: '1', title: 'Code Review Discussion', mode: 'Engineer', lastMessage: '2 hours ago' },
    { id: '2', title: 'System Optimization', mode: 'System Monitor', lastMessage: '5 hours ago' },
    { id: '3', title: 'Design Workflow', mode: 'Designer', lastMessage: '1 day ago' },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-text-primary">Dashboard</h1>
        <p className="mt-2 text-text-secondary">Welcome back! Here's what's happening with your AI assistant.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {stats.map((stat) => (
          <Card key={stat.name} hover>
            <Card.Content>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-text-secondary">{stat.name}</p>
                  <p className="mt-2 text-3xl font-bold text-text-primary">{stat.value}</p>
                  <p
                    className={`mt-1 text-sm ${
                      stat.changeType === 'positive'
                        ? 'text-green-600'
                        : stat.changeType === 'negative'
                        ? 'text-red-600'
                        : 'text-text-secondary'
                    }`}
                  >
                    {stat.change} from last month
                  </p>
                </div>
                <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-primary/10">
                  <stat.icon className="w-6 h-6 text-primary" />
                </div>
              </div>
            </Card.Content>
          </Card>
        ))}
      </div>

      {/* Recent Conversations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <Card.Header>
            <h2 className="text-lg font-semibold text-text-primary">Recent Conversations</h2>
          </Card.Header>
          <Card.Content>
            <div className="space-y-4">
              {recentConversations.map((conv) => (
                <div
                  key={conv.id}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-background-surface transition-colors cursor-pointer"
                >
                  <div>
                    <p className="font-medium text-text-primary">{conv.title}</p>
                    <p className="text-sm text-text-secondary">{conv.mode} • {conv.lastMessage}</p>
                  </div>
                  <button className="text-text-tertiary hover:text-text-primary">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  </button>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <a
                href="/conversations"
                className="text-sm text-primary hover:text-primary-hover font-medium"
              >
                View all conversations →
              </a>
            </div>
          </Card.Content>
        </Card>

        <Card>
          <Card.Header>
            <h2 className="text-lg font-semibold text-text-primary">Quick Actions</h2>
          </Card.Header>
          <Card.Content>
            <div className="space-y-3">
              <a
                href="/chat"
                className="block p-3 border border-border rounded-lg hover:bg-background-surface transition-colors"
              >
                <div className="font-medium text-text-primary">Start New Chat</div>
                <div className="text-sm text-text-secondary mt-1">Begin a new conversation</div>
              </a>
              <a
                href="/integrations"
                className="block p-3 border border-border rounded-lg hover:bg-background-surface transition-colors"
              >
                <div className="font-medium text-text-primary">Connect Integration</div>
                <div className="text-sm text-text-secondary mt-1">Link external services</div>
              </a>
              <a
                href="/settings"
                className="block p-3 border border-border rounded-lg hover:bg-background-surface transition-colors"
              >
                <div className="font-medium text-text-primary">Configure Settings</div>
                <div className="text-sm text-text-secondary mt-1">Update preferences</div>
              </a>
            </div>
          </Card.Content>
        </Card>
      </div>
    </div>
  )
}

