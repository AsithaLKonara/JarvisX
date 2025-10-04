/**
 * Task management routes for JarvisX Orchestrator
 */

import express from 'express';
import { v4 as uuidv4 } from 'uuid';

const router = express.Router();

// POST /tasks - Create a new task
router.post('/', async (req, res) => {
  try {
    const { text, user_id = 'default_user', context } = req.body;

    if (!text || typeof text !== 'string') {
      return res.status(400).json({
        error: 'Text parameter is required and must be a string'
      });
    }

    console.log(`📝 Creating task for user ${user_id}: "${text.substring(0, 100)}..."`);

    // Use task manager to create and plan task
    const taskManager = req.context.taskManager;
    const auditLogger = req.context.auditLogger;

    // Plan the task using LLM
    const planResult = await taskManager.planTask(text, user_id, context);
    
    if (!planResult.success) {
      await auditLogger.logError({
        error: planResult.error,
        user_id,
        action: 'task_planning_failed',
        details: { text, context }
      });

      return res.status(400).json({
        error: 'Task planning failed',
        details: planResult.error
      });
    }

    // Create task record
    const taskId = await taskManager.createTask(planResult.data, user_id);

    // Log audit event
    await auditLogger.logEvent({
      task_id: taskId,
      user_id,
      action: 'task_created',
      details: { intent: planResult.data.intent, steps_count: planResult.data.steps.length }
    });

    res.status(201).json({
      success: true,
      task_id: taskId,
      task: planResult.data,
      status: 'pending'
    });

  } catch (error: any) {
    console.error('❌ Task creation failed:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

// GET /tasks - Get tasks for user
router.get('/', async (req, res) => {
  try {
    const { user_id = 'default_user', limit = 50, status } = req.query;
    const taskManager = req.context.taskManager;

    const tasks = await taskManager.getTasksForUser(
      user_id as string,
      parseInt(limit as string),
      status as string
    );

    res.json({
      success: true,
      tasks,
      count: tasks.length
    });

  } catch (error: any) {
    console.error('❌ Failed to get tasks:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

// GET /tasks/:id - Get specific task
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const taskManager = req.context.taskManager;

    const task = await taskManager.getTask(id);
    
    if (!task) {
      return res.status(404).json({
        error: 'Task not found'
      });
    }

    res.json({
      success: true,
      task
    });

  } catch (error: any) {
    console.error('❌ Failed to get task:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

// PATCH /tasks/:id/approve - Approve a task
router.patch('/:id/approve', async (req, res) => {
  try {
    const { id } = req.params;
    const { approved_by = 'default_user', dry_run = false } = req.body;

    const taskManager = req.context.taskManager;
    const auditLogger = req.context.auditLogger;

    // Get task first
    const task = await taskManager.getTask(id);
    if (!task) {
      return res.status(404).json({
        error: 'Task not found'
      });
    }

    if (task.status !== 'pending') {
      return res.status(400).json({
        error: 'Task is not in pending status',
        current_status: task.status
      });
    }

    console.log(`✅ Approving task ${id} by user ${approved_by}`);

    // Approve the task
    const result = await taskManager.approveTask(id, approved_by, dry_run);

    // Log audit event
    await auditLogger.logEvent({
      task_id: id,
      user_id: approved_by,
      action: 'task_approved',
      details: { dry_run, result }
    });

    res.json({
      success: true,
      task_id: id,
      status: 'approved',
      result
    });

  } catch (error: any) {
    console.error('❌ Task approval failed:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

// PATCH /tasks/:id/reject - Reject a task
router.patch('/:id/reject', async (req, res) => {
  try {
    const { id } = req.params;
    const { rejected_by = 'default_user', reason } = req.body;

    const taskManager = req.context.taskManager;
    const auditLogger = req.context.auditLogger;

    // Get task first
    const task = await taskManager.getTask(id);
    if (!task) {
      return res.status(404).json({
        error: 'Task not found'
      });
    }

    if (task.status !== 'pending') {
      return res.status(400).json({
        error: 'Task is not in pending status',
        current_status: task.status
      });
    }

    console.log(`❌ Rejecting task ${id} by user ${rejected_by}: ${reason}`);

    // Reject the task
    await taskManager.rejectTask(id, rejected_by, reason);

    // Log audit event
    await auditLogger.logEvent({
      task_id: id,
      user_id: rejected_by,
      action: 'task_rejected',
      details: { reason }
    });

    res.json({
      success: true,
      task_id: id,
      status: 'rejected',
      reason
    });

  } catch (error: any) {
    console.error('❌ Task rejection failed:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

// POST /tasks/:id/execute - Execute a task (for testing)
router.post('/:id/execute', async (req, res) => {
  try {
    const { id } = req.params;
    const { user_id = 'default_user', dry_run = false } = req.body;

    const taskManager = req.context.taskManager;
    const auditLogger = req.context.auditLogger;

    // Get task first
    const task = await taskManager.getTask(id);
    if (!task) {
      return res.status(404).json({
        error: 'Task not found'
      });
    }

    if (task.status !== 'approved') {
      return res.status(400).json({
        error: 'Task must be approved before execution',
        current_status: task.status
      });
    }

    console.log(`🚀 Executing task ${id} (dry_run: ${dry_run})`);

    // Execute the task
    const result = await taskManager.executeTask(id, user_id, dry_run);

    // Log audit event
    await auditLogger.logEvent({
      task_id: id,
      user_id,
      action: 'task_executed',
      details: { dry_run, result }
    });

    res.json({
      success: true,
      task_id: id,
      status: 'executed',
      result
    });

  } catch (error: any) {
    console.error('❌ Task execution failed:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

// GET /tasks/pending - Get pending tasks (admin endpoint)
router.get('/pending/list', async (req, res) => {
  try {
    const { limit = 100 } = req.query;
    const taskManager = req.context.taskManager;

    const tasks = await taskManager.getPendingTasks(parseInt(limit as string));

    res.json({
      success: true,
      tasks,
      count: tasks.length
    });

  } catch (error: any) {
    console.error('❌ Failed to get pending tasks:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

export default router;
