'use client'

import React from 'react'
import { motion } from 'framer-motion'

interface IntegrationLogo {
  name: string
  logo: React.ReactNode | string
  url?: string
}

interface IntegrationLogosSectionProps {
  integrations?: IntegrationLogo[]
  title?: string
  description?: string
}

const defaultIntegrations: IntegrationLogo[] = [
  { name: 'Slack', logo: '💬' },
  { name: 'GitHub', logo: '🐙' },
  { name: 'Notion', logo: '📝' },
  { name: 'Google Drive', logo: '📁' },
  { name: 'Dropbox', logo: '☁️' },
  { name: 'Zapier', logo: '⚡' },
]

export default function IntegrationLogosSection({
  integrations = defaultIntegrations,
  title = 'Integrations',
  description = 'Connect with the tools you already use',
}: IntegrationLogosSectionProps) {
  return (
    <section className="py-16 bg-white border-y border-border">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-2xl font-bold text-text-primary">{title}</h2>
          <p className="mt-2 text-text-secondary">{description}</p>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8 items-center justify-items-center">
          {integrations.map((integration, index) => (
            <motion.div
              key={integration.name}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className="flex flex-col items-center gap-2 opacity-60 hover:opacity-100 transition-opacity cursor-pointer"
            >
              <div className="text-4xl">{integration.logo}</div>
              <span className="text-sm text-text-secondary">{integration.name}</span>
            </motion.div>
          ))}
        </div>
        <div className="text-center mt-12">
          <a
            href="/integrations"
            className="text-primary hover:underline text-sm font-medium"
          >
            View all integrations →
          </a>
        </div>
      </div>
    </section>
  )
}

