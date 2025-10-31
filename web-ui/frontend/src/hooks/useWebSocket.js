import { useState, useEffect, useRef, useCallback } from 'react'

/**
 * Custom hook for WebSocket connection
 * Handles connection, reconnection, and message handling
 */
export default function useWebSocket(url = null) {
  const [connectionStatus, setConnectionStatus] = useState('disconnected')
  const [lastMessage, setLastMessage] = useState(null)
  const [messageHistory, setMessageHistory] = useState([])
  
  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  const clientIdRef = useRef(`client-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`)
  
  // WebSocket URL (defaults to backend WebSocket endpoint)
  const wsUrl = url || `ws://localhost:8000/ws/${clientIdRef.current}`
  
  /**
   * Connect to WebSocket
   */
  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(wsUrl)
      
      ws.onopen = () => {
        console.log('✅ WebSocket connected')
        setConnectionStatus('connected')
        
        // Send ping to keep connection alive
        const pingInterval = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }))
          }
        }, 30000) // Ping every 30 seconds
        
        ws.pingInterval = pingInterval
      }
      
      ws.onmessage = (event) => {
        const message = event
        setLastMessage(message)
        setMessageHistory(prev => [...prev, message].slice(-100)) // Keep last 100 messages
      }
      
      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error)
        setConnectionStatus('error')
      }
      
      ws.onclose = () => {
        console.log('🔌 WebSocket disconnected')
        setConnectionStatus('disconnected')
        
        // Clear ping interval
        if (ws.pingInterval) {
          clearInterval(ws.pingInterval)
        }
        
        // Attempt reconnection after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('🔄 Attempting to reconnect...')
          connect()
        }, 3000)
      }
      
      wsRef.current = ws
    } catch (error) {
      console.error('Failed to connect:', error)
      setConnectionStatus('error')
    }
  }, [wsUrl])
  
  /**
   * Send message through WebSocket
   */
  const sendMessage = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
      return true
    } else {
      console.warn('⚠️  WebSocket not connected')
      return false
    }
  }, [])
  
  /**
   * Disconnect WebSocket
   */
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }, [])
  
  // Connect on mount
  useEffect(() => {
    connect()
    
    // Cleanup on unmount
    return () => {
      disconnect()
    }
  }, [connect, disconnect])
  
  return {
    connectionStatus,
    lastMessage,
    messageHistory,
    sendMessage,
    disconnect,
    reconnect: connect
  }
}

