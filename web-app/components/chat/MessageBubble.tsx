'use client'

import React, { useState } from 'react'
// Using inline SVG icons
import { cn } from '@/lib/utils'
import MarkdownRenderer from './MarkdownRenderer'

interface MessageBubbleProps {
  id?: string
  message: string
  role: 'user' | 'assistant'
  timestamp?: Date | string
  onEdit?: (id: string, newContent: string) => void
  onDelete?: (id: string) => void
}

export default function MessageBubble({ 
  id, 
  message, 
  role, 
  timestamp, 
  onEdit, 
  onDelete 
}: MessageBubbleProps) {
  const [copied, setCopied] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [editedContent, setEditedContent] = useState(message)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleEdit = () => {
    setIsEditing(true)
    setEditedContent(message)
  }

  const handleSaveEdit = () => {
    if (id && onEdit && editedContent.trim() && editedContent !== message) {
      onEdit(id, editedContent.trim())
    }
    setIsEditing(false)
  }

  const handleCancelEdit = () => {
    setEditedContent(message)
    setIsEditing(false)
  }

  const handleDelete = () => {
    if (id && onDelete && confirm('Are you sure you want to delete this message?')) {
      onDelete(id)
    }
  }

  const isUser = role === 'user'

  return (
    <div className={cn('flex gap-4 px-4 py-4 group hover:bg-gray-50', !isUser && 'bg-gray-50')}>
      {/* Avatar */}
      <div className={cn(
        'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium',
        isUser ? 'bg-primary text-white' : 'bg-gray-300 text-gray-700'
      )}>
        {isUser ? 'U' : 'J'}
      </div>

      {/* Message Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-medium text-gray-900">
            {isUser ? 'You' : 'JarvisX'}
          </span>
          {timestamp && (
            <span className="text-xs text-gray-500">
              {typeof timestamp === 'string' 
                ? new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                : timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          )}
        </div>
        {isEditing && isUser ? (
          <div className="space-y-2">
            <textarea
              value={editedContent}
              onChange={(e) => setEditedContent(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md text-gray-800 focus:outline-none focus:ring-2 focus:ring-primary resize-none"
              rows={4}
              autoFocus
            />
            <div className="flex gap-2">
              <button
                onClick={handleSaveEdit}
                className="px-3 py-1 text-sm bg-primary text-white rounded hover:bg-primary-hover"
              >
                Save
              </button>
              <button
                onClick={handleCancelEdit}
                className="px-3 py-1 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div className="text-gray-800 break-words">
            {role === 'assistant' ? (
              <MarkdownRenderer content={message} className="text-gray-800" />
            ) : (
              <div className="whitespace-pre-wrap">{message}</div>
            )}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      {!isEditing && (
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={handleCopy}
            className={cn(
              'flex-shrink-0 p-1.5 hover:bg-gray-200 rounded',
              'text-gray-500 hover:text-gray-700'
            )}
            title="Copy message"
          >
            {copied ? (
              <svg className="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            )}
          </button>
          {isUser && id && onEdit && (
            <button
              onClick={handleEdit}
              className="flex-shrink-0 p-1.5 hover:bg-gray-200 rounded text-gray-500 hover:text-gray-700"
              title="Edit message"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
          )}
          {isUser && id && onDelete && (
            <button
              onClick={handleDelete}
              className="flex-shrink-0 p-1.5 hover:bg-gray-200 rounded text-gray-500 hover:text-red-600"
              title="Delete message"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          )}
        </div>
      )}
    </div>
  )
}
