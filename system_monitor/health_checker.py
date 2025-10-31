"""
System Monitor - Health Checker
Component and system health status checking.
"""

from datetime import datetime
from typing import Dict, List
from enum import Enum


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = 'healthy'
    WARNING = 'warning'
    CRITICAL = 'critical'
    OFFLINE = 'offline'


class HealthChecker:
    """Check system component health"""
    
    def __init__(self):
        """Initialize health checker"""
        self.component_status = {}
        self.health_history = []
    
    def check_component(self, component_name: str, is_healthy: bool, message: str = '') -> Dict:
        """Check component health"""
        status = HealthStatus.HEALTHY if is_healthy else HealthStatus.CRITICAL
        health_data = {
            'component': component_name,
            'status': status.value,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.component_status[component_name] = health_data
        self.health_history.append(health_data)
        return health_data
    
    def get_component_status(self, component_name: str) -> Dict:
        """Get specific component status"""
        return self.component_status.get(component_name, {})
    
    def get_all_status(self) -> Dict:
        """Get all components status"""
        return {
            'timestamp': datetime.now().isoformat(),
            'components': self.component_status,
            'overall_status': self._calculate_overall_status()
        }
    
    def _calculate_overall_status(self) -> str:
        """Calculate overall system health"""
        if not self.component_status:
            return HealthStatus.HEALTHY.value
        
        statuses = [c['status'] for c in self.component_status.values()]
        if HealthStatus.CRITICAL.value in statuses:
            return HealthStatus.CRITICAL.value
        elif HealthStatus.WARNING.value in statuses:
            return HealthStatus.WARNING.value
        return HealthStatus.HEALTHY.value
    
    def get_health_history(self, limit: int = 100) -> List[Dict]:
        """Get health check history"""
        return self.health_history[-limit:]
    
    def add_phase_check(self, phase_name: str, status: str) -> Dict:
        """Add phase health check"""
        return self.check_component(f"phase_{phase_name}", status == 'operational', f"Phase {phase_name}")
