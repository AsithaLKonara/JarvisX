'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import Button from '../ui/Button'
import { cn } from '@/lib/utils'

interface Conversation {
  id: string
  title: string
  lastMessage?: string
  updatedAt: string
}

interface SidebarProps {
  conversations?: Conversation[]
  currentConversationId?: string
  onNewChat: () => void
  onSelectConversation: (id: string) => void
  onDeleteConversation?: (id: string) => void
  onRenameConversation?: (id: string, newTitle: string) => void
  userName?: string
  userEmail?: string
}

// Icon components
function PlusIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
    </svg>
  )
}

function MessageSquareIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
  )
}

function SettingsIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  )
}

function LogOutIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
    </svg>
  )
}

function SearchIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  )
}

function EditIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
    </svg>
  )
}

function TrashIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
    </svg>
  )
}

export default function Sidebar({
  conversations = [],
  currentConversationId,
  onNewChat,
  onSelectConversation,
  onDeleteConversation,
  onRenameConversation,
  userName,
  userEmail,
}: SidebarProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editingTitle, setEditingTitle] = useState('')
  const [hoveredId, setHoveredId] = useState<string | null>(null)

  const filteredConversations = conversations.filter((conv) =>
    conv.title.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleRename = (id: string, currentTitle: string) => {
    setEditingId(id)
    setEditingTitle(currentTitle)
  }

  const handleSaveRename = (id: string) => {
    if (onRenameConversation && editingTitle.trim()) {
      onRenameConversation(id, editingTitle.trim())
    }
    setEditingId(null)
    setEditingTitle('')
  }

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (onDeleteConversation && confirm('Are you sure you want to delete this conversation?')) {
      onDeleteConversation(id)
    }
  }

  return (
    <div className="flex flex-col h-full bg-[#202123] text-white w-64 border-r border-gray-700">
      {/* New Chat Button */}
      <div className="p-3">
        <Button
          onClick={onNewChat}
          variant="secondary"
          className="w-full bg-white/5 hover:bg-white/10 border-white/10 text-white justify-start"
        >
          <PlusIcon className="w-4 h-4 mr-2" />
          New chat
        </Button>
      </div>

      {/* Search */}
      <div className="px-3 mb-2">
        <div className="relative">
          <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-md text-sm text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-white/20"
          />
        </div>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto px-2">
        {filteredConversations.length === 0 ? (
          <div className="text-center text-gray-400 text-sm py-8">
            {searchQuery ? 'No conversations found' : 'No conversations yet'}
          </div>
        ) : (
          <div className="space-y-1">
            {filteredConversations.map((conv) => (
              <div
                key={conv.id}
                className={cn(
                  'group relative flex items-center gap-2 p-3 rounded-lg cursor-pointer transition-colors',
                  currentConversationId === conv.id
                    ? 'bg-white/10'
                    : 'hover:bg-white/5'
                )}
                onClick={() => onSelectConversation(conv.id)}
                onMouseEnter={() => setHoveredId(conv.id)}
                onMouseLeave={() => setHoveredId(null)}
              >
                <MessageSquareIcon className="w-4 h-4 text-gray-400 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  {editingId === conv.id ? (
                    <input
                      type="text"
                      value={editingTitle}
                      onChange={(e) => setEditingTitle(e.target.value)}
                      onBlur={() => handleSaveRename(conv.id)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleSaveRename(conv.id)
                        if (e.key === 'Escape') setEditingId(null)
                      }}
                      onClick={(e) => e.stopPropagation()}
                      className="w-full bg-white/10 text-white text-sm px-2 py-1 rounded focus:outline-none focus:ring-1 focus:ring-white/30"
                      autoFocus
                    />
                  ) : (
                    <div className="truncate text-sm">{conv.title}</div>
                  )}
                  {conv.lastMessage && (
                    <div className="truncate text-xs text-gray-400 mt-0.5">
                      {conv.lastMessage}
                    </div>
                  )}
                </div>
                {hoveredId === conv.id && editingId !== conv.id && (
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    {onRenameConversation && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleRename(conv.id, conv.title)
                        }}
                        className="p-1 hover:bg-white/10 rounded"
                        title="Rename"
                      >
                        <EditIcon className="w-3.5 h-3.5" />
                      </button>
                    )}
                    {onDeleteConversation && (
                      <button
                        onClick={(e) => handleDelete(conv.id, e)}
                        className="p-1 hover:bg-white/10 rounded"
                        title="Delete"
                      >
                        <TrashIcon className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* User Menu */}
      <div className="border-t border-gray-700 p-3">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white text-sm font-medium">
            {userName?.[0]?.toUpperCase() || userEmail?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium truncate">{userName || 'User'}</div>
            <div className="text-xs text-gray-400 truncate">{userEmail}</div>
          </div>
        </div>
        <div className="flex gap-2">
          <Link href="/settings">
            <Button variant="ghost" size="sm" className="flex-1 justify-start text-gray-300 hover:text-white hover:bg-white/5">
              <SettingsIcon className="w-4 h-4 mr-2" />
              Settings
            </Button>
          </Link>
          <Link href="/logout">
            <Button variant="ghost" size="sm" className="text-gray-300 hover:text-white hover:bg-white/5">
              <LogOutIcon className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
