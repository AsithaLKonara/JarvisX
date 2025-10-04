/**
 * System Executor for JarvisX Orchestrator
 * Handles system-level operations like opening applications and running commands
 */

import { exec, spawn } from 'child_process';
import { promisify } from 'util';
import * as os from 'os';
import * as path from 'path';

const execAsync = promisify(exec);

export class SystemExecutor {
  private whitelistedCommands: Set<string> = new Set();
  private whitelistedApplications: Set<string> = new Set();

  constructor() {
    this.initializeWhitelist();
  }

  private initializeWhitelist(): void {
    // Whitelisted system commands
    this.whitelistedCommands.add('ls');
    this.whitelistedCommands.add('pwd');
    this.whitelistedCommands.add('whoami');
    this.whitelistedCommands.add('date');
    this.whitelistedCommands.add('uptime');
    this.whitelistedCommands.add('df');
    this.whitelistedCommands.add('ps');

    // Whitelisted applications
    this.whitelistedApplications.add('cursor');
    this.whitelistedApplications.add('vscode');
    this.whitelistedApplications.add('code');
    this.whitelistedApplications.add('notepad');
    this.whitelistedApplications.add('textedit');
    this.whitelistedApplications.add('calculator');
    this.whitelistedApplications.add('browser');
    this.whitelistedApplications.add('chrome');
    this.whitelistedApplications.add('firefox');
    this.whitelistedApplications.add('safari');
    this.whitelistedApplications.add('file-manager');
    this.whitelistedApplications.add('finder');
    this.whitelistedApplications.add('explorer');

    console.log(`✅ System executor initialized with ${this.whitelistedCommands.size} commands and ${this.whitelistedApplications.size} applications`);
  }

  /**
   * Execute a system step
   */
  public async execute(step: any, dryRun: boolean = false): Promise<any> {
    const { action, params } = step;

    try {
      console.log(`🔧 System executor: ${action} (dry_run: ${dryRun})`);

      switch (action) {
        case 'open_ide':
          return await this.openIDE(params.path, dryRun);
        
        case 'run_command':
          return await this.runCommand(params.command, params.args, dryRun);
        
        case 'open_application':
          return await this.openApplication(params.application, params.args, dryRun);
        
        case 'read_file':
          return await this.readFile(params.file_path, dryRun);
        
        case 'write_file':
          return await this.writeFile(params.file_path, params.content, dryRun);
        
        case 'list_directory':
          return await this.listDirectory(params.directory_path, dryRun);
        
        case 'get_system_info':
          return await this.getSystemInfo(dryRun);
        
        default:
          throw new Error(`Unknown system action: ${action}`);
      }

    } catch (error: any) {
      console.error(`❌ System executor failed: ${error.message}`);
      throw error;
    }
  }

  /**
   * Open IDE (Cursor/VSCode) with specified path
   */
  private async openIDE(targetPath?: string, dryRun: boolean = false): Promise<any> {
    const path = targetPath || process.cwd();
    
    if (dryRun) {
      return {
        action: 'open_ide',
        path,
        command: this.getOpenIDECommand(path),
        dry_run: true
      };
    }

    const command = this.getOpenIDECommand(path);
    console.log(`🚀 Opening IDE: ${command}`);

    try {
      await execAsync(command);
      return {
        success: true,
        action: 'open_ide',
        path,
        message: 'IDE opened successfully'
      };
    } catch (error: any) {
      throw new Error(`Failed to open IDE: ${error.message}`);
    }
  }

  /**
   * Get platform-specific IDE command
   */
  private getOpenIDECommand(targetPath: string): string {
    const platform = os.platform();
    
    switch (platform) {
      case 'darwin': // macOS
        return `open -a "Cursor" "${targetPath}"`;
      case 'win32': // Windows
        return `code "${targetPath}"`;
      case 'linux': // Linux
        return `cursor "${targetPath}"`;
      default:
        throw new Error(`Unsupported platform: ${platform}`);
    }
  }

  /**
   * Run whitelisted system command
   */
  private async runCommand(command: string, args: string[] = [], dryRun: boolean = false): Promise<any> {
    if (!this.whitelistedCommands.has(command)) {
      throw new Error(`Command not whitelisted: ${command}`);
    }

    const fullCommand = `${command} ${args.join(' ')}`.trim();

    if (dryRun) {
      return {
        action: 'run_command',
        command: fullCommand,
        whitelisted: true,
        dry_run: true
      };
    }

    console.log(`💻 Running command: ${fullCommand}`);

    try {
      const { stdout, stderr } = await execAsync(fullCommand);
      return {
        success: true,
        action: 'run_command',
        command: fullCommand,
        output: stdout,
        error: stderr
      };
    } catch (error: any) {
      throw new Error(`Command failed: ${error.message}`);
    }
  }

  /**
   * Open whitelisted application
   */
  private async openApplication(application: string, args: string[] = [], dryRun: boolean = false): Promise<any> {
    if (!this.whitelistedApplications.has(application.toLowerCase())) {
      throw new Error(`Application not whitelisted: ${application}`);
    }

    const platform = os.platform();
    let command: string;

    if (dryRun) {
      return {
        action: 'open_application',
        application,
        args,
        platform,
        dry_run: true
      };
    }

    switch (platform) {
      case 'darwin': // macOS
        command = `open -a "${application}" ${args.join(' ')}`;
        break;
      case 'win32': // Windows
        command = `start "${application}" ${args.join(' ')}`;
        break;
      case 'linux': // Linux
        command = `${application} ${args.join(' ')}`;
        break;
      default:
        throw new Error(`Unsupported platform: ${platform}`);
    }

    console.log(`🚀 Opening application: ${command}`);

    try {
      await execAsync(command);
      return {
        success: true,
        action: 'open_application',
        application,
        args,
        message: 'Application opened successfully'
      };
    } catch (error: any) {
      throw new Error(`Failed to open application: ${error.message}`);
    }
  }

  /**
   * Read file content
   */
  private async readFile(filePath: string, dryRun: boolean = false): Promise<any> {
    const fs = await import('fs/promises');
    
    if (dryRun) {
      return {
        action: 'read_file',
        file_path: filePath,
        dry_run: true
      };
    }

    try {
      const content = await fs.readFile(filePath, 'utf-8');
      return {
        success: true,
        action: 'read_file',
        file_path: filePath,
        content,
        size: content.length
      };
    } catch (error: any) {
      throw new Error(`Failed to read file: ${error.message}`);
    }
  }

  /**
   * Write file content
   */
  private async writeFile(filePath: string, content: string, dryRun: boolean = false): Promise<any> {
    const fs = await import('fs/promises');
    
    if (dryRun) {
      return {
        action: 'write_file',
        file_path: filePath,
        content_length: content.length,
        dry_run: true
      };
    }

    try {
      await fs.writeFile(filePath, content, 'utf-8');
      return {
        success: true,
        action: 'write_file',
        file_path: filePath,
        content_length: content.length,
        message: 'File written successfully'
      };
    } catch (error: any) {
      throw new Error(`Failed to write file: ${error.message}`);
    }
  }

  /**
   * List directory contents
   */
  private async listDirectory(directoryPath: string, dryRun: boolean = false): Promise<any> {
    const fs = await import('fs/promises');
    
    if (dryRun) {
      return {
        action: 'list_directory',
        directory_path: directoryPath,
        dry_run: true
      };
    }

    try {
      const items = await fs.readdir(directoryPath, { withFileTypes: true });
      const contents = items.map(item => ({
        name: item.name,
        type: item.isDirectory() ? 'directory' : 'file',
        is_directory: item.isDirectory(),
        is_file: item.isFile()
      }));

      return {
        success: true,
        action: 'list_directory',
        directory_path: directoryPath,
        contents,
        count: contents.length
      };
    } catch (error: any) {
      throw new Error(`Failed to list directory: ${error.message}`);
    }
  }

  /**
   * Get system information
   */
  private async getSystemInfo(dryRun: boolean = false): Promise<any> {
    if (dryRun) {
      return {
        action: 'get_system_info',
        dry_run: true
      };
    }

    try {
      const systemInfo = {
        platform: os.platform(),
        arch: os.arch(),
        release: os.release(),
        hostname: os.hostname(),
        uptime: os.uptime(),
        total_memory: os.totalmem(),
        free_memory: os.freemem(),
        cpus: os.cpus().length,
        user_info: os.userInfo(),
        network_interfaces: Object.keys(os.networkInterfaces())
      };

      return {
        success: true,
        action: 'get_system_info',
        system_info: systemInfo
      };
    } catch (error: any) {
      throw new Error(`Failed to get system info: ${error.message}`);
    }
  }

  /**
   * Check if command is whitelisted
   */
  public isCommandWhitelisted(command: string): boolean {
    return this.whitelistedCommands.has(command);
  }

  /**
   * Check if application is whitelisted
   */
  public isApplicationWhitelisted(application: string): boolean {
    return this.whitelistedApplications.has(application.toLowerCase());
  }

  /**
   * Add command to whitelist
   */
  public addWhitelistedCommand(command: string): void {
    this.whitelistedCommands.add(command);
    console.log(`✅ Added whitelisted command: ${command}`);
  }

  /**
   * Add application to whitelist
   */
  public addWhitelistedApplication(application: string): void {
    this.whitelistedApplications.add(application.toLowerCase());
    console.log(`✅ Added whitelisted application: ${application}`);
  }
}
