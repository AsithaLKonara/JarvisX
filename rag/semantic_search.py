"""
Semantic Search
Document retrieval with context injection and relevance scoring
"""

import logging
from typing import List, Dict, Any, Optional
from rag.vector_store import VectorStore
from rag.embedding_generator import EmbeddingGenerator

logger = logging.getLogger(__name__)


class SemanticSearch:
    """Semantic search for document retrieval"""
    
    def __init__(self, vector_store: Optional[VectorStore] = None, embedding_generator: Optional[EmbeddingGenerator] = None):
        """
        Initialize semantic search
        
        Args:
            vector_store: Vector store instance
            embedding_generator: Embedding generator instance
        """
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator or EmbeddingGenerator()
    
    def search(self, query: str, top_k: int = 5, min_score: float = 0.5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            min_score: Minimum relevance score
            
        Returns:
            List of relevant documents with scores
        """
        if not self.vector_store:
            logger.warning("Vector store not available")
            return []
        
        # Perform vector search
        results = self.vector_store.search(query, top_k=top_k)
        
        # Filter by minimum score (if distance-based, lower is better)
        filtered_results = [
            r for r in results
            if (1.0 - r.get('distance', 1.0)) >= min_score  # Convert distance to score
        ]
        
        # Sort by relevance (higher score = more relevant)
        filtered_results.sort(key=lambda x: 1.0 - x.get('distance', 1.0), reverse=True)
        
        return filtered_results
    
    def inject_context(self, query: str, max_context_length: int = 1000) -> str:
        """
        Inject relevant context into query
        
        Args:
            query: Original query
            max_context_length: Maximum context length in characters
            
        Returns:
            Query with injected context
        """
        # Search for relevant documents
        results = self.search(query, top_k=3)
        
        if not results:
            return query
        
        # Build context from results
        context_parts = []
        current_length = 0
        
        for result in results:
            text = result.get('text', '')
            if current_length + len(text) <= max_context_length:
                context_parts.append(text)
                current_length += len(text)
            else:
                break
        
        if context_parts:
            context = "\n\n".join(context_parts)
            return f"Context:\n{context}\n\nQuery: {query}"
        
        return query
    
    def calculate_relevance(self, query: str, document: str) -> float:
        """
        Calculate relevance score between query and document
        
        Args:
            query: Search query
            document: Document text
            
        Returns:
            Relevance score (0.0-1.0)
        """
        if not self.embedding_generator.is_available:
            # Fallback: simple keyword matching
            query_words = set(query.lower().split())
            doc_words = set(document.lower().split())
            intersection = query_words.intersection(doc_words)
            return len(intersection) / len(query_words) if query_words else 0.0
        
        # Generate embeddings
        query_embedding = self.embedding_generator.generate_single(query)
        doc_embedding = self.embedding_generator.generate_single(document)
        
        if not query_embedding or not doc_embedding:
            return 0.0
        
        # Calculate cosine similarity
        import numpy as np
        query_vec = np.array(query_embedding)
        doc_vec = np.array(doc_embedding)
        
        dot_product = np.dot(query_vec, doc_vec)
        norm_product = np.linalg.norm(query_vec) * np.linalg.norm(doc_vec)
        
        if norm_product == 0:
            return 0.0
        
        similarity = dot_product / norm_product
        return float(similarity)

