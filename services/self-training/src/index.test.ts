/**
 * Self-Training Service Tests
 */

import request from 'supertest';
import app from './index';

describe('Self-Training Service', () => {
  describe('Health Check', () => {
    it('should return healthy status', async () => {
      const response = await request(app)
        .get('/health')
        .expect(200);
      
      expect(response.body.status).toBe('healthy');
      expect(response.body.service).toBe('jarvisx-self-training');
    });
  });

  describe('Training Status', () => {
    it('should return training status', async () => {
      const response = await request(app)
        .get('/training/status')
        .expect(200);
      
      expect(response.body).toHaveProperty('isTraining');
      expect(response.body).toHaveProperty('trainingProgress');
      expect(response.body).toHaveProperty('lastTraining');
    });
  });

  describe('Start Training', () => {
    it('should start training session', async () => {
      const response = await request(app)
        .post('/training/start')
        .send({
          mode: 'incremental',
          priority: 'normal'
        })
        .expect(200);
      
      expect(response.body.success).toBe(true);
      expect(response.body).toHaveProperty('trainingId');
    });
  });

  describe('Pattern Analysis', () => {
    it('should analyze patterns', async () => {
      const response = await request(app)
        .get('/patterns/analyze')
        .expect(200);
      
      expect(response.body.success).toBe(true);
      expect(response.body).toHaveProperty('analysis');
    });
  });
});
