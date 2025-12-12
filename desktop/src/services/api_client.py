"""
API client for desktop application
"""
import requests
import json
from typing import Optional, Dict, Any
from pathlib import Path
import sys

# Add parent directory for config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from utils.config import Config
    config = Config()
    API_URL = config.get('API_URL', 'http://localhost:8000')
except:
    API_URL = 'http://localhost:8000'

API_PREFIX = '/api/v1'

class APIClient:
    """API client for backend communication"""
    
    def __init__(self):
        self.base_url = f"{API_URL}{API_PREFIX}"
        self.token = None
        self.load_token()
    
    def load_token(self):
        """Load token from storage"""
        try:
            from src.utils.config import load_config
            config = load_config()
            self.token = config.get('access_token')
        except:
            pass
    
    def save_token(self, token: str):
        """Save token to storage"""
        try:
            from src.utils.config import save_config
            save_config({'access_token': token})
            self.token = token
        except:
            self.token = token
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """POST request"""
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                json=data,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API Error: {e}")
            return None
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """GET request"""
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API Error: {e}")
            return None

