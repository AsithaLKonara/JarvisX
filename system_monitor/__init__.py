"""Jarvis X V2 - Phase 6: System Monitor"""
# Import only modules that exist
from .health_checker import HealthChecker
from .resource_monitor import ResourceMonitor
from .alert_engine import AlertEngine

# Optional imports - only if modules exist
try:
    from .monitor_handler import MonitorHandler
except ImportError:
    MonitorHandler = None

try:
    from .dashboard_manager import DashboardManager
except ImportError:
    DashboardManager = None

try:
    from .report_generator import ReportGenerator
except ImportError:
    ReportGenerator = None

__all__ = [
    'HealthChecker',
    'ResourceMonitor',
    'AlertEngine',
]

# Add optional modules if they exist
if MonitorHandler is not None:
    __all__.append('MonitorHandler')
if DashboardManager is not None:
    __all__.append('DashboardManager')
if ReportGenerator is not None:
    __all__.append('ReportGenerator')
