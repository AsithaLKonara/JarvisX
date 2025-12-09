"""
Knowledge Base
Learning from documents and building knowledge
"""

import logging
from typing import List, Dict
from rag.document_store import DocumentStore
from rag.vector_store import VectorStore
from rag.embedding_generator import EmbeddingGenerator

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """Knowledge base for document learning"""
    
    def __init__(self, vector_store: Optional[VectorStore] = None):
        """Initialize knowledge base"""
        self.document_store = DocumentStore()
        self.vector_store = vector_store
        self.embedding_generator = EmbeddingGenerator()
    
    def add_knowledge(self, text: str, metadata: Optional[Dict] = None) -> str:
        """Add knowledge to base"""
        doc_id = self.document_store.add_document(f"kb_{len(self.document_store.index)}", text, metadata)
        if self.vector_store and self.embedding_generator.is_available:
            embeddings = self.embedding_generator.generate([text])
            if embeddings:
                self.vector_store.add_documents([{"id": doc_id, "text": text, **(metadata or {})}], embeddings)
        return doc_id

