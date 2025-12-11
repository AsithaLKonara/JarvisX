#!/usr/bin/env python3
"""
Jarvis X V2 - Hybrid Brain System
Combines Custom LLM (Mistral 7B) with HelaGPT for optimal performance
"""

import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime
import time
import json
import re

logger = logging.getLogger(__name__)


class TaskType:
	"""Task classification for routing decisions"""
	# Complex tasks -> Custom LLM
	CODE_ANALYSIS = "code_analysis"
	ENGINEERING = "engineering"
	DESIGN = "design"
	VIDEO_EDITING = "video_editing"
	BUSINESS = "business"
	SYSTEM_MONITORING = "system_monitoring"
	TECHNICAL = "technical"
	
	# Simple tasks -> HelaGPT
	CASUAL_CHAT = "casual_chat"
	GREETING = "greeting"
	SINHALA = "sinhala"
	SIMPLE_QUESTION = "simple_question"
	
	# Unknown -> Try LLM first, fallback to HelaGPT
	UNKNOWN = "unknown"


class HybridBrain:
	"""
	Hybrid AI Brain that intelligently routes tasks between:
	- Custom LLM (Mistral 7B with LoRA) for complex tasks
	- HelaGPT for casual chat and Sinhala support
	"""
	
	def __init__(self, config: Optional[Dict] = None):
		"""Initialize Hybrid Brain System"""
		self.config = config
		self.logger = logging.getLogger(__name__)
		
		# Feature flags
		self.disable_helagpt = os.getenv("DISABLE_HELAGPT", "false").lower() == "true"
		
		# Statistics
		self.stats = {
			'llm_calls': 0,
			'helagpt_calls': 0,
			'llm_failures': 0,
			'helagpt_failures': 0,
			'total_calls': 0,
			'fallback_used': 0,
			'actions_executed': 0
		}
		
		# State
		self.current_state = "IDLE"
		self.last_brain_used = None
		self.conversation_history = []
		
		# Initialize brains
		self._initialize_brains()
		
		# Initialize computer access
		self._initialize_computer_access()
		
		self.logger.info("✅ Hybrid Brain System initialized")
	
	def _initialize_brains(self):
		"""Initialize both brain systems"""
		# Initialize HelaGPT (skip if disabled)
		if not self.disable_helagpt:
			try:
				from core.ai_engine import AIEngine
				from utils.config import Config
				
				self.helagpt = AIEngine(self.config or Config())
				self.helagpt_available = True
				self.logger.info("✅ HelaGPT brain loaded")
			except Exception as e:
				self.helagpt = None
				self.helagpt_available = False
				self.logger.error(f"❌ HelaGPT initialization failed: {e}")
		else:
			self.helagpt = None
			self.helagpt_available = False
			self.logger.info("⏸️  HelaGPT disabled via DISABLE_HELAGPT=true")
		
		# Try to initialize Custom LLM (may not be available yet)
		try:
			from jarvis_llm_brain import JarvisLLMBrain
			
			self.custom_llm = JarvisLLMBrain()
			self.llm_available = True
			self.logger.info("✅ Custom LLM brain loaded")
		except Exception as e:
			self.custom_llm = None
			self.llm_available = False
			self.logger.warning(f"⚠️  Custom LLM not available (will use HelaGPT only): {e}")
	
	def _initialize_computer_access(self):
		"""Initialize computer access layer"""
		try:
			from core.computer_access import ComputerAccessLayer
			
			self.computer_access = ComputerAccessLayer(
				safety_mode=True,
				auto_confirm_safe=True
			)
			self.has_computer_access = True
			self.logger.info("✅ Computer Access Layer loaded")
		except Exception as e:
			self.computer_access = None
			self.has_computer_access = False
			self.logger.warning(f"⚠️  Computer Access Layer not available: {e}")
	
	def classify_task(self, user_input: str) -> str:
		"""
		Classify the task type based on user input.
		Determines which brain should handle the request.
		"""
		user_input_lower = user_input.lower()
		
		# Check for Sinhala text (Unicode range for Sinhala: 0D80-0DFF)
		has_sinhala = any('\u0D80' <= char <= '\u0DFF' for char in user_input)
		if has_sinhala and not self.disable_helagpt:
			return TaskType.SINHALA
		
		# Greetings -> HelaGPT
		greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 
					'good evening', 'howdy', 'greetings']
		if any(greeting in user_input_lower for greeting in greetings) and not self.disable_helagpt:
			return TaskType.GREETING
		
		# Code/Engineering -> Custom LLM
		code_keywords = ['code', 'debug', 'function', 'class', 'variable', 'algorithm',
						'python', 'javascript', 'analyze', 'refactor', 'optimize',
						'bug', 'error', 'compile', 'syntax', 'implement']
		if any(keyword in user_input_lower for keyword in code_keywords):
			return TaskType.ENGINEERING
		
		# Design -> Custom LLM
		design_keywords = ['design', 'ui', 'ux', 'interface', 'layout', 'color',
					  'typography', 'mockup', 'wireframe', 'prototype']
		if any(keyword in user_input_lower for keyword in design_keywords):
			return TaskType.DESIGN
		
		# Video Editing -> Custom LLM
		video_keywords = ['video', 'edit', 'clip', 'caption', 'subtitle', 'render',
						 'export', 'trim', 'cut', 'transition', 'effect']
		if any(keyword in user_input_lower for keyword in video_keywords):
			return TaskType.VIDEO_EDITING
		
		# Business -> Custom LLM
		business_keywords = ['invoice', 'report', 'finance', 'budget', 'revenue',
					   'expense', 'client', 'project', 'task', 'deadline',
					   'business', 'crm', 'analytics']
		if any(keyword in user_input_lower for keyword in business_keywords):
			return TaskType.BUSINESS
		
		# System Monitoring -> Custom LLM
		system_keywords = ['monitor', 'performance', 'cpu', 'memory', 'disk',
					  'network', 'process', 'system', 'resource', 'usage']
		if any(keyword in user_input_lower for keyword in system_keywords):
			return TaskType.SYSTEM_MONITORING
		
		# Technical questions -> Custom LLM
		technical_indicators = ['how to', 'what is', 'explain', 'why does',
						   'how can i', 'tutorial', 'guide']
		if any(indicator in user_input_lower for indicator in technical_indicators):
			return TaskType.TECHNICAL
		
		# Simple/Casual -> HelaGPT (only if enabled)
		casual_indicators = ['thank', 'thanks', 'bye', 'goodbye', 'see you',
					   'joke', 'story', 'fun', 'cool', 'awesome']
		if any(indicator in user_input_lower for indicator in casual_indicators) and not self.disable_helagpt:
			return TaskType.CASUAL_CHAT
		
		# Short messages -> HelaGPT (only if enabled)
		if len(user_input.split()) <= 5 and not self.disable_helagpt:
			return TaskType.SIMPLE_QUESTION
		
		# Default: Try LLM first, fallback to HelaGPT
		return TaskType.UNKNOWN
	
	def get_response(self, user_input: str) -> str:
		"""
		Get intelligent response by routing to appropriate brain.
		
		Routing Logic:
		1. Check if requires computer access action
		2. Execute action if needed and return results
		3. Otherwise, classify task type
		4. Route to Custom LLM for complex tasks
		5. Route to HelaGPT for casual/Sinhala (if enabled)
		6. Fallback to other brain if primary fails
		"""
		try:
			self.current_state = "PROCESSING"
			self.stats['total_calls'] += 1
			start_time = time.time()
			
			# Classify the task
			task_type = self.classify_task(user_input)
			self.logger.info(f"📋 Task classified as: {task_type}")
			
			# Check if this requires computer access
			computer_action = self._detect_computer_action(user_input, task_type)
			if computer_action and self.has_computer_access:
				# Execute actual computer action
				action_result = self.computer_access.execute_action(
					computer_action['action_type'],
					computer_action.get('parameters', {})
				)
				
				if action_result['success']:
					self.stats['actions_executed'] += 1
					# Format action result into natural response
					response = self._format_action_response(computer_action, action_result)
					
					# Update history
					elapsed = time.time() - start_time
					self._update_history(user_input, response, task_type, elapsed, action_executed=True)
					
					self.current_state = "IDLE"
					return response
			
			# No computer action needed - get conversational response
			# Routing decision
			use_llm = self._should_use_llm(task_type)
			
			# Get response from appropriate brain
			response = None
			if use_llm and self.llm_available:
				response = self._get_llm_response(user_input, task_type)
			
			# Fallback to HelaGPT if LLM failed or not available and not disabled
			if response is None and self.helagpt_available and not self.disable_helagpt:
				response = self._get_helagpt_response(user_input, task_type)
			
			# Final fallback
			if response is None:
				response = self._get_emergency_fallback(user_input)
			
			# Update history
			elapsed = time.time() - start_time
			self._update_history(user_input, response, task_type, elapsed)
			
			self.current_state = "IDLE"
			return response
			
		except Exception as e:
			self.logger.error(f"❌ Error in hybrid brain: {e}")
			self.current_state = "ERROR"
			return "I apologize, but I encountered an error. Please try again."
	
	def _should_use_llm(self, task_type: str) -> bool:
		"""Decide whether to use Custom LLM based on task type"""
		if self.disable_helagpt:
			return True  # Force LLM for all tasks when HelaGPT is disabled
		llm_tasks = [
			TaskType.CODE_ANALYSIS,
			TaskType.ENGINEERING,
			TaskType.DESIGN,
			TaskType.VIDEO_EDITING,
			TaskType.BUSINESS,
			TaskType.SYSTEM_MONITORING,
			TaskType.TECHNICAL
		]
		return task_type in llm_tasks or task_type == TaskType.UNKNOWN
	
	def _get_llm_response(self, user_input: str, task_type: str) -> Optional[str]:
		"""Get response from Custom LLM"""
		try:
			self.logger.info("🧠 Using Custom LLM brain...")
			self.stats['llm_calls'] += 1
			self.last_brain_used = "llm"
			
			# Enhance prompt for action extraction if task requires actions
			enhanced_input = self._enhance_prompt_for_action_extraction(user_input, task_type)
			
			# Use shorter max_length for faster responses during testing
			response = self.custom_llm.get_response(enhanced_input, max_length=512)
			
			# Validate response
			if response and len(response.strip()) > 0:
				self.logger.info(f"✅ Custom LLM response received ({len(response)} chars)")
				return response
			else:
				self.logger.warning("⚠️  Custom LLM returned empty response")
				self.stats['llm_failures'] += 1
				return None
				
		except Exception as e:
			self.logger.error(f"❌ Custom LLM error: {e}")
			self.stats['llm_failures'] += 1
			self.last_brain_used = None  # Reset on error
			return None
	
	def _enhance_prompt_for_action_extraction(self, user_input: str, task_type: str) -> str:
		"""Enhance prompt to encourage action extraction in AI response"""
		# For action-oriented tasks, add instruction to be explicit about actions
		action_oriented_tasks = [
			TaskType.SYSTEM_MONITORING,
			TaskType.BUSINESS,
			TaskType.ENGINEERING,
			TaskType.TECHNICAL
		]
		
		if task_type in action_oriented_tasks:
			enhanced = f"""{user_input}

Please respond naturally, but if this request requires any actions (like checking system status, creating files, running commands, generating invoices, etc.), please be explicit about what actions should be taken. I can execute actions like:
- System monitoring (CPU, memory, disk)
- File operations (read, write, list)
- Business operations (invoices, clients, reports)
- Workflow execution
- CLI commands"""
			return enhanced
		
		return user_input
	
	def _get_helagpt_response(self, user_input: str, task_type: str) -> Optional[str]:
		"""Get response from HelaGPT"""
		try:
			self.logger.info("🌐 Using HelaGPT brain...")
			self.stats['helagpt_calls'] += 1
			
			# Track if this is a fallback call
			if self.last_brain_used == "Custom LLM":
				self.stats['fallback_used'] += 1
				self.logger.info("⚠️  Fallback to HelaGPT")
			
			self.last_brain_used = "HelaGPT"
			
			response = self.helagpt.get_response(user_input)
			
			if response and len(response.strip()) > 0:
				self.logger.info("✅ HelaGPT response received")
				return response
			else:
				self.logger.warning("⚠️  HelaGPT returned empty response")
				self.stats['helagpt_failures'] += 1
				return None
				
		except Exception as e:
			self.logger.error(f"❌ HelaGPT error: {e}")
			self.stats['helagpt_failures'] += 1
			return None
	
	def _get_emergency_fallback(self, user_input: str) -> str:
		"""Emergency fallback when both brains fail"""
		self.logger.error("🚨 Both brains failed, using emergency fallback")
		return (
			"I apologize, but I'm having trouble processing your request right now. "
			"Both my AI systems are temporarily unavailable. Please try again in a moment."
		)
	
	def _detect_computer_action(self, user_input: str, task_type: str) -> Optional[Dict]:
		"""Detect if input requires actual computer access"""
		user_input_lower = user_input.lower()
		
		def _extract_path(text: str) -> Optional[str]:
			# Extract path in quotes: "..." or '...'
			m = re.search(r'"([^"]+)"|\'([^\']+)\'', text)
			if m:
				return m.group(1) or m.group(2)
			# After keywords like: in/at/path
			for key in [' in ', ' at ', ' path ']:
				if key in text:
					candidate = text.split(key, 1)[1].strip()
					return candidate.split(' ')[0]
			return None
		
		# System monitoring actions
		if 'monitor cpu' in user_input_lower or 'cpu usage' in user_input_lower:
			return {'action_type': 'monitor_cpu'}
		
		if 'monitor memory' in user_input_lower or 'memory usage' in user_input_lower or 'ram usage' in user_input_lower:
			return {'action_type': 'monitor_memory'}
		
		if 'monitor disk' in user_input_lower or 'disk usage' in user_input_lower or 'disk space' in user_input_lower:
			return {'action_type': 'monitor_disk'}
		
		if 'system stats' in user_input_lower or 'system status' in user_input_lower:
			return {'action_type': 'get_system_stats'}
		
		if 'list processes' in user_input_lower or 'running processes' in user_input_lower or 'top processes' in user_input_lower:
			return {'action_type': 'list_processes'}
		
		# File system actions
		if 'list directory' in user_input_lower or 'list files' in user_input_lower or 'show files' in user_input_lower:
			path = _extract_path(user_input) or '.'
			return {'action_type': 'list_directory', 'parameters': {'path': path}}
		
		if 'read file' in user_input_lower or 'open file' in user_input_lower:
			path = _extract_path(user_input)
			if path:
				return {'action_type': 'read_file', 'parameters': {'file_path': path}}
		
		if 'file info' in user_input_lower or 'file information' in user_input_lower or 'stat file' in user_input_lower:
			path = _extract_path(user_input)
			if path:
				return {'action_type': 'get_file_info', 'parameters': {'file_path': path}}
		
		# Utilities
		if 'screenshot' in user_input_lower:
			return {'action_type': 'screenshot'}
		
		if 'current time' in user_input_lower or 'what time' in user_input_lower:
			return {'action_type': 'get_current_time'}
		
		# No computer action detected
		return None
	
	def _format_action_response(self, action: Dict, result: Dict) -> str:
		"""Format computer action result into natural language response"""
		action_type = action['action_type']
		
		if action_type == 'monitor_cpu':
			cpu = result['result']
			response = f"✅ CPU Monitoring Results:\n\n"
			response += f"Overall Usage: {cpu['percent']:.1f}%\n\n"
			response += f"CPU Cores: {cpu['count']}\n"
			if cpu.get('per_cpu'):
				response += f"\nPer-Core Breakdown:\n"
				for i, usage in enumerate(cpu['per_cpu']):
					response += f"  • Core {i}: {usage:.1f}%\n"
			response += f"\nStatus: {'⚠️  High Usage!' if cpu.get('alert') else '✅ Normal'}"
			return response
		
		elif action_type == 'monitor_memory':
			mem = result['result']
			total_gb = mem['total'] / (1024**3)
			used_gb = mem['used'] / (1024**3)
			available_gb = mem['available'] / (1024**3)
			response = f"✅ Memory Monitoring Results:\n\n"
			response += f"Total Memory: {total_gb:.2f} GB\n"
			response += f"Used: {used_gb:.2f} GB ({mem['percent']:.1f}%)\n"
			response += f"Available: {available_gb:.2f} GB\n"
			response += f"\nStatus: {'⚠️  High Usage!' if mem.get('alert') else '✅ Normal'}"
			return response
		
		elif action_type == 'monitor_disk':
			disk = result['result']
			total_gb = disk['total'] / (1024**3)
			used_gb = disk['used'] / (1024**3)
			free_gb = disk['free'] / (1024**3)
			response = f"✅ Disk Monitoring Results:\n\n"
			response += f"Total Disk: {total_gb:.2f} GB\n"
			response += f"Used: {used_gb:.2f} GB ({disk['percent']:.1f}%)\n"
			response += f"Free: {free_gb:.2f} GB\n"
			response += f"\nStatus: {'⚠️  Low Space!' if disk.get('alert') else '✅ Normal'}"
			return response
		
		elif action_type == 'get_system_stats':
			stats = result['result']
			response = "✅ Complete System Statistics:\n\n"
			
			# CPU
			cpu = stats['cpu']
			response += f"🔹 CPU: {cpu['percent']:.1f}% ({cpu['count']} cores)\n"
			
			# Memory
			mem = stats['memory']
			mem_used_gb = mem['used'] / (1024**3)
			mem_total_gb = mem['total'] / (1024**3)
			response += f"🔹 Memory: {mem_used_gb:.1f}/{mem_total_gb:.1f} GB ({mem['percent']:.1f}%)\n"
			
			# Disk
			disk = stats['disk']
			disk_free_gb = disk['free'] / (1024**3)
			response += f"🔹 Disk: {disk_free_gb:.1f} GB free ({100-disk['percent']:.1f}% available)\n"
			
			# Processes
			proc = stats['processes']
			response += f"🔹 Processes: {proc['total']} running\n"
			
			response += f"\nTimestamp: {stats['timestamp']}"
			return response
		
		elif action_type == 'list_processes':
			proc_info = result['result']
			response = f"✅ Process List:\n\n"
			response += f"Total Processes: {proc_info['total']}\n"
			response += f"\nTop 10 by Memory:\n"
			for i, proc in enumerate(proc_info.get('top_10', [])[:10], 1):
				response += f"  {i}. {proc['name']} - {proc['memory_percent']:.2f}%\n"
			return response
		
		elif action_type == 'get_current_time':
			time_data = result['result']
			response = f"🕐 Current Time: {time_data['time']}"
			return response
		
		elif action_type == 'screenshot':
			response = f"✅ Screenshot captured: {result['result'].get('file_path', 'screenshot.png')}"
			return response
		
		elif action_type == 'list_directory':
			dir_result = result['result']
			response = f"✅ Directory Listing: {dir_result['path']}\n\n"
			items = dir_result.get('items', [])
			if items:
				response += f"Found {len(items)} items:\n"
				for item in items[:20]:  # Limit to 20
					icon = "📁" if item['type'] == 'directory' else "📄"
					response += f"  {icon} {item['name']}\n"
				if len(items) > 20:
					response += f"\n... and {len(items) - 20} more"
			else:
				response += "Directory is empty"
			return response
		
		elif action_type == 'read_file':
			file_path = result['result'].get('file_path')
			content = result['result'].get('content')
			if file_path and content:
				response = f"✅ File Content for {file_path}:\n\n"
				response += content + "\n"
				return response
			else:
				return f"❌ Could not read file {file_path} or content is empty."
		
		elif action_type == 'get_file_info':
			file_path = result['result'].get('file_path')
			if file_path:
				response = f"✅ File Information for {file_path}:\n\n"
				response += f"Size: {result['result']['size']} bytes\n"
				response += f"Created: {result['result']['created']}\n"
				response += f"Modified: {result['result']['modified']}\n"
				response += f"Accessed: {result['result']['accessed']}\n"
				return response
			else:
				return f"❌ Could not get file info for {file_path}."
		
		else:
			# Generic action response
			return f"✅ Action completed: {action_type}\n\nResult: {json.dumps(result['result'], indent=2)}"
	
	def _update_history(self, user_input: str, response: str, 
					   task_type: str, elapsed: float, action_executed: bool = False):
		"""Update conversation history"""
		entry = {
			'user': user_input,
			'assistant': response,
			'task_type': task_type,
			'brain_used': self.last_brain_used,
			'elapsed': elapsed,
			'action_executed': action_executed,
			'timestamp': datetime.now().isoformat()
		}
		
		self.conversation_history.append(entry)
		
		# Keep only last 20 exchanges
		if len(self.conversation_history) > 20:
			self.conversation_history = self.conversation_history[-20:]
	
	def get_statistics(self) -> Dict[str, Any]:
		"""Get usage statistics"""
		return {
			'total_calls': self.stats['total_calls'],
			'llm_calls': self.stats['llm_calls'],
			'helagpt_calls': self.stats['helagpt_calls'],
			'llm_failures': self.stats['llm_failures'],
			'helagpt_failures': self.stats['helagpt_failures'],
			'fallback_used': self.stats['fallback_used'],
			'actions_executed': self.stats['actions_executed'],
			'llm_success_rate': (
				(self.stats['llm_calls'] - self.stats['llm_failures']) / 
				self.stats['llm_calls'] * 100
			) if self.stats['llm_calls'] > 0 else 0,
			'helagpt_success_rate': (
				(self.stats['helagpt_calls'] - self.stats['helagpt_failures']) / 
				self.stats['helagpt_calls'] * 100
			) if self.stats['helagpt_calls'] > 0 else 0,
			'llm_available': self.llm_available,
			'helagpt_available': self.helagpt_available,
			'computer_access_available': self.has_computer_access if hasattr(self, 'has_computer_access') else False
		}
	
	def get_current_state(self) -> str:
		"""Get current state"""
		return self.current_state
	
	def get_conversation_history(self):
		"""Get conversation history"""
		return self.conversation_history.copy()
	
	def get_last_emotion(self) -> Optional[str]:
		"""Get last emotion (for compatibility)"""
		if self.helagpt and self.last_brain_used == "HelaGPT":
			return self.helagpt.get_last_emotion()
		return None
	
	def get_confidence_score(self) -> float:
		"""Get confidence score (for compatibility)"""
		if self.helagpt and self.last_brain_used == "HelaGPT":
			return self.helagpt.get_confidence_score()
		return 0.9  # Default for LLM
	
	def clear_history(self):
		"""Clear conversation history"""
		self.conversation_history = []
		if self.helagpt:
			self.helagpt.clear_history()

