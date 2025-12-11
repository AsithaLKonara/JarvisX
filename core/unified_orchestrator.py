#!/usr/bin/env python3
"""
Unified Orchestrator - Main orchestrator connecting all features
STT → AI Understanding → Action Extraction → Tool Execution → TTS Response
"""

import logging
from typing import Dict, Any, Optional, List
from core.action_extractor import ActionExtractor, ExtractedAction
from core.tool_router import ToolRouter
from core.response_formatter import ResponseFormatter

logger = logging.getLogger(__name__)


class UnifiedOrchestrator:
    """
    Unified orchestrator that connects all features:
    - STT (Speech-to-Text)
    - AI Understanding (HybridBrain)
    - Action Extraction
    - Tool Routing & Execution
    - Response Formatting
    - TTS (Text-to-Speech)
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize unified orchestrator
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self._initialize_components()
        
        self.logger.info("✅ Unified Orchestrator initialized")
    
    def _initialize_components(self):
        """Initialize all orchestrator components"""
        # Initialize AI Brain
        try:
            from core.hybrid_brain import HybridBrain
            self.ai_brain = HybridBrain(self.config)
            self.ai_available = True
            self.logger.info("✅ HybridBrain loaded")
        except Exception as e:
            self.ai_brain = None
            self.ai_available = False
            self.logger.warning(f"HybridBrain not available: {e}")
        
        # Initialize STT
        try:
            from speech.speech_recognizer import SpeechRecognizer
            self.stt = SpeechRecognizer(use_offline=False, enable_noise_reduction=True)
            self.stt_available = self.stt.is_available
            self.logger.info(f"✅ SpeechRecognizer loaded (available: {self.stt_available})")
        except Exception as e:
            self.stt = None
            self.stt_available = False
            self.logger.warning(f"SpeechRecognizer not available: {e}")
        
        # Initialize TTS
        try:
            from speech.text_to_speech import TTSEngine
            import os
            tts_engine = os.getenv('TTS_ENGINE', 'pyttsx3')
            self.tts = TTSEngine(engine=tts_engine)
            self.tts_available = self.tts.is_available
            self.logger.info(f"✅ TTSEngine loaded (available: {self.tts_available})")
        except Exception as e:
            self.tts = None
            self.tts_available = False
            self.logger.warning(f"TTSEngine not available: {e}")
        
        # Initialize action extractor
        self.action_extractor = ActionExtractor()
        
        # Initialize tool router
        self.tool_router = ToolRouter()
        
        # Initialize response formatter
        self.response_formatter = ResponseFormatter()
    
    def process_voice_command(
        self,
        voice_input: Optional[str] = None,
        text_input: Optional[str] = None,
        enable_tts: bool = True
    ) -> Dict[str, Any]:
        """
        Process voice or text command through complete pipeline
        
        Args:
            voice_input: Voice input (if None, will listen via STT)
            text_input: Direct text input (alternative to voice)
            enable_tts: Whether to speak the response
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Step 1: Get input (STT or text)
            user_input = self._get_user_input(voice_input, text_input)
            if not user_input:
                return {
                    'success': False,
                    'error': 'No input received',
                    'response': "I didn't catch that. Could you repeat?"
                }
            
            self.logger.info(f"📥 User input: {user_input}")
            
            # Step 2: Get AI understanding
            ai_response = self._get_ai_response(user_input)
            if not ai_response:
                return {
                    'success': False,
                    'error': 'AI response failed',
                    'response': "I'm having trouble understanding that. Could you rephrase?"
                }
            
            self.logger.info(f"🧠 AI response: {ai_response[:200]}...")
            
            # Step 3: Extract actions
            actions = self.action_extractor.extract_actions(ai_response, user_input)
            
            # Step 4: Execute actions if any
            execution_results = []
            if actions:
                self.logger.info(f"🔧 Extracted {len(actions)} actions")
                for action in actions:
                    result = self.tool_router.route_action(action)
                    execution_results.append({
                        'action': action,
                        'result': result
                    })
            
            # Step 5: Format response
            if execution_results:
                # Format based on execution results
                response = self._format_execution_response(execution_results, ai_response)
            else:
                # No actions, just conversational response
                response = self.response_formatter.format_conversational_response(
                    ai_response,
                    has_actions=False
                )
            
            # Step 6: TTS output
            if enable_tts and self.tts_available:
                self._speak_response(response)
            
            return {
                'success': True,
                'user_input': user_input,
                'ai_response': ai_response,
                'actions': [a.tool for a in actions],
                'execution_results': execution_results,
                'response': response
            }
        
        except Exception as e:
            self.logger.error(f"Error processing command: {e}", exc_info=True)
            error_response = f"I encountered an error: {str(e)}"
            
            if enable_tts and self.tts_available:
                self._speak_response(error_response)
            
            return {
                'success': False,
                'error': str(e),
                'response': error_response
            }
    
    def _get_user_input(
        self,
        voice_input: Optional[str],
        text_input: Optional[str]
    ) -> Optional[str]:
        """Get user input from voice or text"""
        if text_input:
            return text_input.strip()
        
        if voice_input:
            return voice_input.strip()
        
        # Try to listen via STT
        if self.stt_available and self.stt:
            try:
                self.logger.info("🎤 Listening for voice input...")
                text = self.stt.listen(timeout=10)
                if text:
                    return text.strip()
            except Exception as e:
                self.logger.warning(f"STT listening failed: {e}")
        
        return None
    
    def _get_ai_response(self, user_input: str) -> Optional[str]:
        """Get AI response from HybridBrain"""
        if not self.ai_available or not self.ai_brain:
            return None
        
        try:
            # Enhance prompt to encourage action extraction
            enhanced_prompt = self._enhance_prompt_for_actions(user_input)
            response = self.ai_brain.get_response(enhanced_prompt)
            return response
        except Exception as e:
            self.logger.error(f"AI response failed: {e}")
            return None
    
    def _enhance_prompt_for_actions(self, user_input: str) -> str:
        """Enhance user prompt to encourage structured action responses"""
        # Add instruction for action extraction
        enhanced = f"""{user_input}

If this request requires any actions (like checking system status, creating files, running commands, etc.), please indicate what actions should be taken. You can respond naturally, and I'll extract the actions from your response."""
        return enhanced
    
    def _format_execution_response(
        self,
        execution_results: List[Dict],
        ai_response: str
    ) -> str:
        """Format response from execution results"""
        if not execution_results:
            return ai_response
        
        # Check if all succeeded
        all_success = all(r['result'].get('success', False) for r in execution_results)
        
        if all_success and len(execution_results) == 1:
            # Single successful action - format it
            action = execution_results[0]['action']
            result = execution_results[0]['result']
            return self.response_formatter.format_action_result(
                action.action_type,
                action.tool,
                result,
                action.original_text
            )
        elif all_success:
            # Multiple successful actions
            formatted_results = []
            for exec_result in execution_results:
                action = exec_result['action']
                result = exec_result['result']
                formatted = self.response_formatter.format_action_result(
                    action.action_type,
                    action.tool,
                    result
                )
                formatted_results.append(formatted)
            
            return ". ".join(formatted_results)
        else:
            # Some failures
            success_count = sum(1 for r in execution_results if r['result'].get('success', False))
            total_count = len(execution_results)
            
            if success_count > 0:
                return f"I completed {success_count} out of {total_count} actions. {ai_response}"
            else:
                return f"I couldn't complete the requested actions. {ai_response}"
    
    def _speak_response(self, response: str):
        """Speak response using TTS"""
        if not self.tts_available or not self.tts:
            return
        
        try:
            # Truncate very long responses for TTS
            tts_text = response[:500] if len(response) > 500 else response
            self.tts.speak(tts_text, blocking=False)
        except Exception as e:
            self.logger.warning(f"TTS failed: {e}")
    
    def process_text_command(self, text: str, enable_tts: bool = True) -> Dict[str, Any]:
        """Process text command (convenience method)"""
        return self.process_voice_command(text_input=text, enable_tts=enable_tts)
    
    def process_voice_only(self, enable_tts: bool = True) -> Dict[str, Any]:
        """Process voice-only command (listens via STT)"""
        return self.process_voice_command(enable_tts=enable_tts)
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            'ai_available': self.ai_available,
            'stt_available': self.stt_available,
            'tts_available': self.tts_available,
            'tools_available': self.tool_router.get_available_tools()
        }

