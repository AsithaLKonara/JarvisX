#!/usr/bin/env node

/**
 * Test Script for JarvisX Screen Intelligence
 * Demonstrates "click the blue button" functionality
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');

// Configuration
const PC_AGENT_URL = 'http://localhost:8004';
const SCREEN_ANALYZER_URL = 'http://localhost:8010';
const OCR_URL = 'http://localhost:8011';
const VISION_URL = 'http://localhost:8005';

// Test image (you can replace this with a real screenshot)
const TEST_IMAGE_PATH = './test-screenshot.png';

class ScreenIntelligenceTester {
  constructor() {
    this.testResults = [];
  }

  async runAllTests() {
    console.log('🚀 Starting JarvisX Screen Intelligence Tests\n');

    try {
      // Test 1: Check service health
      await this.testServiceHealth();

      // Test 2: OCR text extraction
      await this.testOCRTextExtraction();

      // Test 3: Vision element detection
      await this.testVisionElementDetection();

      // Test 4: Screen analysis
      await this.testScreenAnalysis();

      // Test 5: Find and click element
      await this.testFindAndClickElement();

      // Test 6: Get clickable elements
      await this.testGetClickableElements();

      // Print results
      this.printResults();

    } catch (error) {
      console.error('❌ Test suite failed:', error.message);
    }
  }

  async testServiceHealth() {
    console.log('🔍 Testing service health...');

    const services = [
      { name: 'PC Agent', url: `${PC_AGENT_URL}/health` },
      { name: 'Screen Analyzer', url: `${SCREEN_ANALYZER_URL}/health` },
      { name: 'OCR Service', url: `${OCR_URL}/health` },
      { name: 'Vision Service', url: `${VISION_URL}/health` }
    ];

    for (const service of services) {
      try {
        const response = await axios.get(service.url, { timeout: 5000 });
        if (response.data.status === 'healthy') {
          console.log(`✅ ${service.name}: Healthy`);
          this.testResults.push({ test: `${service.name} Health`, status: 'PASS' });
        } else {
          console.log(`❌ ${service.name}: Unhealthy`);
          this.testResults.push({ test: `${service.name} Health`, status: 'FAIL' });
        }
      } catch (error) {
        console.log(`❌ ${service.name}: Not responding`);
        this.testResults.push({ test: `${service.name} Health`, status: 'FAIL' });
      }
    }
    console.log('');
  }

  async testOCRTextExtraction() {
    console.log('🔍 Testing OCR text extraction...');

    try {
      // Create a simple test image with text
      const testImage = this.createTestImageWithText();
      
      const response = await axios.post(`${OCR_URL}/extract`, {
        image: testImage,
        options: {
          language: 'eng+sin',
          confidence_threshold: 60,
          preprocessing: true
        }
      });

      if (response.data.success) {
        console.log('✅ OCR text extraction: Working');
        console.log(`   Extracted text: "${response.data.data.text}"`);
        this.testResults.push({ test: 'OCR Text Extraction', status: 'PASS' });
      } else {
        console.log('❌ OCR text extraction: Failed');
        this.testResults.push({ test: 'OCR Text Extraction', status: 'FAIL' });
      }
    } catch (error) {
      console.log('❌ OCR text extraction: Error -', error.message);
      this.testResults.push({ test: 'OCR Text Extraction', status: 'FAIL' });
    }
    console.log('');
  }

  async testVisionElementDetection() {
    console.log('🔍 Testing Vision element detection...');

    try {
      const testImage = this.createTestImageWithElements();
      
      const response = await axios.post(`${VISION_URL}/analyze`, {
        image: testImage,
        prompt: 'Find all buttons and interactive elements on this screen',
        options: {
          includeElements: true,
          includeActions: true,
          includeContext: true
        }
      });

      if (response.data.success) {
        console.log('✅ Vision element detection: Working');
        console.log(`   Found ${response.data.data.elements?.length || 0} elements`);
        this.testResults.push({ test: 'Vision Element Detection', status: 'PASS' });
      } else {
        console.log('❌ Vision element detection: Failed');
        this.testResults.push({ test: 'Vision Element Detection', status: 'FAIL' });
      }
    } catch (error) {
      console.log('❌ Vision element detection: Error -', error.message);
      this.testResults.push({ test: 'Vision Element Detection', status: 'FAIL' });
    }
    console.log('');
  }

  async testScreenAnalysis() {
    console.log('🔍 Testing comprehensive screen analysis...');

    try {
      const testImage = this.createTestImageWithElements();
      
      const response = await axios.post(`${SCREEN_ANALYZER_URL}/analyze`, {
        image: testImage,
        options: {
          includeOCR: true,
          includeVision: true,
          language: 'eng+sin',
          confidenceThreshold: 60
        }
      });

      if (response.data.success) {
        console.log('✅ Screen analysis: Working');
        console.log(`   Description: ${response.data.data.description}`);
        console.log(`   Elements found: ${response.data.data.elements?.length || 0}`);
        console.log(`   Text extracted: ${response.data.data.text?.length || 0} characters`);
        this.testResults.push({ test: 'Screen Analysis', status: 'PASS' });
      } else {
        console.log('❌ Screen analysis: Failed');
        this.testResults.push({ test: 'Screen Analysis', status: 'FAIL' });
      }
    } catch (error) {
      console.log('❌ Screen analysis: Error -', error.message);
      this.testResults.push({ test: 'Screen Analysis', status: 'FAIL' });
    }
    console.log('');
  }

  async testFindAndClickElement() {
    console.log('🔍 Testing "click the blue button" functionality...');

    try {
      const testImage = this.createTestImageWithBlueButton();
      
      // First, find the blue button
      const findResponse = await axios.post(`${SCREEN_ANALYZER_URL}/find-element`, {
        image: testImage,
        description: 'blue button'
      });

      if (findResponse.data.success && findResponse.data.data.found) {
        console.log('✅ Blue button found: Working');
        console.log(`   Button position: (${findResponse.data.data.element.position.x}, ${findResponse.data.data.element.position.y})`);
        
        // Test clicking the element
        const clickResponse = await axios.post(`${PC_AGENT_URL}/screen/click-element`, {
          image: testImage,
          elementDescription: 'blue button'
        });

        if (clickResponse.data.success) {
          console.log('✅ Blue button click: Working');
          this.testResults.push({ test: 'Find and Click Blue Button', status: 'PASS' });
        } else {
          console.log('❌ Blue button click: Failed');
          this.testResults.push({ test: 'Find and Click Blue Button', status: 'FAIL' });
        }
      } else {
        console.log('❌ Blue button not found');
        this.testResults.push({ test: 'Find and Click Blue Button', status: 'FAIL' });
      }
    } catch (error) {
      console.log('❌ Find and click element: Error -', error.message);
      this.testResults.push({ test: 'Find and Click Blue Button', status: 'FAIL' });
    }
    console.log('');
  }

  async testGetClickableElements() {
    console.log('🔍 Testing clickable elements detection...');

    try {
      const testImage = this.createTestImageWithElements();
      
      const response = await axios.post(`${SCREEN_ANALYZER_URL}/clickable-elements`, {
        image: testImage
      });

      if (response.data.success) {
        console.log('✅ Clickable elements detection: Working');
        console.log(`   Found ${response.data.data.count} clickable elements`);
        this.testResults.push({ test: 'Clickable Elements Detection', status: 'PASS' });
      } else {
        console.log('❌ Clickable elements detection: Failed');
        this.testResults.push({ test: 'Clickable Elements Detection', status: 'FAIL' });
      }
    } catch (error) {
      console.log('❌ Clickable elements detection: Error -', error.message);
      this.testResults.push({ test: 'Clickable Elements Detection', status: 'FAIL' });
    }
    console.log('');
  }

  createTestImageWithText() {
    // Create a simple base64 encoded image with text
    // This is a placeholder - in a real test, you'd use an actual screenshot
    return 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';
  }

  createTestImageWithElements() {
    // Create a simple base64 encoded image with UI elements
    return 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';
  }

  createTestImageWithBlueButton() {
    // Create a simple base64 encoded image with a blue button
    return 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';
  }

  printResults() {
    console.log('📊 Test Results Summary:');
    console.log('========================\n');

    const passed = this.testResults.filter(r => r.status === 'PASS').length;
    const failed = this.testResults.filter(r => r.status === 'FAIL').length;
    const total = this.testResults.length;

    this.testResults.forEach(result => {
      const status = result.status === 'PASS' ? '✅' : '❌';
      console.log(`${status} ${result.test}: ${result.status}`);
    });

    console.log('\n========================');
    console.log(`Total: ${total} | Passed: ${passed} | Failed: ${failed}`);
    console.log(`Success Rate: ${Math.round((passed / total) * 100)}%`);

    if (failed === 0) {
      console.log('\n🎉 All tests passed! JarvisX Screen Intelligence is working perfectly!');
    } else {
      console.log('\n⚠️  Some tests failed. Check the service logs for details.');
    }
  }
}

// Run the tests
const tester = new ScreenIntelligenceTester();
tester.runAllTests().catch(console.error);
