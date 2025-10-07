/**
 * Safety Service for JarvisX PC Agent
 * Privacy mode, emergency stop, and permission management
 */

export interface SafetySettings {
  privacyMode: boolean;
  emergencyStop: boolean;
  autonomyLevel: 'SUPERVISED' | 'SEMI_AUTO' | 'AUTONOMOUS' | 'LEARNING';
  riskThreshold: number; // 0-100
  requireApproval: boolean;
  auditLogging: boolean;
}

export interface ActionRisk {
  action: string;
  riskScore: number; // 0-100
  category: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  description: string;
  requiresApproval: boolean;
}

export class SafetyService {
  private settings: SafetySettings;
  private isEmergencyStop: boolean = false;
  private actionHistory: Array<{ action: string; timestamp: Date; riskScore: number; approved: boolean }> = [];

  constructor() {
    this.settings = {
      privacyMode: false,
      emergencyStop: false,
      autonomyLevel: 'SEMI_AUTO',
      riskThreshold: 70,
      requireApproval: true,
      auditLogging: true
    };
  }

  public enablePrivacyMode(): void {
    this.settings.privacyMode = true;
    console.log('🔒 Privacy mode enabled - All control disabled');
  }

  public disablePrivacyMode(): void {
    this.settings.privacyMode = false;
    console.log('🔓 Privacy mode disabled - Control restored');
  }

  public isPrivacyModeEnabled(): boolean {
    return this.settings.privacyMode;
  }

  public emergencyStop(): void {
    this.isEmergencyStop = true;
    this.settings.emergencyStop = true;
    console.log('🛑 EMERGENCY STOP ACTIVATED - All operations halted');
  }

  public resumeFromEmergencyStop(): void {
    this.isEmergencyStop = false;
    this.settings.emergencyStop = false;
    console.log('▶️ Emergency stop cleared - Operations resumed');
  }

  public isEmergencyStopped(): boolean {
    return this.isEmergencyStop;
  }

  public setAutonomyLevel(level: 'SUPERVISED' | 'SEMI_AUTO' | 'AUTONOMOUS' | 'LEARNING'): void {
    this.settings.autonomyLevel = level;
    console.log(`🎛️ Autonomy level set to: ${level}`);
  }

  public getAutonomyLevel(): string {
    return this.settings.autonomyLevel;
  }

  public assessActionRisk(action: string, params: any = {}): ActionRisk {
    let riskScore = 0;
    let category: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' = 'LOW';
    let requiresApproval = false;

    // Risk assessment based on action type
    if (action.includes('delete') || action.includes('remove') || action.includes('uninstall')) {
      riskScore += 40;
    }
    
    if (action.includes('system') || action.includes('admin') || action.includes('root')) {
      riskScore += 30;
    }
    
    if (action.includes('file') || action.includes('folder') || action.includes('directory')) {
      riskScore += 20;
    }
    
    if (action.includes('network') || action.includes('internet') || action.includes('browser')) {
      riskScore += 15;
    }
    
    if (action.includes('click') || action.includes('type') || action.includes('keyboard')) {
      riskScore += 10;
    }

    // Risk assessment based on parameters
    if (params.destructive) {
      riskScore += 50;
    }
    
    if (params.systemLevel) {
      riskScore += 40;
    }
    
    if (params.requiresAdmin) {
      riskScore += 35;
    }

    // Determine category and approval requirement
    if (riskScore >= 80) {
      category = 'CRITICAL';
      requiresApproval = true;
    } else if (riskScore >= 60) {
      category = 'HIGH';
      requiresApproval = true;
    } else if (riskScore >= 40) {
      category = 'MEDIUM';
      requiresApproval = this.settings.autonomyLevel === 'SUPERVISED' || this.settings.autonomyLevel === 'LEARNING';
    } else {
      category = 'LOW';
      requiresApproval = this.settings.autonomyLevel === 'SUPERVISED';
    }

    return {
      action,
      riskScore,
      category,
      description: this.getRiskDescription(category, riskScore),
      requiresApproval
    };
  }

  private getRiskDescription(category: string, riskScore: number): string {
    switch (category) {
      case 'CRITICAL':
        return `Critical risk (${riskScore}%) - This action could cause serious system damage or data loss`;
      case 'HIGH':
        return `High risk (${riskScore}%) - This action could affect system stability or important data`;
      case 'MEDIUM':
        return `Medium risk (${riskScore}%) - This action has moderate potential for unintended consequences`;
      case 'LOW':
        return `Low risk (${riskScore}%) - This action is generally safe to execute`;
      default:
        return `Unknown risk level (${riskScore}%)`;
    }
  }

  public canExecuteAction(action: string, params: any = {}): { allowed: boolean; reason?: string; risk?: ActionRisk } {
    // Check emergency stop
    if (this.isEmergencyStopped()) {
      return { allowed: false, reason: 'Emergency stop is active' };
    }

    // Check privacy mode
    if (this.isPrivacyModeEnabled()) {
      return { allowed: false, reason: 'Privacy mode is enabled' };
    }

    // Assess risk
    const risk = this.assessActionRisk(action, params);

    // Log action for audit
    if (this.settings.auditLogging) {
      this.actionHistory.push({
        action,
        timestamp: new Date(),
        riskScore: risk.riskScore,
        approved: false
      });
    }

    // Check if approval is required
    if (risk.requiresApproval) {
      return { 
        allowed: false, 
        reason: 'Action requires approval', 
        risk 
      };
    }

    return { allowed: true, risk };
  }

  public approveAction(action: string, approved: boolean): void {
    // Find the most recent action with this name
    const actionIndex = this.actionHistory.findLastIndex(entry => entry.action === action);
    
    if (actionIndex !== -1) {
      this.actionHistory[actionIndex].approved = approved;
      console.log(`✅ Action "${action}" ${approved ? 'approved' : 'rejected'}`);
    }
  }

  public getActionHistory(): Array<{ action: string; timestamp: Date; riskScore: number; approved: boolean }> {
    return [...this.actionHistory];
  }

  public getSafetyStatus(): any {
    return {
      privacyMode: this.settings.privacyMode,
      emergencyStop: this.isEmergencyStop,
      autonomyLevel: this.settings.autonomyLevel,
      riskThreshold: this.settings.riskThreshold,
      requireApproval: this.settings.requireApproval,
      auditLogging: this.settings.auditLogging,
      totalActions: this.actionHistory.length,
      pendingApprovals: this.actionHistory.filter(a => !a.approved).length
    };
  }

  public updateSettings(newSettings: Partial<SafetySettings>): void {
    this.settings = { ...this.settings, ...newSettings };
    console.log('🔧 Safety settings updated');
  }

  public resetEmergencyStop(): void {
    this.isEmergencyStop = false;
    this.settings.emergencyStop = false;
    console.log('🔄 Emergency stop reset');
  }

  public clearActionHistory(): void {
    this.actionHistory = [];
    console.log('🗑️ Action history cleared');
  }
}
