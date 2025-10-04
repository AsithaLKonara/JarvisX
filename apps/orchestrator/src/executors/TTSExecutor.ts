/**
 * TTS Executor for JarvisX Orchestrator
 * Handles text-to-speech operations
 */

import axios from 'axios';

export class TTSExecutor {
  private ttsServiceUrl: string;

  constructor() {
    this.ttsServiceUrl = process.env.TTS_SERVICE_URL || 'http://localhost:8002';
  }

  /**
   * Execute a TTS step
   */
  public async execute(step: any, dryRun: boolean = false): Promise<any> {
    const { action, params } = step;

    try {
      console.log(`🔊 TTS executor: ${action} (dry_run: ${dryRun})`);

      if (dryRun) {
        return this.getDryRunResult(action, params);
      }

      switch (action) {
        case 'synthesize':
          return await this.synthesize(params.text, params.language, params.voice);
        
        case 'synthesize_and_save':
          return await this.synthesizeAndSave(params.text, params.language, params.output_path);
        
        case 'batch_synthesize':
          return await this.batchSynthesize(params.texts, params.language);
        
        default:
          throw new Error(`Unknown TTS action: ${action}`);
      }

    } catch (error: any) {
      console.error(`❌ TTS executor failed: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get dry run result for TTS actions
   */
  private getDryRunResult(action: string, params: any): any {
    return {
      action,
      params,
      dry_run: true,
      description: this.getActionDescription(action, params)
    };
  }

  /**
   * Get human-readable description of action
   */
  private getActionDescription(action: string, params: any): string {
    switch (action) {
      case 'synthesize':
        return `Synthesize speech: "${params.text.substring(0, 50)}..." in ${params.language}`;
      case 'synthesize_and_save':
        return `Synthesize and save: "${params.text.substring(0, 50)}..." to ${params.output_path}`;
      case 'batch_synthesize':
        return `Batch synthesize ${params.texts.length} texts in ${params.language}`;
      default:
        return `Execute ${action}`;
    }
  }

  /**
   * Synthesize text to speech
   */
  private async synthesize(text: string, language: string = 'si', voice?: string): Promise<any> {
    console.log(`🔊 Synthesizing text in ${language}`);

    try {
      const response = await axios.post(
        `${this.ttsServiceUrl}/synthesize`,
        {
          text,
          language,
          voice: voice || 'default',
          speed: 1.0
        },
        {
          responseType: 'arraybuffer',
          timeout: 30000
        }
      );

      const audioBuffer = Buffer.from(response.data);

      return {
        success: true,
        action: 'synthesize',
        text: text.substring(0, 100),
        language,
        voice,
        audio_size: audioBuffer.length,
        audio_buffer: audioBuffer.toString('base64')
      };

    } catch (error: any) {
      throw new Error(`Failed to synthesize speech: ${error.response?.data?.error || error.message}`);
    }
  }

  /**
   * Synthesize text and save to file
   */
  private async synthesizeAndSave(text: string, language: string, outputPath: string): Promise<any> {
    console.log(`🔊 Synthesizing and saving to ${outputPath}`);

    const result = await this.synthesize(text, language);

    if (result.success) {
      const fs = await import('fs/promises');
      const audioBuffer = Buffer.from(result.audio_buffer, 'base64');
      
      await fs.writeFile(outputPath, audioBuffer);
      
      return {
        success: true,
        action: 'synthesize_and_save',
        text: text.substring(0, 100),
        language,
        output_path: outputPath,
        file_size: audioBuffer.length
      };
    }

    throw new Error('Synthesis failed');
  }

  /**
   * Batch synthesize multiple texts
   */
  private async batchSynthesize(texts: string[], language: string): Promise<any> {
    console.log(`🔊 Batch synthesizing ${texts.length} texts`);

    try {
      const response = await axios.post(
        `${this.ttsServiceUrl}/synthesize-batch`,
        {
          texts,
          language,
          speed: 1.0
        },
        {
          timeout: 60000
        }
      );

      return {
        success: true,
        action: 'batch_synthesize',
        language,
        texts_count: texts.length,
        results: response.data.results,
        success_count: response.data.successCount
      };

    } catch (error: any) {
      throw new Error(`Failed to batch synthesize: ${error.response?.data?.error || error.message}`);
    }
  }

  /**
   * Get available voices
   */
  public async getAvailableVoices(): Promise<any> {
    try {
      const response = await axios.get(`${this.ttsServiceUrl}/voices`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to get available voices:', error);
      return { voices: {}, recommended: {} };
    }
  }

  /**
   * Get supported languages
   */
  public async getSupportedLanguages(): Promise<any> {
    try {
      const response = await axios.get(`${this.ttsServiceUrl}/languages`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to get supported languages:', error);
      return { supported_languages: [], default: 'si' };
    }
  }

  /**
   * Check if TTS service is available
   */
  public async isServiceAvailable(): Promise<boolean> {
    try {
      const response = await axios.get(`${this.ttsServiceUrl}/health`, { timeout: 5000 });
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }

  /**
   * Check if TTS service is configured
   */
  public isConfigured(): boolean {
    return !!(this.ttsServiceUrl);
  }
}
