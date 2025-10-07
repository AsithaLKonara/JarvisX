/**
 * Approval Request Model
 * Approval workflow and decision tracking
 */

import { DataTypes, Model, Optional } from 'sequelize';
import { sequelize } from '../config/database';

export interface ApprovalRequestAttributes {
  id: string;
  userId: string;
  commandId?: string;
  action: string;
  description: string;
  riskScore: number;
  riskCategory: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  context: any;
  parameters: any;
  status: 'pending' | 'approved' | 'rejected' | 'expired' | 'cancelled';
  approvedBy?: string;
  approvedAt?: Date;
  rejectedBy?: string;
  rejectedAt?: Date;
  reason?: string;
  expiresAt: Date;
  priority: 'low' | 'medium' | 'high' | 'critical';
  category: 'system' | 'file' | 'network' | 'browser' | 'application' | 'security';
  createdAt: Date;
  updatedAt: Date;
}

export interface ApprovalRequestCreationAttributes extends Optional<ApprovalRequestAttributes, 'id' | 'commandId' | 'approvedBy' | 'approvedAt' | 'rejectedBy' | 'rejectedAt' | 'reason'> {}

export class ApprovalRequest extends Model<ApprovalRequestAttributes, ApprovalRequestCreationAttributes> implements ApprovalRequestAttributes {
  public id!: string;
  public userId!: string;
  public commandId?: string;
  public action!: string;
  public description!: string;
  public riskScore!: number;
  public riskCategory!: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  public context!: any;
  public parameters!: any;
  public status!: 'pending' | 'approved' | 'rejected' | 'expired' | 'cancelled';
  public approvedBy?: string;
  public approvedAt?: Date;
  public rejectedBy?: string;
  public rejectedAt?: Date;
  public reason?: string;
  public expiresAt!: Date;
  public priority!: 'low' | 'medium' | 'high' | 'critical';
  public category!: 'system' | 'file' | 'network' | 'browser' | 'application' | 'security';
  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;

  // Instance methods
  public isPending(): boolean {
    return this.status === 'pending';
  }

  public isApproved(): boolean {
    return this.status === 'approved';
  }

  public isRejected(): boolean {
    return this.status === 'rejected';
  }

  public isExpired(): boolean {
    return this.status === 'expired' || new Date() > this.expiresAt;
  }

  public isCancelled(): boolean {
    return this.status === 'cancelled';
  }

  public isHighRisk(): boolean {
    return this.riskCategory === 'HIGH' || this.riskCategory === 'CRITICAL';
  }

  public isCritical(): boolean {
    return this.riskCategory === 'CRITICAL';
  }

  public isHighPriority(): boolean {
    return this.priority === 'high' || this.priority === 'critical';
  }

  public getTimeRemaining(): number {
    return Math.max(0, this.expiresAt.getTime() - Date.now());
  }

  public getTimeRemainingMinutes(): number {
    return Math.floor(this.getTimeRemaining() / (1000 * 60));
  }

  public isUrgent(): boolean {
    return this.getTimeRemainingMinutes() < 5;
  }

  public approve(approvedBy: string, reason?: string): void {
    this.status = 'approved';
    this.approvedBy = approvedBy;
    this.approvedAt = new Date();
    this.reason = reason;
  }

  public reject(rejectedBy: string, reason?: string): void {
    this.status = 'rejected';
    this.rejectedBy = rejectedBy;
    this.rejectedAt = new Date();
    this.reason = reason;
  }

  public cancel(): void {
    this.status = 'cancelled';
  }

  public toSafeJSON(): any {
    const values = Object.assign({}, this.get());
    // Remove sensitive data from parameters and context
    if (values.parameters && values.parameters.password) {
      delete values.parameters.password;
    }
    if (values.context && values.context.password) {
      delete values.context.password;
    }
    return values;
  }
}

ApprovalRequest.init(
  {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true,
    },
    userId: {
      type: DataTypes.UUID,
      allowNull: false,
      references: {
        model: 'users',
        key: 'id',
      },
    },
    commandId: {
      type: DataTypes.UUID,
      allowNull: true,
      references: {
        model: 'commands',
        key: 'id',
      },
    },
    action: {
      type: DataTypes.STRING,
      allowNull: false,
      validate: {
        len: [1, 255],
      },
    },
    description: {
      type: DataTypes.TEXT,
      allowNull: false,
    },
    riskScore: {
      type: DataTypes.FLOAT,
      allowNull: false,
      validate: {
        min: 0,
        max: 100,
      },
    },
    riskCategory: {
      type: DataTypes.ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'),
      allowNull: false,
    },
    context: {
      type: DataTypes.JSONB,
      allowNull: false,
      defaultValue: {},
    },
    parameters: {
      type: DataTypes.JSONB,
      allowNull: false,
      defaultValue: {},
    },
    status: {
      type: DataTypes.ENUM('pending', 'approved', 'rejected', 'expired', 'cancelled'),
      allowNull: false,
      defaultValue: 'pending',
    },
    approvedBy: {
      type: DataTypes.UUID,
      allowNull: true,
      references: {
        model: 'users',
        key: 'id',
      },
    },
    approvedAt: {
      type: DataTypes.DATE,
      allowNull: true,
    },
    rejectedBy: {
      type: DataTypes.UUID,
      allowNull: true,
      references: {
        model: 'users',
        key: 'id',
      },
    },
    rejectedAt: {
      type: DataTypes.DATE,
      allowNull: true,
    },
    reason: {
      type: DataTypes.TEXT,
      allowNull: true,
    },
    expiresAt: {
      type: DataTypes.DATE,
      allowNull: false,
    },
    priority: {
      type: DataTypes.ENUM('low', 'medium', 'high', 'critical'),
      allowNull: false,
      defaultValue: 'medium',
    },
    category: {
      type: DataTypes.ENUM('system', 'file', 'network', 'browser', 'application', 'security'),
      allowNull: false,
      defaultValue: 'system',
    },
  },
  {
    sequelize,
    tableName: 'approval_requests',
    indexes: [
      {
        fields: ['userId'],
      },
      {
        fields: ['commandId'],
      },
      {
        fields: ['status'],
      },
      {
        fields: ['riskCategory'],
      },
      {
        fields: ['priority'],
      },
      {
        fields: ['category'],
      },
      {
        fields: ['expiresAt'],
      },
      {
        fields: ['createdAt'],
      },
    ],
  }
);

export default ApprovalRequest;
