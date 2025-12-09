"""
Model Caching and Optimization
Implements model caching, lazy loading, and memory optimization
"""

import os
import gc
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ModelCache:
    """Cache for loaded models to avoid reloading"""
    
    def __init__(self):
        """Initialize model cache"""
        self._cache: Dict[str, Any] = {}
        self._cache_metadata: Dict[str, Dict] = {}
        self.max_cache_size = 2  # Maximum models to cache
        self.last_access: Dict[str, datetime] = {}
    
    def get(self, model_key: str) -> Optional[Any]:
        """
        Get cached model
        
        Args:
            model_key: Unique key for model
            
        Returns:
            Cached model or None
        """
        if model_key in self._cache:
            self.last_access[model_key] = datetime.now()
            logger.debug(f"Model cache hit: {model_key}")
            return self._cache[model_key]
        return None
    
    def set(self, model_key: str, model: Any, metadata: Optional[Dict] = None):
        """
        Cache model
        
        Args:
            model_key: Unique key for model
            model: Model object to cache
            metadata: Optional metadata about model
        """
        # Evict least recently used if cache is full
        if len(self._cache) >= self.max_cache_size and model_key not in self._cache:
            self._evict_lru()
        
        self._cache[model_key] = model
        self.last_access[model_key] = datetime.now()
        if metadata:
            self._cache_metadata[model_key] = metadata
        
        logger.debug(f"Model cached: {model_key}")
    
    def _evict_lru(self):
        """Evict least recently used model"""
        if not self.last_access:
            return
        
        # Find LRU
        lru_key = min(self.last_access.items(), key=lambda x: x[1])[0]
        
        # Remove from cache
        if lru_key in self._cache:
            del self._cache[lru_key]
        if lru_key in self._cache_metadata:
            del self._cache_metadata[lru_key]
        if lru_key in self.last_access:
            del self.last_access[lru_key]
        
        # Force garbage collection
        gc.collect()
        logger.debug(f"Evicted model from cache: {lru_key}")
    
    def clear(self, model_key: Optional[str] = None):
        """
        Clear cache
        
        Args:
            model_key: Specific model to clear (None = clear all)
        """
        if model_key:
            if model_key in self._cache:
                del self._cache[model_key]
            if model_key in self._cache_metadata:
                del self._cache_metadata[model_key]
            if model_key in self.last_access:
                del self.last_access[model_key]
            gc.collect()
        else:
            self._cache.clear()
            self._cache_metadata.clear()
            self.last_access.clear()
            gc.collect()
            logger.info("Model cache cleared")


class LazyModelLoader:
    """Lazy loading for models to reduce startup time"""
    
    def __init__(self):
        """Initialize lazy loader"""
        self._models: Dict[str, Any] = {}
        self._loaders: Dict[str, callable] = {}
        self._loaded: Dict[str, bool] = {}
    
    def register(self, model_key: str, loader: callable):
        """
        Register a model loader
        
        Args:
            model_key: Unique key for model
            loader: Function that loads the model
        """
        self._loaders[model_key] = loader
        self._loaded[model_key] = False
    
    def get(self, model_key: str) -> Optional[Any]:
        """
        Get model (loads if not already loaded)
        
        Args:
            model_key: Model key
            
        Returns:
            Loaded model or None
        """
        if model_key not in self._loaders:
            logger.warning(f"Model loader not registered: {model_key}")
            return None
        
        # Return cached if already loaded
        if self._loaded[model_key] and model_key in self._models:
            return self._models[model_key]
        
        # Load model
        try:
            logger.info(f"Lazy loading model: {model_key}")
            model = self._loaders[model_key]()
            self._models[model_key] = model
            self._loaded[model_key] = True
            return model
        except Exception as e:
            logger.error(f"Failed to load model {model_key}: {e}")
            return None
    
    def preload(self, model_key: str):
        """
        Preload a model
        
        Args:
            model_key: Model key to preload
        """
        self.get(model_key)


# Global instances
_model_cache = ModelCache()
_lazy_loader = LazyModelLoader()


def get_model_cache() -> ModelCache:
    """Get global model cache"""
    return _model_cache


def get_lazy_loader() -> LazyModelLoader:
    """Get global lazy loader"""
    return _lazy_loader


def optimize_memory():
    """Optimize memory usage"""
    gc.collect()
    logger.info("Memory optimization: garbage collection performed")

