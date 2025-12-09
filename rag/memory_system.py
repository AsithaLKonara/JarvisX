"""
Long-term Memory System
Persistent context and knowledge base
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from rag.vector_store import VectorStore
from rag.document_store import DocumentStore

logger = logging.getLogger(__name__)


class MemorySystem:
    """Long-term memory for persistent context"""
    
    def __init__(self, vector_store: Optional[VectorStore] = None, document_store: Optional[DocumentStore] = None):
        """Initialize memory system"""
        self.vector_store = vector_store
        self.document_store = document_store or DocumentStore()
    
    def store_memory(self, content: str, metadata: Optional[Dict] = None) -> str:
        """Store memory"""
        doc_id = f"memory_{datetime.now().timestamp()}"
        self.document_store.add_document(doc_id, content, metadata)
        return doc_id
    
    def retrieve_memories(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve relevant memories"""
        if self.vector_store:
            return self.vector_store.search(query, top_k)
        return []

