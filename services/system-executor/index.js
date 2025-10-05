/**
 * JarvisX System Executor
 * Safe system command execution with whitelist validation
 */

const express = require('express');
const cors = require('cors');
const { exec, spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8009;

// Middleware
app.use(cors());
app.use(express.json());

// Whitelist of allowed system commands
const ALLOWED_COMMANDS = {
  // File operations
  'ls': { args: ['-la'], description: 'List directory contents' },
  'pwd': { args: [], description: 'Print working directory' },
  'mkdir': { args: ['-p'], description: 'Create directory' },
  'rmdir': { args: [], description: 'Remove empty directory' },
  'rm': { args: ['-f'], description: 'Remove file' },
  'cp': { args: ['-r'], description: 'Copy file or directory' },
  'mv': { args: [], description: 'Move or rename file' },
  'chmod': { args: [], description: 'Change file permissions' },
  
  // System information
  'whoami': { args: [], description: 'Show current user' },
  'date': { args: [], description: 'Show current date and time' },
  'uptime': { args: [], description: 'Show system uptime' },
  'df': { args: ['-h'], description: 'Show disk usage' },
  'free': { args: ['-h'], description: 'Show memory usage' },
  'ps': { args: ['aux'], description: 'Show running processes' },
  
  // Network
  'ping': { args: ['-c', '4'], description: 'Ping host' },
  'curl': { args: [], description: 'Make HTTP request' },
  'wget': { args: [], description: 'Download file' },
  
  // Git operations
  'git': { args: [], description: 'Git operations' },
  
  // Node.js operations
  'npm': { args: [], description: 'Node package manager' },
  'node': { args: [], description: 'Node.js runtime' },
  
  // Text processing
  'grep': { args: [], description: 'Search text in files' },
  'sed': { args: [], description: 'Stream editor' },
  'awk': { args: [], description: 'Text processing' },
  'head': { args: ['-n', '20'], description: 'Show first lines of file' },
  'tail': { args: ['-n', '20'], description: 'Show last lines of file' },
  'cat': { args: [], description: 'Display file contents' },
  'wc': { args: ['-l'], description: 'Count lines in file' },
  
  // Compression
  'tar': { args: [], description: 'Archive operations' },
  'gzip': { args: [], description: 'Compress files' },
  'gunzip': { args: [], description: 'Decompress files' },
  
  // Text editors (safe operations only)
  'nano': { args: [], description: 'Text editor' },
  'vim': { args: [], description: 'Text editor' },
  'code': { args: [], description: 'VS Code editor' }
};

// Dangerous commands that are explicitly forbidden
const FORBIDDEN_COMMANDS = [
  'rm', 'del', 'format', 'fdisk', 'mkfs', 'dd', 'shutdown', 'reboot', 'halt',
  'poweroff', 'init', 'killall', 'pkill', 'kill', 'kill -9', 'sudo rm',
  'sudo del', 'sudo format', 'chmod 777', 'chown', 'useradd', 'userdel',
  'passwd', 'su', 'sudo su', 'sudo -i', 'bash', 'sh', 'zsh', 'csh', 'tcsh'
];

/**
 * Validate command safety
 */
function validateCommand(command, args = []) {
  // Check if command is in forbidden list
  const fullCommand = `${command} ${args.join(' ')}`.toLowerCase();
  for (const forbidden of FORBIDDEN_COMMANDS) {
    if (fullCommand.includes(forbidden.toLowerCase())) {
      return { valid: false, reason: `Command contains forbidden operation: ${forbidden}` };
    }
  }

  // Check if command is in whitelist
  if (!ALLOWED_COMMANDS[command]) {
    return { valid: false, reason: `Command '${command}' is not in whitelist` };
  }

  // Additional safety checks
  if (args.some(arg => arg.includes(';') || arg.includes('|') || arg.includes('&'))) {
    return { valid: false, reason: 'Command contains dangerous shell operators' };
  }

  return { valid: true };
}

/**
 * Execute system command safely
 */
function executeCommand(command, args = [], options = {}) {
  return new Promise((resolve, reject) => {
    const validation = validateCommand(command, args);
    if (!validation.valid) {
      reject(new Error(validation.reason));
      return;
    }

    // Set timeout (default 30 seconds)
    const timeout = options.timeout || 30000;
    
    // Execute command
    const child = spawn(command, args, {
      stdio: ['pipe', 'pipe', 'pipe'],
      timeout: timeout
    });

    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    child.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    child.on('close', (code) => {
      resolve({
        success: code === 0,
        exitCode: code,
        stdout: stdout.trim(),
        stderr: stderr.trim(),
        command: `${command} ${args.join(' ')}`,
        duration: Date.now() - child.spawnargs.startTime
      });
    });

    child.on('error', (error) => {
      reject(error);
    });

    child.on('timeout', () => {
      child.kill();
      reject(new Error(`Command timed out after ${timeout}ms`));
    });
  });
}

/**
 * Get system information safely
 */
async function getSystemInfo() {
  try {
    const info = {};
    
    // Get basic system info
    const commands = [
      { cmd: 'whoami', key: 'user' },
      { cmd: 'pwd', key: 'workingDirectory' },
      { cmd: 'date', key: 'currentTime' },
      { cmd: 'uptime', key: 'uptime' }
    ];

    for (const { cmd, key } of commands) {
      try {
        const result = await executeCommand(cmd);
        info[key] = result.success ? result.stdout : 'Unknown';
      } catch (error) {
        info[key] = 'Error';
      }
    }

    return info;
  } catch (error) {
    throw new Error(`Failed to get system info: ${error.message}`);
  }
}

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'system-executor',
    allowedCommands: Object.keys(ALLOWED_COMMANDS).length,
    timestamp: new Date().toISOString()
  });
});

// Get system information
app.get('/system-info', async (req, res) => {
  try {
    const info = await getSystemInfo();
    res.json({
      success: true,
      systemInfo: info
    });
  } catch (error) {
    console.error('❌ Failed to get system info:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Execute system command
app.post('/execute', async (req, res) => {
  try {
    const { command, args = [], timeout = 30000, dry_run = false } = req.body;

    if (!command) {
      return res.status(400).json({
        success: false,
        error: 'Command is required'
      });
    }

    if (dry_run) {
      const validation = validateCommand(command, args);
      return res.json({
        success: true,
        dry_run: true,
        command: `${command} ${args.join(' ')}`,
        valid: validation.valid,
        reason: validation.reason || 'Command is safe to execute',
        description: ALLOWED_COMMANDS[command]?.description || 'No description available'
      });
    }

    console.log(`🔧 Executing system command: ${command} ${args.join(' ')}`);
    
    const result = await executeCommand(command, args, { timeout });
    
    res.json({
      success: true,
      result
    });

  } catch (error) {
    console.error('❌ Command execution failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// List allowed commands
app.get('/commands', (req, res) => {
  const commands = Object.entries(ALLOWED_COMMANDS).map(([cmd, config]) => ({
    command: cmd,
    args: config.args,
    description: config.description
  }));

  res.json({
    success: true,
    commands,
    total: commands.length
  });
});

// File operations
app.post('/file-operations', async (req, res) => {
  try {
    const { operation, path: filePath, content, dry_run = false } = req.body;

    if (!operation || !filePath) {
      return res.status(400).json({
        success: false,
        error: 'Operation and path are required'
      });
    }

    if (dry_run) {
      return res.json({
        success: true,
        dry_run: true,
        operation,
        path: filePath,
        description: `Would perform ${operation} on ${filePath}`
      });
    }

    let result;

    switch (operation) {
      case 'read':
        result = await fs.readFile(filePath, 'utf8');
        break;
        
      case 'write':
        if (!content) {
          throw new Error('Content is required for write operation');
        }
        await fs.writeFile(filePath, content, 'utf8');
        result = 'File written successfully';
        break;
        
      case 'exists':
        try {
          await fs.access(filePath);
          result = true;
        } catch {
          result = false;
        }
        break;
        
      case 'list':
        const files = await fs.readdir(filePath);
        result = files;
        break;
        
      case 'stat':
        const stats = await fs.stat(filePath);
        result = {
          isFile: stats.isFile(),
          isDirectory: stats.isDirectory(),
          size: stats.size,
          modified: stats.mtime
        };
        break;
        
      default:
        throw new Error(`Unknown file operation: ${operation}`);
    }

    res.json({
      success: true,
      operation,
      path: filePath,
      result
    });

  } catch (error) {
    console.error('❌ File operation failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Process management
app.post('/processes', async (req, res) => {
  try {
    const { action, pid, dry_run = false } = req.body;

    if (dry_run) {
      return res.json({
        success: true,
        dry_run: true,
        action,
        description: `Would ${action} process`
      });
    }

    let result;

    switch (action) {
      case 'list':
        const psResult = await executeCommand('ps', ['aux']);
        result = psResult.stdout;
        break;
        
      case 'kill':
        if (!pid) {
          throw new Error('PID is required for kill operation');
        }
        const killResult = await executeCommand('kill', [pid.toString()]);
        result = killResult;
        break;
        
      default:
        throw new Error(`Unknown process action: ${action}`);
    }

    res.json({
      success: true,
      action,
      result
    });

  } catch (error) {
    console.error('❌ Process operation failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('❌ Unhandled error:', error);
  res.status(500).json({
    success: false,
    error: 'Internal server error',
    message: error.message
  });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🔧 System Executor service running on port ${PORT}`);
  console.log(`✅ Whitelist contains ${Object.keys(ALLOWED_COMMANDS).length} safe commands`);
  console.log(`🛡️ Security: ${FORBIDDEN_COMMANDS.length} dangerous commands blocked`);
});

module.exports = app;
