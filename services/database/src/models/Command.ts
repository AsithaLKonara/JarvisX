/**
 * Command Model
 * Command execution history and tracking
 */

import { DataTypes, Model, Optional } from 'sequelize';
import { sequelize } from '../config/database';

export interface CommandAttributes {
  id: string;
  userId: string;
  type: 'voice' | 'click' | 'keyboard' | 'system' | 'browser' | 'approval';
  action: string;
  parameters: any;
  status: 'pending' | 'executing' | 'completed' | 'failed' | 'cancelled';
  result?: any;
  error?: string;
  executionTime?: number;
  confidence?: number;
  riskScore?: number;
  approvedBy?: string;
  approvedAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface CommandCreationAttributes extends Optional<CommandAttributes, 'id' | 'result' | 'error' | 'executionTime' | 'confidence' | 'riskScore' | 'approvedBy' | 'approvedAt'> {}

export class Command extends Model<CommandAttributes, CommandCreationAttributes> implements CommandAttributes {
  public id!: string;
  public userId!: string;
  public type!: 'voice' | 'click' | 'keyboard' | 'system' | 'browser' | 'approval';
  public action!: string;
  public parameters!: any;
  public status!: 'pending' | 'executing' | 'completed' | 'failed' | 'cancelled';
  public result?: any;
  public error?: string;
  public executionTime?: number;
  public confidence?: number;
  public riskScore?: number;
  public approvedBy?: string;
  public approvedAt?: Date;
  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;

  // Instance methods
  public isCompleted(): boolean {
    return this.status === 'completed';
  }

  public isFailed(): boolean {
    return this.status === 'failed';
  }

  public isPending(): boolean {
    return this.status === 'pending';
  }

  public isExecuting(): boolean {
    return this.status === 'executing';
  }

  public isHighRisk(): boolean {
    return (this.riskScore || 0) > 70;
  }

  public isApproved(): boolean {
    return !!this.approvedBy && !!this.approvedAt;
  }

  public getExecutionDuration(): number {
    if (this.executionTime) {
      return this.executionTime;
    }
    return Date.now() - this.createdAt.getTime();
  }

  public toSafeJSON(): any {
    const values = Object.assign({}, this.get());
    // Remove sensitive data from parameters
    if (values.parameters && values.parameters.password) {
      delete values.parameters.password;
    }
    return values;
  }
}

Command.init(
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
    type: {
      type: DataTypes.ENUM('voice', 'click', 'keyboard', 'system', 'browser', 'approval'),
      allowNull: false,
    },
    action: {
      type: DataTypes.STRING,
      allowNull: false,
      validate: {
        len: [1, 255],
      },
    },
    parameters: {
      type: DataTypes.JSONB,
      allowNull: false,
      defaultValue: {},
    },
    status: {
      type: DataTypes.ENUM('pending', 'executing', 'completed', 'failed', 'cancelled'),
      allowNull: false,
      defaultValue: 'pending',
    },
    result: {
      type: DataTypes.JSONB,
      allowNull: true,
    },
    error: {
      type: DataTypes.TEXT,
      allowNull: true,
    },
    executionTime: {
      type: DataTypes.INTEGER,
      allowNull: true,
      comment: 'Execution time in milliseconds',
    },
    confidence: {
      type: DataTypes.FLOAT,
      allowNull: true,
      validate: {
        min: 0,
        max: 100,
      },
    },
    riskScore: {
      type: DataTypes.FLOAT,
      allowNull: true,
      validate: {
        min: 0,
        max: 100,
      },
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
  },
  {
    sequelize,
    tableName: 'commands',
    indexes: [
      {
        fields: ['userId'],
      },
      {
        fields: ['type'],
      },
      {
        fields: ['status'],
      },
      {
        fields: ['createdAt'],
      },
      {
        fields: ['riskScore'],
      },
      {
        fields: ['approvedBy'],
      },
    ],
  }
);

export default Command;
