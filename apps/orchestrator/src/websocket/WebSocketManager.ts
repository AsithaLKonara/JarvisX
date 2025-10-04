/**
 * WebSocket Manager for JarvisX Orchestrator
 * Handles real-time communication with desktop and mobile clients
 */

import { WebSocketServer, WebSocket } from 'ws';
import { TaskManager } from '../tasks/TaskManager';
import { IncomingMessage } from 'http';

export interface WebSocketClient {
  id: string;
  ws: WebSocket;
  user_id?: string;
  client_type: 'desktop' | 'mobile' | 'unknown';
  connected_at: Date;
  last_ping: Date;
}

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

export class WebSocketManager {
  private wss: WebSocketServer;
  private taskManager: TaskManager;
  private clients: Map<string, WebSocketClient> = new Map();
  private heartbeatInterval: NodeJS.Timeout | null = null;

  constructor(wss: WebSocketServer, taskManager: TaskManager) {
    this.wss = wss;
    this.taskManager = taskManager;
    this.startHeartbeat();
  }

  /**
   * Handle new WebSocket connection
   */
  public handleConnection(ws: WebSocket, req: IncomingMessage): void {
    const clientId = this.generateClientId();
    const client: WebSocketClient = {
      id: clientId,
      ws,
      client_type: 'unknown',
      connected_at: new Date(),
      last_ping: new Date()
    };

    this.clients.set(clientId, client);
    console.log(`🔌 WebSocket client connected: ${clientId}`);

    // Send welcome message
    this.sendToClient(clientId, {
      type: 'welcome',
      data: {
        client_id: clientId,
        server_time: new Date().toISOString()
      }
    });

    // Handle messages from client
    ws.on('message', (data: Buffer) => {
      try {
        const message = JSON.parse(data.toString()) as WebSocketMessage;
        this.handleClientMessage(clientId, message);
      } catch (error) {
        console.error(`❌ Invalid WebSocket message from ${clientId}:`, error);
        this.sendError(clientId, 'Invalid message format');
      }
    });

    // Handle client disconnect
    ws.on('close', () => {
      console.log(`🔌 WebSocket client disconnected: ${clientId}`);
      this.clients.delete(clientId);
    });

    // Handle errors
    ws.on('error', (error) => {
      console.error(`❌ WebSocket error for client ${clientId}:`, error);
      this.clients.delete(clientId);
    });

    // Handle pong responses
    ws.on('pong', () => {
      const client = this.clients.get(clientId);
      if (client) {
        client.last_ping = new Date();
      }
    });
  }

  /**
   * Handle message from client
   */
  private async handleClientMessage(clientId: string, message: WebSocketMessage): Promise<void> {
    const client = this.clients.get(clientId);
    if (!client) {
      return;
    }

    try {
      console.log(`📨 WebSocket message from ${clientId}: ${message.type}`);

      switch (message.type) {
        case 'authenticate':
          await this.handleAuthentication(clientId, message.data);
          break;
        
        case 'subscribe_tasks':
          await this.handleTaskSubscription(clientId, message.data);
          break;
        
        case 'approve_task':
          await this.handleTaskApproval(clientId, message.data);
          break;
        
        case 'reject_task':
          await this.handleTaskRejection(clientId, message.data);
          break;
        
        case 'ping':
          this.handlePing(clientId);
          break;
        
        case 'get_status':
          await this.handleStatusRequest(clientId);
          break;
        
        default:
          this.sendError(clientId, `Unknown message type: ${message.type}`);
      }

    } catch (error: any) {
      console.error(`❌ Error handling message from ${clientId}:`, error);
      this.sendError(clientId, error.message);
    }
  }

  /**
   * Handle client authentication
   */
  private async handleAuthentication(clientId: string, data: any): Promise<void> {
    const { token, client_type } = data;
    
    // In a real implementation, you'd verify the JWT token here
    // For now, we'll just accept any token
    if (token) {
      const client = this.clients.get(clientId);
      if (client) {
        client.user_id = 'authenticated_user'; // Extract from token
        client.client_type = client_type || 'unknown';
        
        this.sendToClient(clientId, {
          type: 'authenticated',
          data: {
            user_id: client.user_id,
            client_type: client.client_type
          }
        });
      }
    } else {
      this.sendError(clientId, 'Authentication token required');
    }
  }

  /**
   * Handle task subscription
   */
  private async handleTaskSubscription(clientId: string, data: any): Promise<void> {
    const { user_id, filters } = data;
    
    try {
      // Get user's tasks
      const tasks = await this.taskManager.getTasksForUser(user_id, 50);
      
      this.sendToClient(clientId, {
        type: 'tasks_update',
        data: {
          tasks,
          count: tasks.length
        }
      });

    } catch (error: any) {
      this.sendError(clientId, `Failed to get tasks: ${error.message}`);
    }
  }

  /**
   * Handle task approval
   */
  private async handleTaskApproval(clientId: string, data: any): Promise<void> {
    const { task_id, dry_run } = data;
    
    try {
      const result = await this.taskManager.approveTask(task_id, 'websocket_user', dry_run);
      
      this.sendToClient(clientId, {
        type: 'task_approved',
        data: {
          task_id,
          result,
          dry_run
        }
      });

      // Broadcast to all clients
      this.broadcast({
        type: 'task_status_changed',
        data: {
          task_id,
          status: 'approved',
          approved_by: 'websocket_user'
        }
      });

    } catch (error: any) {
      this.sendError(clientId, `Failed to approve task: ${error.message}`);
    }
  }

  /**
   * Handle task rejection
   */
  private async handleTaskRejection(clientId: string, data: any): Promise<void> {
    const { task_id, reason } = data;
    
    try {
      await this.taskManager.rejectTask(task_id, 'websocket_user', reason);
      
      this.sendToClient(clientId, {
        type: 'task_rejected',
        data: {
          task_id,
          reason
        }
      });

      // Broadcast to all clients
      this.broadcast({
        type: 'task_status_changed',
        data: {
          task_id,
          status: 'rejected',
          rejected_by: 'websocket_user'
        }
      });

    } catch (error: any) {
      this.sendError(clientId, `Failed to reject task: ${error.message}`);
    }
  }

  /**
   * Handle ping from client
   */
  private handlePing(clientId: string): void {
    const client = this.clients.get(clientId);
    if (client) {
      client.last_ping = new Date();
    }
    
    this.sendToClient(clientId, {
      type: 'pong',
      data: {
        server_time: new Date().toISOString()
      }
    });
  }

  /**
   * Handle status request
   */
  private async handleStatusRequest(clientId: string): Promise<void> {
    const status = {
      connected_clients: this.clients.size,
      server_time: new Date().toISOString(),
      uptime: process.uptime()
    };

    this.sendToClient(clientId, {
      type: 'status',
      data: status
    });
  }

  /**
   * Send message to specific client
   */
  public sendToClient(clientId: string, message: WebSocketMessage): void {
    const client = this.clients.get(clientId);
    if (client && client.ws.readyState === WebSocket.OPEN) {
      try {
        client.ws.send(JSON.stringify(message));
      } catch (error) {
        console.error(`❌ Failed to send message to ${clientId}:`, error);
        this.clients.delete(clientId);
      }
    }
  }

  /**
   * Broadcast message to all connected clients
   */
  public broadcast(message: WebSocketMessage): void {
    console.log(`📢 Broadcasting message to ${this.clients.size} clients: ${message.type}`);
    
    this.clients.forEach((client, clientId) => {
      this.sendToClient(clientId, message);
    });
  }

  /**
   * Broadcast message to specific user's clients
   */
  public broadcastToUser(userId: string, message: WebSocketMessage): void {
    this.clients.forEach((client, clientId) => {
      if (client.user_id === userId) {
        this.sendToClient(clientId, message);
      }
    });
  }

  /**
   * Send error message to client
   */
  private sendError(clientId: string, error: string): void {
    this.sendToClient(clientId, {
      type: 'error',
      data: {
        error,
        timestamp: new Date().toISOString()
      }
    });
  }

  /**
   * Generate unique client ID
   */
  private generateClientId(): string {
    return `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Start heartbeat to keep connections alive
   */
  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      this.clients.forEach((client, clientId) => {
        if (client.ws.readyState === WebSocket.OPEN) {
          // Check if client is responsive
          const timeSinceLastPing = Date.now() - client.last_ping.getTime();
          if (timeSinceLastPing > 60000) { // 60 seconds
            console.log(`🔌 Disconnecting unresponsive client: ${clientId}`);
            client.ws.terminate();
            this.clients.delete(clientId);
          } else {
            // Send ping
            client.ws.ping();
          }
        } else {
          // Remove disconnected clients
          this.clients.delete(clientId);
        }
      });
    }, 30000); // Every 30 seconds
  }

  /**
   * Stop heartbeat
   */
  public stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  /**
   * Get connected clients count
   */
  public getConnectedClientsCount(): number {
    return this.clients.size;
  }

  /**
   * Get connected clients info
   */
  public getConnectedClients(): WebSocketClient[] {
    return Array.from(this.clients.values());
  }

  /**
   * Notify clients about new task
   */
  public notifyNewTask(task: any): void {
    this.broadcast({
      type: 'new_task',
      data: {
        task,
        timestamp: new Date().toISOString()
      }
    });
  }

  /**
   * Notify clients about task status change
   */
  public notifyTaskStatusChange(taskId: string, status: string, details?: any): void {
    this.broadcast({
      type: 'task_status_changed',
      data: {
        task_id: taskId,
        status,
        details,
        timestamp: new Date().toISOString()
      }
    });
  }
}
