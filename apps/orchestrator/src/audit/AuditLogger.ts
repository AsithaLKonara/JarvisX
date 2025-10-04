/**
 * Audit Logger for JarvisX Orchestrator
 * Handles logging of all system events for security and compliance
 */

import { DatabaseManager } from '../database/DatabaseManager';

export interface AuditEvent {
  task_id?: string;
  user_id?: string;
  action: string;
  details: any;
  ip_address?: string;
  user_agent?: string;
}

export interface ErrorEvent {
  error: string;
  stack?: string;
  url?: string;
  method?: string;
  user_id?: string;
}

export class AuditLogger {
  private dbManager: DatabaseManager;

  constructor(dbManager: DatabaseManager) {
    this.dbManager = dbManager;
  }

  /**
   * Log an audit event
   */
  public async logEvent(event: AuditEvent): Promise<string> {
    try {
      const logId = await this.dbManager.logAuditEvent({
        task_id: event.task_id,
        user_id: event.user_id,
        action: event.action,
        details: JSON.stringify(event.details),
        ip_address: event.ip_address,
        user_agent: event.user_agent
      });

      console.log(`📝 Audit log: ${event.action} by ${event.user_id || 'system'}`);
      return logId;

    } catch (error: any) {
      console.error('❌ Failed to log audit event:', error);
      // Fallback to console logging
      console.log(`AUDIT: ${JSON.stringify(event)}`);
      return 'console_fallback';
    }
  }

  /**
   * Log an error event
   */
  public async logError(errorEvent: ErrorEvent): Promise<string> {
    try {
      const logId = await this.dbManager.logAuditEvent({
        user_id: errorEvent.user_id,
        action: 'error',
        details: JSON.stringify({
          error: errorEvent.error,
          stack: errorEvent.stack,
          url: errorEvent.url,
          method: errorEvent.method
        }),
        ip_address: undefined,
        user_agent: undefined
      });

      console.error(`🚨 Error logged: ${errorEvent.error}`);
      return logId;

    } catch (error: any) {
      console.error('❌ Failed to log error event:', error);
      console.error(`ERROR: ${JSON.stringify(errorEvent)}`);
      return 'console_fallback';
    }
  }

  /**
   * Get audit logs with filtering
   */
  public async getLogs(filters: {
    task_id?: string;
    user_id?: string;
    action?: string;
    limit?: number;
    offset?: number;
  } = {}): Promise<any[]> {
    try {
      const {
        task_id,
        user_id,
        action,
        limit = 100,
        offset = 0
      } = filters;

      let sql = 'SELECT * FROM audit_logs WHERE 1=1';
      const params: any[] = [];

      if (task_id) {
        sql += ' AND task_id = ?';
        params.push(task_id);
      }

      if (user_id) {
        sql += ' AND user_id = ?';
        params.push(user_id);
      }

      if (action) {
        sql += ' AND action = ?';
        params.push(action);
      }

      sql += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?';
      params.push(limit, offset);

      const logs = await this.dbManager.all(sql, params);
      
      // Parse details for each log
      logs.forEach((log: any) => {
        try {
          log.details = JSON.parse(log.details);
        } catch {
          // Keep as string if parsing fails
        }
      });

      return logs;

    } catch (error: any) {
      console.error('❌ Failed to get audit logs:', error);
      return [];
    }
  }

  /**
   * Log task creation
   */
  public async logTaskCreated(taskId: string, userId: string, intent: string, stepsCount: number): Promise<void> {
    await this.logEvent({
      task_id: taskId,
      user_id: userId,
      action: 'task_created',
      details: {
        intent,
        steps_count: stepsCount
      }
    });
  }

  /**
   * Log task approval
   */
  public async logTaskApproved(taskId: string, userId: string, dryRun: boolean): Promise<void> {
    await this.logEvent({
      task_id: taskId,
      user_id: userId,
      action: 'task_approved',
      details: {
        dry_run: dryRun
      }
    });
  }

  /**
   * Log task rejection
   */
  public async logTaskRejected(taskId: string, userId: string, reason?: string): Promise<void> {
    await this.logEvent({
      task_id: taskId,
      user_id: userId,
      action: 'task_rejected',
      details: {
        reason
      }
    });
  }

  /**
   * Log task execution
   */
  public async logTaskExecuted(taskId: string, userId: string, result: any): Promise<void> {
    await this.logEvent({
      task_id: taskId,
      user_id: userId,
      action: 'task_executed',
      details: {
        success: result.success,
        duration: result.duration,
        errors_count: result.errors.length
      }
    });
  }

  /**
   * Log user authentication
   */
  public async logUserAuth(userId: string, action: 'login' | 'logout' | 'register', ipAddress?: string, userAgent?: string): Promise<void> {
    await this.logEvent({
      user_id: userId,
      action: `user_${action}`,
      details: {},
      ip_address: ipAddress,
      user_agent: userAgent
    });
  }

  /**
   * Log permission changes
   */
  public async logPermissionChange(userId: string, permissions: string[], changedBy: string): Promise<void> {
    await this.logEvent({
      user_id: userId,
      action: 'permissions_updated',
      details: {
        permissions,
        changed_by: changedBy
      }
    });
  }

  /**
   * Log executor execution
   */
  public async logExecutorExecution(taskId: string, executorName: string, action: string, input: any, output: any, duration: number, success: boolean): Promise<void> {
    await this.logEvent({
      task_id: taskId,
      action: 'executor_execution',
      details: {
        executor: executorName,
        executor_action: action,
        input,
        output,
        duration,
        success
      }
    });
  }
}
