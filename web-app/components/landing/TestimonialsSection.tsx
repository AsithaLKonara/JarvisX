'use client'

import React from 'react'
import { motion } from 'framer-motion'
import Card from '../ui/Card'

interface Testimonial {
  name: string
  role: string
  company?: string
  content: string
  avatar?: string
  rating?: number
}

interface TestimonialsSectionProps {
  testimonials?: Testimonial[]
}

const defaultTestimonials: Testimonial[] = [
  {
    name: 'Sarah Chen',
    role: 'Senior Developer',
    company: 'Tech Corp',
    content: 'JarvisX has completely transformed how I work. The code review features are incredibly accurate and save me hours every day.',
    rating: 5,
  },
  {
    name: 'Michael Rodriguez',
    role: 'Product Manager',
    company: 'StartupXYZ',
    content: 'The business mode helps me generate reports and invoices in seconds. It\'s like having a personal assistant that never sleeps.',
    rating: 5,
  },
  {
    name: 'Emily Johnson',
    role: 'Designer',
    company: 'Creative Studio',
    content: 'As a designer, I love the color theory guidance and workflow automation. It\'s become an essential part of my toolkit.',
    rating: 5,
  },
]

export default function TestimonialsSection({ testimonials = defaultTestimonials }: TestimonialsSectionProps) {
  return (
    <section id="testimonials" className="py-24 sm:py-32 bg-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-text-primary sm:text-4xl">
            What Our Users Say
          </h2>
          <p className="mt-4 text-lg text-text-secondary">
            Join thousands of professionals who use JarvisX to boost their productivity.
          </p>
        </div>
        <div className="mx-auto mt-16 grid max-w-2xl grid-cols-1 gap-8 sm:mt-20 lg:mx-0 lg:max-w-none lg:grid-cols-3">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card hover className="h-full">
                <Card.Content>
                  {testimonial.rating && (
                    <div className="flex gap-1 mb-4">
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <svg
                          key={i}
                          className="w-5 h-5 text-yellow-400"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                      ))}
                    </div>
                  )}
                  <p className="text-text-secondary mb-6">"{testimonial.content}"</p>
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary font-semibold">
                      {testimonial.name[0]}
                    </div>
                    <div>
                      <div className="font-semibold text-text-primary">{testimonial.name}</div>
                      <div className="text-sm text-text-secondary">
                        {testimonial.role}
                        {testimonial.company && ` at ${testimonial.company}`}
                      </div>
                    </div>
                  </div>
                </Card.Content>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

