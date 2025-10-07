/**
 * JarvisX Approval Service
 * Smart decision making and user approval system
 */

import OpenAI from 'openai';
import { v4 as uuidv4 } from 'uuid';

export interface ApprovalRequest {
  id: string;
  action: string;
  description: string;
  riskScore: number;
  riskCategory: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  context: any;
  parameters: any;
  requiresApproval: boolean;
  autoApprove: boolean;
  timeout: number; // in minutes
  createdAt: Date;
  expiresAt: Date;
  status: 'pending' | 'approved' | 'rejected' | 'expired' | 'cancelled';
  userId?: string;
  deviceId?: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  category: 'system' | 'file' | 'network' | 'browser' | 'application' | 'security';
}

export interface ApprovalDecision {
  requestId: string;
  decision: 'approve' | 'reject' | 'modify';
  reason: string;
  confidence: number;
  suggestedModifications?: any;
  timestamp: Date;
  userId?: string;
}

export interface UserPreferences {
  userId: string;
  autoApproveLowRisk: boolean;
  autoApproveMediumRisk: boolean;
  autoApproveHighRisk: boolean;
  autoApproveCriticalRisk: boolean;
  maxRiskThreshold: number;
  preferredApprovalMethod: 'mobile' | 'desktop' | 'voice' | 'web';
  notificationSettings: {
    email: boolean;
    push: boolean;
    sms: boolean;
  };
  workingHours: {
    start: string; // HH:MM format
    end: string;   // HH:MM format
    timezone: string;
  };
  riskTolerance: 'conservative' | 'moderate' | 'aggressive';
}

export class ApprovalService {
  private openai: OpenAI;
  private requests: Map<string, ApprovalRequest> = new Map();
  private decisions: Map<string, ApprovalDecision> = new Map();
  private userPreferences: Map<string, UserPreferences> = new Map();
  private isInitialized: boolean = false;

  constructor() {
    this.initializeOpenAI();
  }

  private initializeOpenAI(): void {
    try {
      if (!process.env.OPENAI_API_KEY) {
        throw new Error('OPENAI_API_KEY not found in environment variables');
      }

      this.openai = new OpenAI({
        apiKey: process.env.OPENAI_API_KEY
      });

      this.isInitialized = true;
      console.log('✅ Approval Service OpenAI client initialized');
      
    } catch (error) {
      console.error('❌ Failed to initialize Approval Service OpenAI client:', error);
      this.isInitialized = false;
    }
  }

  public async assessRisk(action: string, parameters: any, context: any = {}): Promise<{
    riskScore: number;
    riskCategory: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    requiresApproval: boolean;
    autoApprove: boolean;
    reasoning: string;
    factors: string[];
  }> {
    if (!this.isInitialized) {
      throw new Error('Approval Service not initialized');
    }

    try {
      console.log('🔍 Assessing risk for action:', action);

      const prompt = `You are an AI risk assessment system. Analyze the following action and provide a comprehensive risk assessment.

Action: ${action}
Parameters: ${JSON.stringify(parameters, null, 2)}
Context: ${JSON.stringify(context, null, 2)}

Assess the risk based on:
1. Potential system damage
2. Data loss risk
3. Security implications
4. User impact
5. Reversibility
6. Complexity
7. Dependencies

Provide a risk score (0-100) and category:
- LOW (0-30): Safe, reversible, minimal impact
- MEDIUM (31-60): Moderate risk, some impact, mostly reversible
- HIGH (61-80): Significant risk, notable impact, difficult to reverse
- CRITICAL (81-100): Extreme risk, severe impact, irreversible

Respond in JSON format:
{
  "riskScore": 45,
  "riskCategory": "MEDIUM",
  "requiresApproval": true,
  "autoApprove": false,
  "reasoning": "Detailed explanation of risk assessment",
  "factors": ["factor1", "factor2", "factor3"]
}`;

      const response = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: "You are an expert risk assessment AI. Provide accurate, conservative risk assessments for system actions."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        max_tokens: 1000,
        temperature: 0.2
      });

      const content = response.choices[0].message.content || '{}';
      const assessment = JSON.parse(content);

      console.log(`✅ Risk assessment completed: ${assessment.riskCategory} (${assessment.riskScore})`);

      return assessment;

    } catch (error) {
      console.error('❌ Risk assessment failed:', error);
      throw error;
    }
  }

  public async createApprovalRequest(
    action: string,
    description: string,
    parameters: any,
    context: any = {},
    userId?: string,
    deviceId?: string
  ): Promise<ApprovalRequest> {
    try {
      console.log('📝 Creating approval request for action:', action);

      // Assess risk first
      const riskAssessment = await this.assessRisk(action, parameters, context);

      // Determine if approval is required based on risk and user preferences
      const userPrefs = userId ? this.userPreferences.get(userId) : null;
      const requiresApproval = this.determineApprovalRequirement(riskAssessment, userPrefs);
      const autoApprove = this.determineAutoApprove(riskAssessment, userPrefs);

      const request: ApprovalRequest = {
        id: uuidv4(),
        action,
        description,
        riskScore: riskAssessment.riskScore,
        riskCategory: riskAssessment.riskCategory,
        context,
        parameters,
        requiresApproval,
        autoApprove,
        timeout: this.getTimeoutForRisk(riskAssessment.riskCategory),
        createdAt: new Date(),
        expiresAt: new Date(Date.now() + this.getTimeoutForRisk(riskAssessment.riskCategory) * 60000),
        status: autoApprove ? 'approved' : 'pending',
        userId,
        deviceId,
        priority: this.getPriorityForRisk(riskAssessment.riskCategory),
        category: this.categorizeAction(action)
      };

      this.requests.set(request.id, request);

      // If auto-approve, create decision immediately
      if (autoApprove) {
        const decision: ApprovalDecision = {
          requestId: request.id,
          decision: 'approve',
          reason: 'Auto-approved based on risk assessment and user preferences',
          confidence: 95,
          timestamp: new Date(),
          userId
        };
        this.decisions.set(request.id, decision);
      }

      console.log(`✅ Approval request created: ${request.id} (${request.status})`);

      return request;

    } catch (error) {
      console.error('❌ Approval request creation failed:', error);
      throw error;
    }
  }

  public async makeDecision(
    requestId: string,
    decision: 'approve' | 'reject' | 'modify',
    reason: string,
    userId?: string,
    suggestedModifications?: any
  ): Promise<ApprovalDecision> {
    try {
      const request = this.requests.get(requestId);
      if (!request) {
        throw new Error(`Approval request ${requestId} not found`);
      }

      if (request.status !== 'pending') {
        throw new Error(`Request ${requestId} is not pending`);
      }

      console.log(`🤔 Making decision for request ${requestId}: ${decision}`);

      const approvalDecision: ApprovalDecision = {
        requestId,
        decision,
        reason,
        confidence: this.calculateDecisionConfidence(request, decision),
        suggestedModifications,
        timestamp: new Date(),
        userId
      };

      this.decisions.set(requestId, approvalDecision);

      // Update request status
      request.status = decision === 'approve' ? 'approved' : decision === 'reject' ? 'rejected' : 'pending';

      console.log(`✅ Decision made for request ${requestId}: ${decision}`);

      return approvalDecision;

    } catch (error) {
      console.error('❌ Decision making failed:', error);
      throw error;
    }
  }

  public async getSmartRecommendation(requestId: string): Promise<{
    recommendation: 'approve' | 'reject' | 'modify';
    confidence: number;
    reasoning: string;
    suggestedModifications?: any;
  }> {
    if (!this.isInitialized) {
      throw new Error('Approval Service not initialized');
    }

    try {
      const request = this.requests.get(requestId);
      if (!request) {
        throw new Error(`Approval request ${requestId} not found`);
      }

      console.log(`🧠 Generating smart recommendation for request ${requestId}`);

      const prompt = `You are an AI approval advisor. Analyze this approval request and provide a smart recommendation.

Request Details:
- Action: ${request.action}
- Description: ${request.description}
- Risk Score: ${request.riskScore}
- Risk Category: ${request.riskCategory}
- Parameters: ${JSON.stringify(request.parameters, null, 2)}
- Context: ${JSON.stringify(request.context, null, 2)}

Consider:
1. Risk vs benefit analysis
2. User's historical preferences
3. System safety implications
4. Potential alternatives
5. Reversibility of the action

Provide a recommendation with confidence level and reasoning.

Respond in JSON format:
{
  "recommendation": "approve",
  "confidence": 85,
  "reasoning": "Detailed explanation of recommendation",
  "suggestedModifications": {
    "parameter1": "modified_value",
    "reason": "Why this modification is suggested"
  }
}`;

      const response = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: "You are an expert approval advisor. Provide smart, safe recommendations for system actions."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        max_tokens: 1000,
        temperature: 0.3
      });

      const content = response.choices[0].message.content || '{}';
      const recommendation = JSON.parse(content);

      console.log(`✅ Smart recommendation generated: ${recommendation.recommendation} (${recommendation.confidence}%)`);

      return recommendation;

    } catch (error) {
      console.error('❌ Smart recommendation failed:', error);
      throw error;
    }
  }

  private determineApprovalRequirement(riskAssessment: any, userPrefs?: UserPreferences): boolean {
    if (!userPrefs) {
      // Default behavior based on risk
      return riskAssessment.riskScore >= 30;
    }

    // Use user preferences
    switch (riskAssessment.riskCategory) {
      case 'LOW':
        return !userPrefs.autoApproveLowRisk;
      case 'MEDIUM':
        return !userPrefs.autoApproveMediumRisk;
      case 'HIGH':
        return !userPrefs.autoApproveHighRisk;
      case 'CRITICAL':
        return !userPrefs.autoApproveCriticalRisk;
      default:
        return true;
    }
  }

  private determineAutoApprove(riskAssessment: any, userPrefs?: UserPreferences): boolean {
    if (!userPrefs) {
      return riskAssessment.riskScore < 20;
    }

    return riskAssessment.riskScore < userPrefs.maxRiskThreshold;
  }

  private getTimeoutForRisk(riskCategory: string): number {
    switch (riskCategory) {
      case 'LOW':
        return 5; // 5 minutes
      case 'MEDIUM':
        return 15; // 15 minutes
      case 'HIGH':
        return 30; // 30 minutes
      case 'CRITICAL':
        return 60; // 1 hour
      default:
        return 15;
    }
  }

  private getPriorityForRisk(riskCategory: string): 'low' | 'medium' | 'high' | 'critical' {
    switch (riskCategory) {
      case 'LOW':
        return 'low';
      case 'MEDIUM':
        return 'medium';
      case 'HIGH':
        return 'high';
      case 'CRITICAL':
        return 'critical';
      default:
        return 'medium';
    }
  }

  private categorizeAction(action: string): 'system' | 'file' | 'network' | 'browser' | 'application' | 'security' {
    const lowerAction = action.toLowerCase();
    
    if (lowerAction.includes('file') || lowerAction.includes('folder') || lowerAction.includes('directory')) {
      return 'file';
    }
    if (lowerAction.includes('network') || lowerAction.includes('internet') || lowerAction.includes('browser')) {
      return 'network';
    }
    if (lowerAction.includes('browser') || lowerAction.includes('web') || lowerAction.includes('url')) {
      return 'browser';
    }
    if (lowerAction.includes('app') || lowerAction.includes('application') || lowerAction.includes('program')) {
      return 'application';
    }
    if (lowerAction.includes('security') || lowerAction.includes('permission') || lowerAction.includes('access')) {
      return 'security';
    }
    
    return 'system';
  }

  private calculateDecisionConfidence(request: ApprovalRequest, decision: string): number {
    let confidence = 50; // Base confidence

    // Adjust based on risk level
    if (request.riskCategory === 'LOW') {
      confidence += 20;
    } else if (request.riskCategory === 'MEDIUM') {
      confidence += 10;
    } else if (request.riskCategory === 'HIGH') {
      confidence -= 10;
    } else if (request.riskCategory === 'CRITICAL') {
      confidence -= 20;
    }

    // Adjust based on decision type
    if (decision === 'approve' && request.riskScore < 30) {
      confidence += 15;
    } else if (decision === 'reject' && request.riskScore > 70) {
      confidence += 15;
    }

    return Math.max(0, Math.min(100, confidence));
  }

  public setUserPreferences(userId: string, preferences: UserPreferences): void {
    this.userPreferences.set(userId, preferences);
    console.log(`✅ User preferences updated for user: ${userId}`);
  }

  public getUserPreferences(userId: string): UserPreferences | undefined {
    return this.userPreferences.get(userId);
  }

  public getRequest(requestId: string): ApprovalRequest | undefined {
    return this.requests.get(requestId);
  }

  public getDecision(requestId: string): ApprovalDecision | undefined {
    return this.decisions.get(requestId);
  }

  public getPendingRequests(): ApprovalRequest[] {
    return Array.from(this.requests.values()).filter(req => req.status === 'pending');
  }

  public getRequestsByUser(userId: string): ApprovalRequest[] {
    return Array.from(this.requests.values()).filter(req => req.userId === userId);
  }

  public getApprovalStats(): any {
    const requests = Array.from(this.requests.values());
    const decisions = Array.from(this.decisions.values());

    return {
      totalRequests: requests.length,
      pending: requests.filter(r => r.status === 'pending').length,
      approved: requests.filter(r => r.status === 'approved').length,
      rejected: requests.filter(r => r.status === 'rejected').length,
      expired: requests.filter(r => r.status === 'expired').length,
      cancelled: requests.filter(r => r.status === 'cancelled').length,
      averageRiskScore: requests.length > 0 ? 
        requests.reduce((sum, r) => sum + r.riskScore, 0) / requests.length : 0,
      averageDecisionTime: decisions.length > 0 ?
        decisions.reduce((sum, d) => sum + (d.timestamp.getTime() - requests.find(r => r.id === d.requestId)?.createdAt.getTime() || 0), 0) / decisions.length : 0
    };
  }

  public isReady(): boolean {
    return this.isInitialized;
  }
}
