"""
System Monitor - Alert Engine
Alert generation and notification management.
"""

from datetime import datetime
from typing import Dict, List, Callable
from enum import Enum


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = 'info'
    WARNING = 'warning'
    CRITICAL = 'critical'


class AlertEngine:
    """Generate and manage alerts"""
    
    def __init__(self):
        """Initialize alert engine"""
        self.alerts = []
        self.subscribers = []
        self.alert_rules = {}
    
    def create_alert(self, level: str, title: str, message: str, source: str = '') -> Dict:
        """Create system alert"""
        alert = {
            'id': len(self.alerts) + 1,
            'level': level,
            'title': title,
            'message': message,
            'source': source,
            'timestamp': datetime.now().isoformat(),
            'acknowledged': False
        }
        self.alerts.append(alert)
        self._notify_subscribers(alert)
        return alert
    
    def subscribe(self, callback: Callable):
        """Subscribe to alerts"""
        self.subscribers.append(callback)
    
    def _notify_subscribers(self, alert: Dict):
        """Notify all subscribers of alert"""
        for callback in self.subscribers:
            try:
                callback(alert)
            except Exception:
                pass
    
    def get_alerts(self, level: str = None) -> List[Dict]:
        """Get alerts, optionally filtered by level"""
        if level:
            return [a for a in self.alerts if a['level'] == level]
        return self.alerts
    
    def acknowledge_alert(self, alert_id: int) -> bool:
        """Mark alert as acknowledged"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['acknowledged'] = True
                return True
        return False
    
    def add_alert_rule(self, rule_name: str, condition: Callable, action: Callable) -> bool:
        """Add alert rule"""
        try:
            self.alert_rules[rule_name] = {'condition': condition, 'action': action}
            return True
        except Exception:
            return False
    
    def evaluate_rules(self, data: Dict) -> List[Dict]:
        """Evaluate all alert rules"""
        triggered = []
        for rule_name, rule in self.alert_rules.items():
            try:
                if rule['condition'](data):
                    result = rule['action'](data)
                    triggered.append(result)
            except Exception:
                pass
        return triggered
    
    def get_active_alerts(self) -> List[Dict]:
        """Get unacknowledged alerts"""
        return [a for a in self.alerts if not a['acknowledged']]
    
    def clear_acknowledged_alerts(self) -> int:
        """Clear acknowledged alerts"""
        count = len(self.alerts)
        self.alerts = [a for a in self.alerts if not a['acknowledged']]
        return count - len(self.alerts)
