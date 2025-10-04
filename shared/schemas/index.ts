import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import taskSchema from './task.schema.json';
import orderSchema from './order.schema.json';

const ajv = new Ajv({ allErrors: true });
addFormats(ajv);

export const taskValidator = ajv.compile(taskSchema);
export const orderValidator = ajv.compile(orderSchema);

export interface Task {
  task_id: string;
  intent: string;
  user_text?: string;
  steps: TaskStep[];
  estimated_duration?: number;
  risk_level?: 'low' | 'medium' | 'high';
  error?: string;
}

export interface TaskStep {
  step_id: number;
  action: string;
  tool: 'system_executor' | 'web_executor' | 'whatsapp_executor' | 'tts_service';
  params: Record<string, any>;
  requires_approval?: boolean;
  permissions?: string[];
}

export interface Order {
  customer: {
    name: string;
    phone?: string;
    address?: string;
    email?: string;
  };
  items: OrderItem[];
  total_amount?: number;
  delivery_date?: string;
  payment_method?: 'cash' | 'card' | 'bank_transfer' | 'digital_wallet';
  notes?: string;
  source?: 'whatsapp' | 'voice' | 'web' | 'mobile';
  timestamp?: string;
}

export interface OrderItem {
  sku: string;
  title: string;
  qty: number;
  price?: number;
  notes?: string;
}

export function validateTask(data: unknown): { valid: boolean; errors?: any[] } {
  const valid = taskValidator(data);
  return {
    valid: valid as boolean,
    errors: valid ? undefined : taskValidator.errors
  };
}

export function validateOrder(data: unknown): { valid: boolean; errors?: any[] } {
  const valid = orderValidator(data);
  return {
    valid: valid as boolean,
    errors: valid ? undefined : orderValidator.errors
  };
}
