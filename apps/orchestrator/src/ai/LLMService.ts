/**
 * LLM Service for JarvisX Orchestrator
 * Handles OpenAI GPT-5 integration with prompt management and response validation
 */

import OpenAI from 'openai';
import fs from 'fs/promises';
import path from 'path';
import { validateTask } from '../../../shared/schemas';
import { Task } from '../../../shared/schemas';

export interface LLMConfig {
  apiKey: string;
  model: string;
  maxTokens: number;
  temperature: number;
  timeout: number;
}

export interface LLMResponse {
  success: boolean;
  data?: any;
  error?: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export class LLMService {
  private client: OpenAI | null = null;
  private config: LLMConfig;
  private prompts: Map<string, string> = new Map();

  constructor() {
    this.config = {
      apiKey: process.env.GPT_API_KEY || '',
      model: process.env.GPT_MODEL || 'gpt-4',
      maxTokens: parseInt(process.env.GPT_MAX_TOKENS || '4000'),
      temperature: parseFloat(process.env.GPT_TEMPERATURE || '0.1'),
      timeout: parseInt(process.env.GPT_TIMEOUT || '30000')
    };

    this.initializeClient();
    this.loadPrompts();
  }

  private initializeClient(): void {
    if (this.config.apiKey) {
      this.client = new OpenAI({
        apiKey: this.config.apiKey,
        timeout: this.config.timeout
      });
      console.log(`✅ LLM Service initialized with model: ${this.config.model}`);
    } else {
      console.warn('⚠️  GPT_API_KEY not found, LLM Service disabled');
    }
  }

  private async loadPrompts(): Promise<void> {
    try {
      const promptsDir = path.join(__dirname, '../../../shared/prompts');
      const files = await fs.readdir(promptsDir);
      
      for (const file of files) {
        if (file.endsWith('.prompt.txt')) {
          const promptName = file.replace('.prompt.txt', '');
          const promptContent = await fs.readFile(
            path.join(promptsDir, file), 
            'utf-8'
          );
          this.prompts.set(promptName, promptContent);
        }
      }
      
      console.log(`✅ Loaded ${this.prompts.size} prompt templates`);
    } catch (error) {
      console.warn('⚠️  Failed to load prompt templates:', error);
    }
  }

  public isConfigured(): boolean {
    return this.client !== null && this.config.apiKey.length > 0;
  }

  public async planTask(userText: string, context?: any): Promise<LLMResponse> {
    if (!this.client) {
      return {
        success: false,
        error: 'LLM service not configured'
      };
    }

    try {
      const plannerPrompt = this.prompts.get('planner') || this.getDefaultPlannerPrompt();
      const systemPrompt = plannerPrompt.split('USER:')[0].replace('SYSTEM:', '').trim();
      const userPromptTemplate = plannerPrompt.split('USER:')[1]?.trim() || '';
      
      const userPrompt = userPromptTemplate
        .replace('{{user_text}}', userText)
        .replace('{{permissions}}', JSON.stringify(context?.permissions || []))
        .replace('{{preferences}}', JSON.stringify(context?.preferences || {}));

      console.log(`🤖 Planning task for: "${userText.substring(0, 100)}..."`);

      const response = await this.client.chat.completions.create({
        model: this.config.model,
        messages: [
          {
            role: 'system',
            content: systemPrompt
          },
          {
            role: 'user',
            content: userPrompt
          }
        ],
        max_tokens: this.config.maxTokens,
        temperature: this.config.temperature,
        response_format: { type: "json_object" }
      });

      const content = response.choices[0]?.message?.content;
      if (!content) {
        return {
          success: false,
          error: 'Empty response from LLM'
        };
      }

      // Parse and validate JSON response
      let taskData: Task;
      try {
        taskData = JSON.parse(content);
      } catch (parseError) {
        return {
          success: false,
          error: `Invalid JSON response: ${parseError}`
        };
      }

      // Validate against schema
      const validation = validateTask(taskData);
      if (!validation.valid) {
        return {
          success: false,
          error: `Schema validation failed: ${JSON.stringify(validation.errors)}`,
          data: taskData // Return raw data for debugging
        };
      }

      console.log(`✅ Task planned successfully: ${taskData.task_id}`);

      return {
        success: true,
        data: taskData,
        usage: {
          prompt_tokens: response.usage?.prompt_tokens || 0,
          completion_tokens: response.usage?.completion_tokens || 0,
          total_tokens: response.usage?.total_tokens || 0
        }
      };

    } catch (error: any) {
      console.error('❌ Task planning failed:', error);
      return {
        success: false,
        error: error.message || 'Unknown error occurred'
      };
    }
  }

  public async parseWhatsAppOrder(message: string, context?: any): Promise<LLMResponse> {
    if (!this.client) {
      return {
        success: false,
        error: 'LLM service not configured'
      };
    }

    try {
      const parserPrompt = this.prompts.get('whatsapp-order-parser') || this.getDefaultOrderParserPrompt();
      const systemPrompt = parserPrompt.split('USER:')[0].replace('SYSTEM:', '').trim();
      const userPromptTemplate = parserPrompt.split('USER:')[1]?.trim() || '';
      
      const userPrompt = userPromptTemplate.replace('{{message}}', message);

      console.log(`📱 Parsing WhatsApp order: "${message.substring(0, 100)}..."`);

      const response = await this.client.chat.completions.create({
        model: this.config.model,
        messages: [
          {
            role: 'system',
            content: systemPrompt
          },
          {
            role: 'user',
            content: userPrompt
          }
        ],
        max_tokens: 1000,
        temperature: 0.1,
        response_format: { type: "json_object" }
      });

      const content = response.choices[0]?.message?.content;
      if (!content) {
        return {
          success: false,
          error: 'Empty response from LLM'
        };
      }

      const orderData = JSON.parse(content);
      
      // Add timestamp if not present
      if (!orderData.timestamp) {
        orderData.timestamp = new Date().toISOString();
      }

      console.log(`✅ WhatsApp order parsed successfully`);

      return {
        success: true,
        data: orderData,
        usage: {
          prompt_tokens: response.usage?.prompt_tokens || 0,
          completion_tokens: response.usage?.completion_tokens || 0,
          total_tokens: response.usage?.total_tokens || 0
        }
      };

    } catch (error: any) {
      console.error('❌ WhatsApp order parsing failed:', error);
      return {
        success: false,
        error: error.message || 'Unknown error occurred'
      };
    }
  }

  public async checkSafety(action: string, tool: string, params: any, userPermissions: string[]): Promise<LLMResponse> {
    if (!this.client) {
      return {
        success: false,
        error: 'LLM service not configured'
      };
    }

    try {
      const safetyPrompt = this.prompts.get('safety-checker') || this.getDefaultSafetyPrompt();
      const systemPrompt = safetyPrompt.split('USER:')[0].replace('SYSTEM:', '').trim();
      const userPromptTemplate = safetyPrompt.split('USER:')[1]?.trim() || '';
      
      const userPrompt = userPromptTemplate
        .replace('{{action_description}}', action)
        .replace('{{tool_name}}', tool)
        .replace('{{parameters}}', JSON.stringify(params))
        .replace('{{user_permissions}}', JSON.stringify(userPermissions));

      const response = await this.client.chat.completions.create({
        model: this.config.model,
        messages: [
          {
            role: 'system',
            content: systemPrompt
          },
          {
            role: 'user',
            content: userPrompt
          }
        ],
        max_tokens: 500,
        temperature: 0.0,
        response_format: { type: "json_object" }
      });

      const content = response.choices[0]?.message?.content;
      if (!content) {
        return {
          success: false,
          error: 'Empty response from LLM'
        };
      }

      const safetyData = JSON.parse(content);

      return {
        success: true,
        data: safetyData,
        usage: {
          prompt_tokens: response.usage?.prompt_tokens || 0,
          completion_tokens: response.usage?.completion_tokens || 0,
          total_tokens: response.usage?.total_tokens || 0
        }
      };

    } catch (error: any) {
      console.error('❌ Safety check failed:', error);
      return {
        success: false,
        error: error.message || 'Unknown error occurred'
      };
    }
  }

  private getDefaultPlannerPrompt(): string {
    return `SYSTEM:
You are an expert task planner for JarvisX, a Sinhala-enabled AI assistant. Your job is to convert user instructions (in Sinhala or English) into structured JSON task plans.

CRITICAL RULES:
1. ALWAYS return valid JSON only - no prose, no explanations, no markdown
2. If you cannot plan a task, return: {"task_id":"error","intent":"","steps":[],"error":"Cannot process this request"}
3. All steps must have valid tool names from the available list
4. Mark steps as requires_approval=true for any potentially dangerous actions

AVAILABLE TOOLS:
- system_executor: Open applications, run whitelisted commands, file operations
- web_executor: Navigate websites, fill forms, click buttons (using Playwright)
- whatsapp_executor: Send WhatsApp messages, parse incoming messages
- tts_service: Convert text to speech in Sinhala or English

OUTPUT FORMAT (JSON only):
{
  "task_id": "unique_task_id",
  "intent": "Clear description of what user wants",
  "user_text": "Original user input",
  "steps": [
    {
      "step_id": 1,
      "action": "Human readable action description",
      "tool": "executor_name",
      "params": {
        "param1": "value1"
      },
      "requires_approval": true,
      "permissions": ["permission_name"]
    }
  ],
  "estimated_duration": 30,
  "risk_level": "low"
}

USER:
Instruction: "{{user_text}}"
Context: tools available: system_executor, web_executor, whatsapp_executor, tts_service.
Constraints: Ask for user confirmation for any step that requires shell commands, payments, or access to private keys.
Return a JSON Task.`;
  }

  private getDefaultOrderParserPrompt(): string {
    return `SYSTEM:
You are a strict order parser for JarvisX. Extract structured order data from WhatsApp messages in Sinhala or English.

CRITICAL RULES:
1. Return ONLY valid JSON matching the Order schema
2. If information is missing, use null values
3. Do not add extra fields beyond the schema
4. Extract phone numbers, quantities, and amounts accurately

OUTPUT FORMAT (JSON only):
{
  "customer": {
    "name": "string (required)",
    "phone": "string (optional)",
    "address": "string (optional)"
  },
  "items": [
    {
      "sku": "string (required)",
      "title": "string (required)", 
      "qty": "integer (required)"
    }
  ],
  "source": "whatsapp",
  "timestamp": "ISO date string"
}

USER:
Parse this WhatsApp message: "{{message}}"`;
  }

  private getDefaultSafetyPrompt(): string {
    return `SYSTEM:
You are a safety checker for JarvisX. Analyze proposed actions and determine if they are safe to execute.

DANGEROUS PATTERNS TO BLOCK:
- File deletion commands (rm, del, unlink)
- System administration (sudo, admin, root)
- Network requests to unknown domains
- Access to private keys, passwords, credentials

SAFE PATTERNS TO ALLOW:
- Opening applications (open, start)
- Reading public files
- Basic web navigation to known sites
- Creating new files in user directories

OUTPUT FORMAT (JSON only):
{
  "safe": true/false,
  "requires_approval": true/false,
  "risk_level": "low/medium/high",
  "reason": "explanation",
  "suggested_alternative": "safer alternative if unsafe"
}

USER:
Action: "{{action_description}}"
Tool: "{{tool_name}}"
Parameters: {{parameters}}
User permissions: {{user_permissions}}

Analyze this action:`;
  }
}
