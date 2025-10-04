/**
 * Task Manager for JarvisX Orchestrator
 * Handles task lifecycle, planning, approval, and execution
 */

import { DatabaseManager } from '../database/DatabaseManager';
import { AuditLogger } from '../audit/AuditLogger';
import { PermissionManager } from '../security/PermissionManager';
import { LLMService } from '../ai/LLMService';
import { ExecutorRegistry } from '../executors/ExecutorRegistry';
import { Task } from '../../../shared/schemas';

export interface TaskExecutionResult {
  success: boolean;
  results: any[];
  errors: string[];
  duration: number;
}

export class TaskManager {
  private dbManager: DatabaseManager;
  private auditLogger: AuditLogger;
  private permissionManager: PermissionManager;
  private llmService: LLMService;
  private executorRegistry: ExecutorRegistry;

  constructor(
    dbManager: DatabaseManager,
    auditLogger: AuditLogger,
    permissionManager: PermissionManager,
    llmService: LLMService,
    executorRegistry: ExecutorRegistry
  ) {
    this.dbManager = dbManager;
    this.auditLogger = auditLogger;
    this.permissionManager = permissionManager;
    this.llmService = llmService;
    this.executorRegistry = executorRegistry;
  }

  /**
   * Plan a task using LLM service
   */
  public async planTask(userText: string, userId: string, context?: any): Promise<{ success: boolean; data?: Task; error?: string }> {
    try {
      console.log(`🧠 Planning task for user ${userId}: "${userText.substring(0, 100)}..."`);

      // Get user permissions
      const userPermissions = await this.permissionManager.getUserPermissions(userId);

      // Plan task using LLM
      const planResult = await this.llmService.planTask(userText, {
        permissions: userPermissions,
        preferences: context?.preferences || {}
      });

      if (!planResult.success) {
        return {
          success: false,
          error: planResult.error
        };
      }

      return {
        success: true,
        data: planResult.data
      };

    } catch (error: any) {
      console.error('❌ Task planning failed:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Create a new task in the database
   */
  public async createTask(taskData: Task, userId: string): Promise<string> {
    const taskId = await this.dbManager.createTask({
      user_id: userId,
      status: 'pending',
      intent: taskData.intent,
      user_text: taskData.user_text || '',
      task_data: JSON.stringify(taskData)
    });

    console.log(`📝 Created task ${taskId}: ${taskData.intent}`);
    return taskId;
  }

  /**
   * Get a task by ID
   */
  public async getTask(taskId: string): Promise<any> {
    const task = await this.dbManager.getTask(taskId);
    if (task) {
      try {
        task.task_data = JSON.parse(task.task_data);
      } catch {
        // Keep as string if parsing fails
      }
    }
    return task;
  }

  /**
   * Get tasks for a specific user
   */
  public async getTasksForUser(userId: string, limit: number = 50, status?: string): Promise<any[]> {
    let sql = 'SELECT * FROM tasks WHERE user_id = ?';
    const params: any[] = [userId];

    if (status) {
      sql += ' AND status = ?';
      params.push(status);
    }

    sql += ' ORDER BY created_at DESC LIMIT ?';
    params.push(limit);

    const tasks = await this.dbManager.all(sql, params);
    
    // Parse task_data for each task
    tasks.forEach((task: any) => {
      try {
        task.task_data = JSON.parse(task.task_data);
      } catch {
        // Keep as string if parsing fails
      }
    });

    return tasks;
  }

  /**
   * Get pending tasks
   */
  public async getPendingTasks(limit: number = 100): Promise<any[]> {
    const tasks = await this.dbManager.getPendingTasks(limit);
    
    // Parse task_data for each task
    tasks.forEach((task: any) => {
      try {
        task.task_data = JSON.parse(task.task_data);
      } catch {
        // Keep as string if parsing fails
      }
    });

    return tasks;
  }

  /**
   * Approve a task
   */
  public async approveTask(taskId: string, approvedBy: string, dryRun: boolean = false): Promise<TaskExecutionResult> {
    try {
      const task = await this.getTask(taskId);
      if (!task) {
        throw new Error('Task not found');
      }

      if (task.status !== 'pending') {
        throw new Error(`Task is not in pending status: ${task.status}`);
      }

      // Update task status to approved
      await this.dbManager.updateTaskStatus(taskId, 'approved', approvedBy);

      console.log(`✅ Approved task ${taskId} by user ${approvedBy}`);

      // If dry run, return the planned execution steps
      if (dryRun) {
        return {
          success: true,
          results: task.task_data.steps.map((step: any) => ({
            step_id: step.step_id,
            action: step.action,
            tool: step.tool,
            params: step.params,
            dry_run: true
          })),
          errors: [],
          duration: 0
        };
      }

      // Execute the task
      return await this.executeTask(taskId, approvedBy, false);

    } catch (error: any) {
      console.error('❌ Task approval failed:', error);
      
      // Update task status to failed
      await this.dbManager.updateTaskStatus(taskId, 'failed', undefined, error.message);
      
      throw error;
    }
  }

  /**
   * Reject a task
   */
  public async rejectTask(taskId: string, rejectedBy: string, reason?: string): Promise<void> {
    const task = await this.getTask(taskId);
    if (!task) {
      throw new Error('Task not found');
    }

    if (task.status !== 'pending') {
      throw new Error(`Task is not in pending status: ${task.status}`);
    }

    await this.dbManager.updateTaskStatus(taskId, 'rejected', rejectedBy, reason);
    console.log(`❌ Rejected task ${taskId} by user ${rejectedBy}: ${reason}`);
  }

  /**
   * Execute a task
   */
  public async executeTask(taskId: string, executedBy: string, dryRun: boolean = false): Promise<TaskExecutionResult> {
    const startTime = Date.now();
    const results: any[] = [];
    const errors: string[] = [];

    try {
      const task = await this.getTask(taskId);
      if (!task) {
        throw new Error('Task not found');
      }

      if (task.status !== 'approved') {
        throw new Error(`Task must be approved before execution: ${task.status}`);
      }

      // Update status to executing
      await this.dbManager.updateTaskStatus(taskId, 'executing');

      console.log(`🚀 Executing task ${taskId} (dry_run: ${dryRun})`);

      const taskData = task.task_data as Task;

      // Execute each step
      for (const step of taskData.steps) {
        try {
          console.log(`  📋 Executing step ${step.step_id}: ${step.action}`);

          // Check permissions for this step
          if (step.permissions && step.permissions.length > 0) {
            const hasPermission = await this.permissionManager.checkUserPermissions(
              executedBy,
              step.permissions
            );

            if (!hasPermission) {
              const error = `Insufficient permissions for step ${step.step_id}: ${step.permissions.join(', ')}`;
              errors.push(error);
              console.error(`  ❌ ${error}`);
              continue;
            }
          }

          // Execute step using appropriate executor
          const executor = this.executorRegistry.getExecutor(step.tool);
          if (!executor) {
            const error = `No executor found for tool: ${step.tool}`;
            errors.push(error);
            console.error(`  ❌ ${error}`);
            continue;
          }

          const stepResult = await executor.execute(step, dryRun);
          results.push({
            step_id: step.step_id,
            action: step.action,
            tool: step.tool,
            result: stepResult,
            dry_run: dryRun
          });

          console.log(`  ✅ Step ${step.step_id} completed`);

        } catch (stepError: any) {
          const error = `Step ${step.step_id} failed: ${stepError.message}`;
          errors.push(error);
          console.error(`  ❌ ${error}`);
        }
      }

      const duration = Date.now() - startTime;
      const success = errors.length === 0;

      // Update task status
      await this.dbManager.updateTaskStatus(
        taskId,
        success ? 'completed' : 'failed',
        undefined,
        success ? undefined : errors.join('; ')
      );

      console.log(`🏁 Task ${taskId} execution completed in ${duration}ms (success: ${success})`);

      return {
        success,
        results,
        errors,
        duration
      };

    } catch (error: any) {
      const duration = Date.now() - startTime;
      console.error(`❌ Task execution failed: ${error.message}`);

      // Update task status to failed
      await this.dbManager.updateTaskStatus(taskId, 'failed', undefined, error.message);

      return {
        success: false,
        results,
        errors: [...errors, error.message],
        duration
      };
    }
  }

  /**
   * Get task execution logs
   */
  public async getTaskLogs(taskId: string): Promise<any[]> {
    return await this.dbManager.all(
      'SELECT * FROM executor_logs WHERE task_id = ? ORDER BY timestamp ASC',
      [taskId]
    );
  }
}
