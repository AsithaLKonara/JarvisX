/**
 * Database Configuration
 * PostgreSQL and Redis connection setup
 */

import { Sequelize } from 'sequelize';
import { createClient } from 'redis';
import dotenv from 'dotenv';

dotenv.config();

// PostgreSQL Configuration
export const sequelize = new Sequelize({
  database: process.env.POSTGRES_DB || 'jarvisx',
  username: process.env.POSTGRES_USER || 'jarvisx',
  password: process.env.POSTGRES_PASSWORD || 'jarvisx123',
  host: process.env.POSTGRES_HOST || 'localhost',
  port: parseInt(process.env.POSTGRES_PORT || '5432'),
  dialect: 'postgres',
  logging: process.env.NODE_ENV === 'development' ? console.log : false,
  pool: {
    max: 20,
    min: 0,
    acquire: 30000,
    idle: 10000
  },
  define: {
    timestamps: true,
    underscored: true,
    freezeTableName: true
  }
});

// Redis Configuration
export const redisClient = createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379',
  password: process.env.REDIS_PASSWORD,
  database: parseInt(process.env.REDIS_DB || '0')
});

// Redis connection event handlers
redisClient.on('connect', () => {
  console.log('✅ Redis connected');
});

redisClient.on('error', (err) => {
  console.error('❌ Redis connection error:', err);
});

redisClient.on('disconnect', () => {
  console.log('🔌 Redis disconnected');
});

// Database connection functions
export const connectDatabase = async (): Promise<void> => {
  try {
    await sequelize.authenticate();
    console.log('✅ PostgreSQL connection established successfully');
  } catch (error) {
    console.error('❌ Unable to connect to PostgreSQL:', error);
    throw error;
  }
};

export const connectRedis = async (): Promise<void> => {
  try {
    await redisClient.connect();
    console.log('✅ Redis connection established successfully');
  } catch (error) {
    console.error('❌ Unable to connect to Redis:', error);
    throw error;
  }
};

export const disconnectDatabase = async (): Promise<void> => {
  try {
    await sequelize.close();
    console.log('✅ PostgreSQL connection closed');
  } catch (error) {
    console.error('❌ Error closing PostgreSQL connection:', error);
  }
};

export const disconnectRedis = async (): Promise<void> => {
  try {
    await redisClient.disconnect();
    console.log('✅ Redis connection closed');
  } catch (error) {
    console.error('❌ Error closing Redis connection:', error);
  }
};

// Database health check
export const checkDatabaseHealth = async (): Promise<{
  postgres: boolean;
  redis: boolean;
  timestamp: string;
}> => {
  const timestamp = new Date().toISOString();
  
  let postgres = false;
  let redis = false;
  
  try {
    await sequelize.authenticate();
    postgres = true;
  } catch (error) {
    console.error('❌ PostgreSQL health check failed:', error);
  }
  
  try {
    await redisClient.ping();
    redis = true;
  } catch (error) {
    console.error('❌ Redis health check failed:', error);
  }
  
  return {
    postgres,
    redis,
    timestamp
  };
};

export default {
  sequelize,
  redisClient,
  connectDatabase,
  connectRedis,
  disconnectDatabase,
  disconnectRedis,
  checkDatabaseHealth
};
