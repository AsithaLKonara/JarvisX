/**
 * JarvisX Desktop Assistant Window
 * Siri-style AI interface with real-time action streaming and voice controls
 */

import React, { useEffect, useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Mic, 
  MicOff, 
  Monitor, 
  Settings, 
  Activity, 
  CheckCircle, 
  XCircle, 
  Clock,
  Play,
  Pause,
  Maximize2,
  Minimize2
} from 'lucide-react';

// Types
interface ActionEvent {
  sessionId: string;
  stepId: number;
  action: string;
  selector?: string;
  cursor?: { x: number; y: number };
  status: 'started' | 'completed' | 'failed' | 'queued';
  meta?: {
    screenshot?: string;
    log?: string;
    duration?: number;
  };
  timestamp: string;
}

interface WebSocketMessage {
  type: 'status' | 'action_event' | 'session_start' | 'session_end' | 'approval_request';
  data?: any;
  event?: ActionEvent;
  status?: 'idle' | 'listening' | 'streaming' | 'processing';
}

interface AssistantWindowProps {
  wsUrl: string;
  onClose?: () => void;
  isMinimized?: boolean;
  onToggleMinimize?: () => void;
}

export function AssistantWindow({ 
  wsUrl, 
  onClose, 
  isMinimized = false, 
  onToggleMinimize 
}: AssistantWindowProps) {
  // State
  const [status, setStatus] = useState<'idle' | 'listening' | 'streaming' | 'processing'>('idle');
  const [events, setEvents] = useState<ActionEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentSession, setCurrentSession] = useState<string | null>(null);
  const [pendingApprovals, setPendingApprovals] = useState<any[]>([]);
  const [cursorPosition, setCursorPosition] = useState<{ x: number; y: number } | null>(null);
  
  // Refs
  const wsRef = useRef<WebSocket | null>(null);
  const eventContainerRef = useRef<HTMLDivElement>(null);

  // WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log('🔌 Connected to JarvisX Orchestrator');
          setIsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            handleWebSocketMessage(message);
          } catch (error) {
            console.error('❌ Failed to parse WebSocket message:', error);
          }
        };

        ws.onclose = () => {
          console.log('🔌 WebSocket disconnected');
          setIsConnected(false);
          // Attempt to reconnect after 3 seconds
          setTimeout(connectWebSocket, 3000);
        };

        ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          setIsConnected(false);
        };
      } catch (error) {
        console.error('❌ Failed to connect to WebSocket:', error);
        setIsConnected(false);
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [wsUrl]);

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'status':
        setStatus(message.status || 'idle');
        break;
      
      case 'action_event':
        if (message.event) {
          setEvents(prev => [...prev, message.event!]);
          
          // Update cursor position if available
          if (message.event.cursor) {
            setCursorPosition(message.event.cursor);
          }
          
          // Auto-scroll to latest event
          setTimeout(() => {
            if (eventContainerRef.current) {
              eventContainerRef.current.scrollTop = eventContainerRef.current.scrollHeight;
            }
          }, 100);
        }
        break;
      
      case 'session_start':
        setCurrentSession(message.data?.sessionId || null);
        setEvents([]); // Clear previous events
        break;
      
      case 'session_end':
        setCurrentSession(null);
        setCursorPosition(null);
        break;
      
      case 'approval_request':
        setPendingApprovals(prev => [...prev, message.data]);
        break;
    }
  }, []);

  // Send WebSocket message
  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  // Voice control handlers
  const handleMicToggle = useCallback(() => {
    setIsMuted(!isMuted);
    sendMessage({
      type: 'voice_control',
      action: isMuted ? 'unmute' : 'mute'
    });
  }, [isMuted, sendMessage]);

  const handleStartSession = useCallback(() => {
    sendMessage({
      type: 'start_session',
      data: { screenShare: true, audioShare: false }
    });
  }, [sendMessage]);

  const handleEndSession = useCallback(() => {
    sendMessage({
      type: 'end_session',
      data: { sessionId: currentSession }
    });
  }, [sendMessage, currentSession]);

  // Approval handlers
  const handleApproval = useCallback((approvalId: string, approved: boolean) => {
    sendMessage({
      type: 'approval_response',
      data: { approvalId, approved }
    });
    
    setPendingApprovals(prev => prev.filter(a => a.id !== approvalId));
  }, [sendMessage]);

  // Quick actions
  const handleQuickAction = useCallback((action: string) => {
    sendMessage({
      type: 'quick_action',
      data: { action }
    });
  }, [sendMessage]);

  // Animation variants
  const containerVariants = {
    minimized: {
      width: 60,
      height: 60,
      borderRadius: 30,
    },
    expanded: {
      width: '100%',
      height: '100%',
      borderRadius: 20,
    }
  };

  const pulseVariants = {
    listening: {
      scale: [1, 1.2, 1],
      opacity: [0.7, 1, 0.7],
      transition: {
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut"
      }
    },
    idle: {
      scale: 1,
      opacity: 0.7
    }
  };

  if (isMinimized) {
    return (
      <motion.div
        className="fixed bottom-6 right-6 z-50"
        initial={false}
        animate={isMinimized ? "minimized" : "expanded"}
        variants={containerVariants}
      >
        <div className="assistant-minimized bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full shadow-2xl cursor-pointer flex items-center justify-center"
             onClick={onToggleMinimize}>
          <motion.div
            variants={pulseVariants}
            animate={status === 'listening' ? 'listening' : 'idle'}
          >
            <div className="avatar w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
              <span className="text-white text-sm font-bold">J</span>
            </div>
          </motion.div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      className="assistant-window fixed inset-4 z-50 bg-black/20 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/10"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <header className="flex items-center justify-between p-4 border-b border-white/10">
        <div className="flex items-center gap-3">
          <motion.div
            className="avatar w-12 h-12 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 flex items-center justify-center"
            variants={pulseVariants}
            animate={status === 'listening' ? 'listening' : 'idle'}
          >
            <span className="text-white text-lg font-bold">J</span>
          </motion.div>
          <div>
            <div className="text-white text-lg font-semibold">JarvisX</div>
            <div className="text-white/60 text-sm capitalize">{status}</div>
          </div>
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`} />
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={handleMicToggle}
            className={`p-2 rounded-lg transition-colors ${
              isMuted ? 'bg-red-500/20 text-red-400' : 'bg-white/10 text-white hover:bg-white/20'
            }`}
          >
            {isMuted ? <MicOff size={20} /> : <Mic size={20} />}
          </button>
          
          <button
            onClick={onToggleMinimize}
            className="p-2 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors"
          >
            <Minimize2 size={20} />
          </button>
          
          {onClose && (
            <button
              onClick={onClose}
              className="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
            >
              <XCircle size={20} />
            </button>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="flex h-full">
        {/* Left Sidebar - Quick Actions */}
        <aside className="w-64 p-4 border-r border-white/10 bg-black/10">
          <div className="space-y-4">
            <h3 className="text-white text-sm font-medium uppercase tracking-wide">Quick Actions</h3>
            
            <div className="space-y-2">
              <button
                onClick={() => handleQuickAction('open_ide')}
                className="w-full p-3 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors flex items-center gap-3"
              >
                <Monitor size={16} />
                <span className="text-sm">Open IDE</span>
              </button>
              
              <button
                onClick={() => handleQuickAction('run_tests')}
                className="w-full p-3 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors flex items-center gap-3"
              >
                <Activity size={16} />
                <span className="text-sm">Run Tests</span>
              </button>
              
              <button
                onClick={() => handleQuickAction('git_status')}
                className="w-full p-3 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors flex items-center gap-3"
              >
                <Settings size={16} />
                <span className="text-sm">Git Status</span>
              </button>
            </div>

            {/* Session Controls */}
            <div className="pt-4 border-t border-white/10">
              <h4 className="text-white text-sm font-medium mb-2">Session</h4>
              {currentSession ? (
                <button
                  onClick={handleEndSession}
                  className="w-full p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors flex items-center gap-2"
                >
                  <Pause size={14} />
                  <span className="text-sm">End Session</span>
                </button>
              ) : (
                <button
                  onClick={handleStartSession}
                  className="w-full p-2 rounded-lg bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors flex items-center gap-2"
                >
                  <Play size={14} />
                  <span className="text-sm">Start Session</span>
                </button>
              )}
            </div>

            {/* Pending Approvals */}
            {pendingApprovals.length > 0 && (
              <div className="pt-4 border-t border-white/10">
                <h4 className="text-white text-sm font-medium mb-2">Pending Approvals</h4>
                <div className="space-y-2">
                  {pendingApprovals.map((approval) => (
                    <div key={approval.id} className="p-2 rounded-lg bg-yellow-500/20 border border-yellow-500/30">
                      <div className="text-yellow-400 text-xs mb-1">{approval.action}</div>
                      <div className="flex gap-1">
                        <button
                          onClick={() => handleApproval(approval.id, true)}
                          className="flex-1 px-2 py-1 rounded text-xs bg-green-500/20 text-green-400 hover:bg-green-500/30"
                        >
                          ✓
                        </button>
                        <button
                          onClick={() => handleApproval(approval.id, false)}
                          className="flex-1 px-2 py-1 rounded text-xs bg-red-500/20 text-red-400 hover:bg-red-500/30"
                        >
                          ✗
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </aside>

        {/* Center - Action Stream */}
        <section className="flex-1 p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-white text-lg font-semibold">Live Action Stream</h3>
            <div className="text-white/60 text-sm">
              {events.length} events
            </div>
          </div>
          
          <div
            ref={eventContainerRef}
            className="action-stream h-96 overflow-y-auto space-y-2 pr-2"
          >
            <AnimatePresence>
              {events.map((event, index) => (
                <motion.div
                  key={`${event.sessionId}-${event.stepId}`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: index * 0.1 }}
                  className={`p-3 rounded-lg border transition-colors ${
                    event.status === 'completed' 
                      ? 'bg-green-500/10 border-green-500/30' 
                      : event.status === 'failed'
                      ? 'bg-red-500/10 border-red-500/30'
                      : event.status === 'started'
                      ? 'bg-blue-500/10 border-blue-500/30'
                      : 'bg-white/5 border-white/10'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="flex-shrink-0">
                      {event.status === 'completed' && <CheckCircle size={16} className="text-green-400" />}
                      {event.status === 'failed' && <XCircle size={16} className="text-red-400" />}
                      {event.status === 'started' && <Activity size={16} className="text-blue-400" />}
                      {event.status === 'queued' && <Clock size={16} className="text-yellow-400" />}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="text-white text-sm font-medium truncate">
                        {event.action}
                      </div>
                      <div className="text-white/60 text-xs">
                        Step {event.stepId} • {new Date(event.timestamp).toLocaleTimeString()}
                      </div>
                      {event.meta?.log && (
                        <div className="text-white/40 text-xs mt-1 font-mono">
                          {event.meta.log}
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
            
            {events.length === 0 && (
              <div className="text-center text-white/40 py-8">
                <Activity size={48} className="mx-auto mb-4 opacity-50" />
                <div>No actions yet. Start a session to see live activity.</div>
              </div>
            )}
          </div>
        </section>

        {/* Right Sidebar - Context */}
        <aside className="w-80 p-4 border-l border-white/10 bg-black/10">
          <div className="space-y-4">
            <h3 className="text-white text-sm font-medium uppercase tracking-wide">Context</h3>
            
            {/* Project Info */}
            <div className="p-3 rounded-lg bg-white/5 border border-white/10">
              <h4 className="text-white text-sm font-medium mb-2">Current Project</h4>
              <div className="text-white/60 text-xs">
                {currentSession ? `Session: ${currentSession.slice(0, 8)}...` : 'No active session'}
              </div>
            </div>

            {/* System Metrics */}
            <div className="p-3 rounded-lg bg-white/5 border border-white/10">
              <h4 className="text-white text-sm font-medium mb-2">System</h4>
              <div className="space-y-1 text-xs">
                <div className="flex justify-between text-white/60">
                  <span>Status:</span>
                  <span className="text-green-400">Active</span>
                </div>
                <div className="flex justify-between text-white/60">
                  <span>Uptime:</span>
                  <span>2h 34m</span>
                </div>
                <div className="flex justify-between text-white/60">
                  <span>Tasks:</span>
                  <span>{events.length}</span>
                </div>
              </div>
            </div>

            {/* Voice Status */}
            <div className="p-3 rounded-lg bg-white/5 border border-white/10">
              <h4 className="text-white text-sm font-medium mb-2">Voice</h4>
              <div className="space-y-1 text-xs">
                <div className="flex justify-between text-white/60">
                  <span>Status:</span>
                  <span className={isMuted ? 'text-red-400' : 'text-green-400'}>
                    {isMuted ? 'Muted' : 'Active'}
                  </span>
                </div>
                <div className="flex justify-between text-white/60">
                  <span>Language:</span>
                  <span>Sinhala/EN</span>
                </div>
              </div>
            </div>
          </div>
        </aside>
      </main>

      {/* Cursor Overlay (for screen streaming) */}
      {cursorPosition && (
        <motion.div
          className="fixed pointer-events-none z-50"
          style={{
            left: cursorPosition.x,
            top: cursorPosition.y,
          }}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          exit={{ scale: 0 }}
        >
          <div className="w-4 h-4 rounded-full bg-blue-500 shadow-lg border-2 border-white" />
        </motion.div>
      )}
    </motion.div>
  );
}

// CSS for the assistant window (to be added to global styles)
const assistantStyles = `
.assistant-window {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.assistant-minimized {
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

.action-stream::-webkit-scrollbar {
  width: 4px;
}

.action-stream::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.action-stream::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
}

.action-stream::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}
`;

export default AssistantWindow;
