"""
Mode Orchestrator - Handles mode switching and coordination
Phase 1 of Jarvis X V2
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class ModeStatus(Enum):
    """Mode status enumeration"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"

@dataclass
class ModeInfo:
    """Mode information"""
    name: str
    status: ModeStatus
    handler: Optional[object] = None
    last_used: Optional[str] = None

class ModeOrchestrator:
    """Orchestrates mode switching and coordination"""
    
    def __init__(self):
        self.modes = {
            'engineer': ModeInfo('Engineer Mode', ModeStatus.INACTIVE),
            'designer': ModeInfo('Designer Mode', ModeStatus.INACTIVE),
            'editor': ModeInfo('Editor Mode', ModeStatus.INACTIVE),
            'business': ModeInfo('Business Mode', ModeStatus.INACTIVE),
            'monitor': ModeInfo('System Monitor', ModeStatus.INACTIVE),
            'avatar': ModeInfo('Avatar System', ModeStatus.INACTIVE)
        }
        self.current_mode = None
    
    def activate_mode(self, mode: str) -> bool:
        """Activate a specific mode"""
        if mode not in self.modes:
            return False
        
        # Deactivate current mode
        if self.current_mode:
            self.modes[self.current_mode].status = ModeStatus.INACTIVE
        
        # Activate new mode
        self.modes[mode].status = ModeStatus.ACTIVE
        self.current_mode = mode
        
        return True
    
    def get_mode_status(self, mode: str) -> Optional[ModeStatus]:
        """Get status of a specific mode"""
        if mode in self.modes:
            return self.modes[mode].status
        return None
    
    def get_all_modes(self) -> Dict[str, ModeInfo]:
        """Get all mode information"""
        return self.modes.copy()
    
    def is_mode_available(self, mode: str) -> bool:
        """Check if a mode is available"""
        return mode in self.modes and self.modes[mode].status != ModeStatus.ERROR



