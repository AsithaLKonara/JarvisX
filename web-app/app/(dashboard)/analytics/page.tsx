'use client'

import React, { useState } from 'react'
import Card from '@/components/ui/Card'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

// Mock data - replace with real API data
const usageData = [
  { date: 'Mon', messages: 120, conversations: 15 },
  { date: 'Tue', messages: 190, conversations: 22 },
  { date: 'Wed', messages: 150, conversations: 18 },
  { date: 'Thu', messages: 210, conversations: 25 },
  { date: 'Fri', messages: 180, conversations: 20 },
  { date: 'Sat', messages: 90, conversations: 12 },
  { date: 'Sun', messages: 70, conversations: 10 },
]

const modeUsageData = [
  { name: 'Engineer', value: 35 },
  { name: 'Business', value: 25 },
  { name: 'Designer', value: 15 },
  { name: 'System Monitor', value: 12 },
  { name: 'Editor', value: 8 },
  { name: 'Career', value: 5 },
]

const responseTimeData = [
  { date: 'Mon', avg: 1.2 },
  { date: 'Tue', avg: 1.1 },
  { date: 'Wed', avg: 1.3 },
  { date: 'Thu', avg: 1.0 },
  { date: 'Fri', avg: 1.2 },
  { date: 'Sat', avg: 1.1 },
  { date: 'Sun', avg: 1.2 },
]

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState('7d')

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Analytics</h1>
          <p className="mt-2 text-text-secondary">View usage statistics and performance metrics.</p>
        </div>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="px-4 py-2 border border-border rounded-lg bg-white text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="90d">Last 90 days</option>
          <option value="custom">Custom range</option>
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Usage Chart */}
        <Card>
          <Card.Header>
            <h2 className="text-lg font-semibold text-text-primary">Usage Over Time</h2>
          </Card.Header>
          <Card.Content>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={usageData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="date" stroke="#6b7280" />
                <YAxis stroke="#6b7280" />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="messages" stroke="#6366f1" strokeWidth={2} name="Messages" />
                <Line type="monotone" dataKey="conversations" stroke="#10b981" strokeWidth={2} name="Conversations" />
              </LineChart>
            </ResponsiveContainer>
          </Card.Content>
        </Card>

        {/* Mode Usage */}
        <Card>
          <Card.Header>
            <h2 className="text-lg font-semibold text-text-primary">Mode Usage</h2>
          </Card.Header>
          <Card.Content>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={modeUsageData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {modeUsageData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card.Content>
        </Card>
      </div>

      {/* Response Time Chart */}
      <Card>
        <Card.Header>
          <h2 className="text-lg font-semibold text-text-primary">Average Response Time</h2>
        </Card.Header>
        <Card.Content>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={responseTimeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="date" stroke="#6b7280" />
              <YAxis stroke="#6b7280" unit="s" />
              <Tooltip />
              <Bar dataKey="avg" fill="#6366f1" name="Avg Response Time (s)" />
            </BarChart>
          </ResponsiveContainer>
        </Card.Content>
      </Card>
    </div>
  )
}
