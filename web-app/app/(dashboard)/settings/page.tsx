'use client'

import React, { useState } from 'react'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import { Tabs } from '@/components/ui/Tabs'

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    name: 'John Doe',
    email: 'john@example.com',
    defaultMode: 'engineer',
    theme: 'light',
    language: 'en',
    notifications: true,
  })

  const handleSave = () => {
    // TODO: Save settings via API
    console.log('Saving settings:', settings)
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-text-primary">Settings</h1>
        <p className="mt-2 text-text-secondary">Manage your account settings and preferences.</p>
      </div>

      <Tabs defaultValue="profile">
        <Tabs.List>
          <Tabs.Trigger value="profile">Profile</Tabs.Trigger>
          <Tabs.Trigger value="preferences">Preferences</Tabs.Trigger>
          <Tabs.Trigger value="voice">Voice</Tabs.Trigger>
          <Tabs.Trigger value="api">API</Tabs.Trigger>
          <Tabs.Trigger value="security">Security</Tabs.Trigger>
        </Tabs.List>

        <Tabs.Content value="profile">
          <Card>
            <Card.Header>
              <h2 className="text-lg font-semibold text-text-primary">Profile Information</h2>
            </Card.Header>
            <Card.Content>
              <div className="space-y-4">
                <Input
                  label="Name"
                  value={settings.name}
                  onChange={(e) => setSettings({ ...settings, name: e.target.value })}
                />
                <Input
                  label="Email"
                  type="email"
                  value={settings.email}
                  onChange={(e) => setSettings({ ...settings, email: e.target.value })}
                />
                <Button onClick={handleSave} variant="primary">
                  Save Changes
                </Button>
              </div>
            </Card.Content>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="preferences">
          <Card>
            <Card.Header>
              <h2 className="text-lg font-semibold text-text-primary">Preferences</h2>
            </Card.Header>
            <Card.Content>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    Default Mode
                  </label>
                  <select
                    value={settings.defaultMode}
                    onChange={(e) => setSettings({ ...settings, defaultMode: e.target.value })}
                    className="w-full px-3.5 py-2 text-sm border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="engineer">Engineer Mode</option>
                    <option value="system">System Monitor</option>
                    <option value="designer">Designer Mode</option>
                    <option value="editor">Editor Mode</option>
                    <option value="business">Business Mode</option>
                    <option value="casual">Casual/Sinhala</option>
                    <option value="career">Career Assistant</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">Theme</label>
                  <select
                    value={settings.theme}
                    onChange={(e) => setSettings({ ...settings, theme: e.target.value })}
                    className="w-full px-3.5 py-2 text-sm border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                    <option value="system">System</option>
                  </select>
                </div>
                <Button onClick={handleSave} variant="primary">
                  Save Changes
                </Button>
              </div>
            </Card.Content>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="voice">
          <Card>
            <Card.Header>
              <h2 className="text-lg font-semibold text-text-primary">Voice Settings</h2>
            </Card.Header>
            <Card.Content>
              <div className="space-y-4">
                <p className="text-text-secondary">Voice settings will be available soon.</p>
              </div>
            </Card.Content>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="api">
          <Card>
            <Card.Header>
              <h2 className="text-lg font-semibold text-text-primary">API Settings</h2>
            </Card.Header>
            <Card.Content>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    API Key
                  </label>
                  <div className="flex gap-2">
                    <Input type="password" value="••••••••••••" readOnly />
                    <Button variant="secondary">Regenerate</Button>
                  </div>
                </div>
              </div>
            </Card.Content>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="security">
          <Card>
            <Card.Header>
              <h2 className="text-lg font-semibold text-text-primary">Security</h2>
            </Card.Header>
            <Card.Content>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    Change Password
                  </label>
                  <Input type="password" placeholder="New password" />
                  <Input type="password" placeholder="Confirm password" className="mt-2" />
                  <Button variant="primary" className="mt-2">Update Password</Button>
                </div>
              </div>
            </Card.Content>
          </Card>
        </Tabs.Content>
      </Tabs>
    </div>
  )
}

