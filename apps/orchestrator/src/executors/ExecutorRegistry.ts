/**
 * Executor Registry for JarvisX Orchestrator
 * Manages and coordinates different types of executors
 */

import { SystemExecutor } from './SystemExecutor';
import { WebExecutor } from './WebExecutor';
import { WhatsAppExecutor } from './WhatsAppExecutor';
import { TTSExecutor } from './TTSExecutor';

export interface Executor {
  name: string;
  execute(step: any, dryRun?: boolean): Promise<any>;
}

export class ExecutorRegistry {
  private executors: Map<string, Executor> = new Map();

  constructor() {
    this.initializeExecutors();
  }

  private initializeExecutors(): void {
    // Initialize system executor
    const systemExecutor = new SystemExecutor();
    this.executors.set('system_executor', systemExecutor);

    // Initialize web executor
    const webExecutor = new WebExecutor();
    this.executors.set('web_executor', webExecutor);

    // Initialize WhatsApp executor
    const whatsappExecutor = new WhatsAppExecutor();
    this.executors.set('whatsapp_executor', whatsappExecutor);

    // Initialize TTS executor
    const ttsExecutor = new TTSExecutor();
    this.executors.set('tts_service', ttsExecutor);

    console.log(`✅ Initialized ${this.executors.size} executors`);
  }

  /**
   * Get executor by name
   */
  public getExecutor(name: string): Executor | undefined {
    return this.executors.get(name);
  }

  /**
   * Get all available executors
   */
  public getAvailableExecutors(): string[] {
    return Array.from(this.executors.keys());
  }

  /**
   * Register a new executor
   */
  public registerExecutor(executor: Executor): void {
    this.executors.set(executor.name, executor);
    console.log(`✅ Registered executor: ${executor.name}`);
  }

  /**
   * Unregister an executor
   */
  public unregisterExecutor(name: string): void {
    this.executors.delete(name);
    console.log(`❌ Unregistered executor: ${name}`);
  }
}
