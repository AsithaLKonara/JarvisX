"""
Embedding Generation
Generate embeddings for documents and queries
"""

import logging
from typing import List, Optional
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for text"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding generator
        
        Args:
            model_name: Embedding model name
        """
        self.model_name = model_name
        self.model = None
        self.is_available = False
        self._initialize()
    
    def _initialize(self):
        """Initialize embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            
            self.model = SentenceTransformer(self.model_name)
            self.is_available = True
            logger.info(f"Embedding generator initialized: {self.model_name}")
        except ImportError:
            logger.warning("sentence-transformers not installed. Install with: pip install sentence-transformers")
            self.is_available = False
        except Exception as e:
            logger.error(f"Failed to initialize embedding generator: {e}")
            self.is_available = False
    
    def generate(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        Generate embeddings for texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors or None if unavailable
        """
        if not self.is_available or not self.model:
            logger.warning("Embedding generator not available")
            return None
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return None
    
    def generate_single(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None
        """
        result = self.generate([text])
        return result[0] if result else None

