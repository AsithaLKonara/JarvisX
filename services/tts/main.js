/**
 * JarvisX TTS Service
 * Text-to-Speech service with Google Cloud TTS and Festival fallback
 */

const express = require('express');
const cors = require('cors');
const multer = require('multer');
const fs = require('fs').promises;
const path = require('path');
const { spawn } = require('child_process');
const textToSpeech = require('@google-cloud/text-to-speech');

const app = express();
const PORT = process.env.PORT || 8000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Configure multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({ storage });

// Initialize Google Cloud TTS client
let ttsClient = null;
try {
  if (process.env.GOOGLE_CLOUD_KEY) {
    const credentials = JSON.parse(process.env.GOOGLE_CLOUD_KEY);
    ttsClient = new textToSpeech.TextToSpeechClient({
      credentials
    });
    console.log('Google Cloud TTS client initialized');
  } else {
    console.log('Google Cloud TTS not configured, using Festival fallback');
  }
} catch (error) {
  console.error('Failed to initialize Google Cloud TTS:', error.message);
  console.log('Falling back to Festival TTS');
}

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'tts',
    google_cloud_enabled: ttsClient !== null,
    festival_available: checkFestivalAvailability()
  });
});

/**
 * Synthesize text to speech
 */
app.post('/synthesize', async (req, res) => {
  try {
    const { text, language = 'si', voice = 'default', speed = 1.0 } = req.body;

    if (!text || typeof text !== 'string') {
      return res.status(400).json({
        error: 'Text parameter is required and must be a string'
      });
    }

    console.log(`Synthesizing text: "${text.substring(0, 100)}..." (${language})`);

    let audioBuffer;
    
    // Try Google Cloud TTS first if available
    if (ttsClient && language === 'si') {
      try {
        audioBuffer = await synthesizeWithGoogleCloud(text, language, voice, speed);
      } catch (error) {
        console.warn('Google Cloud TTS failed, falling back to Festival:', error.message);
        audioBuffer = await synthesizeWithFestival(text, language, speed);
      }
    } else {
      // Use Festival for other languages or when Google Cloud is not available
      audioBuffer = await synthesizeWithFestival(text, language, speed);
    }

    res.set({
      'Content-Type': 'audio/wav',
      'Content-Length': audioBuffer.length,
      'Content-Disposition': `attachment; filename="synthesized_${Date.now()}.wav"`
    });

    res.send(audioBuffer);

  } catch (error) {
    console.error('TTS synthesis failed:', error);
    res.status(500).json({
      error: 'Synthesis failed',
      message: error.message
    });
  }
});

/**
 * Synthesize with Google Cloud TTS
 */
async function synthesizeWithGoogleCloud(text, language, voice, speed) {
  const request = {
    input: { text },
    voice: {
      languageCode: getGoogleCloudLanguageCode(language),
      name: voice === 'default' ? undefined : voice,
      ssmlGender: 'NEUTRAL'
    },
    audioConfig: {
      audioEncoding: 'LINEAR16',
      speakingRate: speed
    }
  };

  const [response] = await ttsClient.synthesizeSpeech(request);
  return response.audioContent;
}

/**
 * Synthesize with Festival TTS
 */
async function synthesizeWithFestival(text, language, speed) {
  return new Promise((resolve, reject) => {
    const tempInputFile = `/tmp/festival_input_${Date.now()}.txt`;
    const tempOutputFile = `/tmp/festival_output_${Date.now()}.wav`;

    // Write text to temporary file
    fs.writeFile(tempInputFile, text)
      .then(() => {
        // Run Festival command
        const festivalCmd = `echo "(Parameter.set 'Duration_Stretch ${speed})" | cat - ${tempInputFile} | festival --tts --pipe > ${tempOutputFile}`;
        
        const child = spawn('bash', ['-c', festivalCmd]);

        child.on('close', async (code) => {
          try {
            if (code === 0) {
              const audioBuffer = await fs.readFile(tempOutputFile);
              resolve(audioBuffer);
            } else {
              reject(new Error(`Festival command failed with code ${code}`));
            }
          } catch (error) {
            reject(error);
          } finally {
            // Clean up temporary files
            try {
              await fs.unlink(tempInputFile);
              await fs.unlink(tempOutputFile);
            } catch (cleanupError) {
              console.warn('Failed to clean up temporary files:', cleanupError.message);
            }
          }
        });

        child.on('error', reject);
      })
      .catch(reject);
  });
}

/**
 * Check if Festival is available
 */
function checkFestivalAvailability() {
  try {
    const { execSync } = require('child_process');
    execSync('which festival', { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

/**
 * Get Google Cloud language code
 */
function getGoogleCloudLanguageCode(language) {
  const languageMap = {
    'si': 'si-LK',  // Sinhala (Sri Lanka)
    'en': 'en-US',  // English (US)
    'ta': 'ta-IN',  // Tamil (India)
    'hi': 'hi-IN'   // Hindi (India)
  };
  return languageMap[language] || 'en-US';
}

/**
 * Get available voices
 */
app.get('/voices', (req, res) => {
  const voices = {
    google_cloud: ttsClient ? [
      { id: 'si-LK-Wavenet-A', name: 'Sinhala Female', language: 'si', gender: 'female' },
      { id: 'si-LK-Wavenet-B', name: 'Sinhala Male', language: 'si', gender: 'male' },
      { id: 'en-US-Wavenet-A', name: 'English Female', language: 'en', gender: 'female' },
      { id: 'en-US-Wavenet-B', name: 'English Male', language: 'en', gender: 'male' }
    ] : [],
    festival: [
      { id: 'default', name: 'Festival Default', language: 'en', gender: 'neutral' }
    ]
  };

  res.json({
    voices,
    recommended: {
      si: ttsClient ? 'si-LK-Wavenet-A' : 'default',
      en: ttsClient ? 'en-US-Wavenet-A' : 'default'
    }
  });
});

/**
 * Batch synthesis endpoint
 */
app.post('/synthesize-batch', async (req, res) => {
  try {
    const { texts, language = 'si', voice = 'default', speed = 1.0 } = req.body;

    if (!Array.isArray(texts)) {
      return res.status(400).json({
        error: 'Texts parameter must be an array'
      });
    }

    const results = [];
    
    for (let i = 0; i < texts.length; i++) {
      try {
        const audioBuffer = await synthesizeWithGoogleCloud(texts[i], language, voice, speed);
        results.push({
          index: i,
          text: texts[i],
          status: 'success',
          audioLength: audioBuffer.length
        });
      } catch (error) {
        results.push({
          index: i,
          text: texts[i],
          status: 'error',
          error: error.message
        });
      }
    }

    res.json({
      results,
      totalProcessed: results.length,
      successCount: results.filter(r => r.status === 'success').length
    });

  } catch (error) {
    console.error('Batch synthesis failed:', error);
    res.status(500).json({
      error: 'Batch synthesis failed',
      message: error.message
    });
  }
});

/**
 * Supported languages endpoint
 */
app.get('/languages', (req, res) => {
  res.json({
    supported_languages: [
      { code: 'si', name: 'Sinhala', google_cloud: !!ttsClient },
      { code: 'en', name: 'English', google_cloud: !!ttsClient },
      { code: 'ta', name: 'Tamil', google_cloud: !!ttsClient },
      { code: 'hi', name: 'Hindi', google_cloud: !!ttsClient }
    ],
    default: 'si',
    festival_fallback: true
  });
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Unhandled error:', error);
  res.status(500).json({
    error: 'Internal server error',
    message: error.message
  });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`JarvisX TTS Service running on port ${PORT}`);
  console.log(`Google Cloud TTS: ${ttsClient ? 'Enabled' : 'Disabled'}`);
  console.log(`Festival TTS: ${checkFestivalAvailability() ? 'Available' : 'Not available'}`);
});

module.exports = app;
