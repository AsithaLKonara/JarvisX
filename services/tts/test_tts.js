/**
 * Tests for TTS service
 */

const request = require('supertest');
const app = require('./main');

describe('TTS Service', () => {
  
  describe('GET /health', () => {
    it('should return health status', async () => {
      const response = await request(app)
        .get('/health')
        .expect(200);
      
      expect(response.body).toHaveProperty('status', 'healthy');
      expect(response.body).toHaveProperty('service', 'tts');
      expect(response.body).toHaveProperty('google_cloud_enabled');
      expect(response.body).toHaveProperty('festival_available');
    });
  });

  describe('GET /languages', () => {
    it('should return supported languages', async () => {
      const response = await request(app)
        .get('/languages')
        .expect(200);
      
      expect(response.body).toHaveProperty('supported_languages');
      expect(response.body).toHaveProperty('default', 'si');
      expect(response.body).toHaveProperty('festival_fallback', true);
      
      const languages = response.body.supported_languages;
      expect(languages).toEqual(
        expect.arrayContaining([
          expect.objectContaining({ code: 'si', name: 'Sinhala' }),
          expect.objectContaining({ code: 'en', name: 'English' })
        ])
      );
    });
  });

  describe('GET /voices', () => {
    it('should return available voices', async () => {
      const response = await request(app)
        .get('/voices')
        .expect(200);
      
      expect(response.body).toHaveProperty('voices');
      expect(response.body).toHaveProperty('recommended');
      
      const voices = response.body.voices;
      expect(voices).toHaveProperty('google_cloud');
      expect(voices).toHaveProperty('festival');
    });
  });

  describe('POST /synthesize', () => {
    it('should synthesize text to speech', async () => {
      const testText = 'Hello, this is a test message';
      
      const response = await request(app)
        .post('/synthesize')
        .send({
          text: testText,
          language: 'en',
          speed: 1.0
        })
        .expect(200);
      
      expect(response.headers['content-type']).toMatch(/audio\/wav/);
      expect(response.headers['content-length']).toBeDefined();
      expect(response.body).toBeInstanceOf(Buffer);
      expect(response.body.length).toBeGreaterThan(0);
    });

    it('should handle Sinhala text', async () => {
      const sinhalaText = 'ආයුබෝවන්, මේ පරීක්ෂණ පණිවිඩයක්';
      
      const response = await request(app)
        .post('/synthesize')
        .send({
          text: sinhalaText,
          language: 'si',
          speed: 1.0
        })
        .expect(200);
      
      expect(response.headers['content-type']).toMatch(/audio\/wav/);
      expect(response.body).toBeInstanceOf(Buffer);
    });

    it('should return 400 for missing text', async () => {
      const response = await request(app)
        .post('/synthesize')
        .send({
          language: 'en'
        })
        .expect(400);
      
      expect(response.body).toHaveProperty('error');
      expect(response.body.error).toContain('Text parameter is required');
    });

    it('should return 400 for invalid text type', async () => {
      const response = await request(app)
        .post('/synthesize')
        .send({
          text: 123,
          language: 'en'
        })
        .expect(400);
      
      expect(response.body).toHaveProperty('error');
    });

    it('should handle different speeds', async () => {
      const testText = 'This is a speed test';
      
      const speeds = [0.5, 1.0, 1.5, 2.0];
      
      for (const speed of speeds) {
        const response = await request(app)
          .post('/synthesize')
          .send({
            text: testText,
            language: 'en',
            speed: speed
          })
          .expect(200);
        
        expect(response.body).toBeInstanceOf(Buffer);
        expect(response.body.length).toBeGreaterThan(0);
      }
    });
  });

  describe('POST /synthesize-batch', () => {
    it('should synthesize multiple texts', async () => {
      const texts = [
        'First message',
        'Second message',
        'Third message'
      ];
      
      const response = await request(app)
        .post('/synthesize-batch')
        .send({
          texts: texts,
          language: 'en'
        })
        .expect(200);
      
      expect(response.body).toHaveProperty('results');
      expect(response.body).toHaveProperty('totalProcessed', 3);
      expect(response.body).toHaveProperty('successCount');
      
      const results = response.body.results;
      expect(results).toHaveLength(3);
      
      results.forEach((result, index) => {
        expect(result).toHaveProperty('index', index);
        expect(result).toHaveProperty('text', texts[index]);
        expect(result).toHaveProperty('status');
      });
    });

    it('should return 400 for invalid texts parameter', async () => {
      const response = await request(app)
        .post('/synthesize-batch')
        .send({
          texts: 'not an array',
          language: 'en'
        })
        .expect(400);
      
      expect(response.body).toHaveProperty('error');
      expect(response.body.error).toContain('Texts parameter must be an array');
    });

    it('should handle empty texts array', async () => {
      const response = await request(app)
        .post('/synthesize-batch')
        .send({
          texts: [],
          language: 'en'
        })
        .expect(200);
      
      expect(response.body.results).toHaveLength(0);
      expect(response.body.totalProcessed).toBe(0);
      expect(response.body.successCount).toBe(0);
    });
  });

  describe('Error handling', () => {
    it('should handle very long text gracefully', async () => {
      const longText = 'This is a very long text. '.repeat(1000);
      
      const response = await request(app)
        .post('/synthesize')
        .send({
          text: longText,
          language: 'en'
        });
      
      // Should either succeed or fail gracefully
      expect([200, 500, 413]).toContain(response.status);
    });

    it('should handle special characters', async () => {
      const specialText = 'Special chars: !@#$%^&*()_+-=[]{}|;:,.<>?';
      
      const response = await request(app)
        .post('/synthesize')
        .send({
          text: specialText,
          language: 'en'
        });
      
      // Should handle special characters gracefully
      expect([200, 500]).toContain(response.status);
    });
  });
});

// Integration test helper
async function testEndToEndFlow() {
  console.log('Testing end-to-end TTS flow...');
  
  try {
    // Test health check
    const healthResponse = await request(app).get('/health');
    console.log('Health check:', healthResponse.body);
    
    // Test language support
    const languagesResponse = await request(app).get('/languages');
    console.log('Supported languages:', languagesResponse.body.supported_languages.length);
    
    // Test synthesis
    const synthesisResponse = await request(app)
      .post('/synthesize')
      .send({
        text: 'Test synthesis',
        language: 'en'
      });
    
    console.log('Synthesis test:', synthesisResponse.status === 200 ? 'PASSED' : 'FAILED');
    
    return true;
  } catch (error) {
    console.error('Integration test failed:', error.message);
    return false;
  }
}

if (require.main === module) {
  testEndToEndFlow().then(success => {
    process.exit(success ? 0 : 1);
  });
}
