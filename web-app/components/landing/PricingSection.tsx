'use client'

import React from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import Button from '../ui/Button'
import Card from '../ui/Card'
import Badge from '../ui/Badge'

interface PricingPlan {
  name: string
  price: string
  period: string
  description: string
  features: string[]
  cta: string
  ctaLink: string
  popular?: boolean
  badge?: string
}

interface PricingSectionProps {
  plans?: PricingPlan[]
}

const defaultPlans: PricingPlan[] = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    description: 'Perfect for trying out JarvisX',
    features: [
      '100 messages per month',
      'Basic AI modes',
      'Web access only',
      'Community support',
    ],
    cta: 'Get Started',
    ctaLink: '/signup',
  },
  {
    name: 'Pro',
    price: '$29',
    period: 'per month',
    description: 'For professionals and small teams',
    features: [
      'Unlimited messages',
      'All 7 AI modes',
      'Web, Mobile, Desktop access',
      'Priority support',
      'Advanced integrations',
      'Export conversations',
    ],
    cta: 'Start Free Trial',
    ctaLink: '/signup',
    popular: true,
    badge: 'Most Popular',
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    description: 'For large organizations',
    features: [
      'Everything in Pro',
      'Dedicated support',
      'Custom integrations',
      'SLA guarantees',
      'Team management',
      'Advanced analytics',
      'On-premise deployment',
    ],
    cta: 'Contact Sales',
    ctaLink: '/contact',
  },
]

export default function PricingSection({ plans = defaultPlans }: PricingSectionProps) {
  return (
    <section id="pricing" className="py-24 sm:py-32 bg-background-surface">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-text-primary sm:text-4xl">
            Simple, transparent pricing
          </h2>
          <p className="mt-4 text-lg text-text-secondary">
            Choose the plan that's right for you. All plans include our core features.
          </p>
        </div>
        <div className="mx-auto mt-16 grid max-w-2xl grid-cols-1 gap-8 sm:mt-20 lg:mx-0 lg:max-w-none lg:grid-cols-3">
          {plans.map((plan, index) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className={plan.popular ? 'lg:scale-105' : ''}
            >
              <Card hover={!plan.popular} className={plan.popular ? 'ring-2 ring-primary' : ''}>
                {plan.popular && plan.badge && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge variant="default" className="bg-primary text-white">
                      {plan.badge}
                    </Badge>
                  </div>
                )}
                <Card.Header>
                  <Card.Title className="text-2xl font-bold">{plan.name}</Card.Title>
                  <div className="mt-4">
                    <span className="text-4xl font-bold text-text-primary">{plan.price}</span>
                    {plan.period && (
                      <span className="text-text-secondary ml-2">{plan.period}</span>
                    )}
                  </div>
                  <Card.Description className="mt-2">{plan.description}</Card.Description>
                </Card.Header>
                <Card.Content>
                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, i) => (
                      <li key={i} className="flex items-start gap-3">
                        <svg
                          className="w-5 h-5 text-primary flex-shrink-0 mt-0.5"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                        <span className="text-text-secondary">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <Link href={plan.ctaLink}>
                    <Button
                      variant={plan.popular ? 'primary' : 'secondary'}
                      className="w-full"
                      size="lg"
                    >
                      {plan.cta}
                    </Button>
                  </Link>
                </Card.Content>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}


