/**
 * Personality Service Tests
 */

import request from 'supertest';
import app from './index';

describe('Personality Service', () => {
  describe('Health Check', () => {
    it('should return healthy status', async () => {
      const response = await request(app)
        .get('/health')
        .expect(200);
      
      expect(response.body.status).toBe('healthy');
      expect(response.body.service).toBe('personality');
    });
  });

  describe('Personality Status', () => {
    it('should return personality status', async () => {
      const response = await request(app)
        .get('/personality/status')
        .expect(200);
      
      expect(response.body).toHaveProperty('traits');
      expect(response.body).toHaveProperty('mood');
      expect(response.body).toHaveProperty('preferences');
    });
  });

  describe('Personality Response', () => {
    it('should generate response to user input', async () => {
      const response = await request(app)
        .post('/personality/respond')
        .send({
          message: 'Hello JarvisX',
          context: { type: 'greeting' },
          userEmotion: 'friendly'
        })
        .expect(200);
      
      expect(response.body).toHaveProperty('response');
      expect(response.body).toHaveProperty('emotion');
      expect(typeof response.body.response).toBe('string');
    });
  });
});
