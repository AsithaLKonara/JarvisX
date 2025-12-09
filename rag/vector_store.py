"""
Vector Database Interface
Abstract interface for vector database operations (ChromaDB, Pinecone, etc.)
"""

import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class VectorStore(ABC):
    """Abstract base class for vector stores"""
    
    @abstractmethod
    def add_documents(self, documents: List[Dict[str, Any]], embeddings: Optional[List[List[float]]] = None):
        """Add documents to vector store"""
        pass
    
    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        pass
    
    @abstractmethod
    def delete(self, ids: List[str]):
        """Delete documents by IDs"""
        pass


class ChromaDBStore(VectorStore):
    """ChromaDB implementation"""
    
    def __init__(self, collection_name: str = "jarvis_documents", persist_directory: Optional[str] = None):
        """
        Initialize ChromaDB store
        
        Args:
            collection_name: Collection name
            persist_directory: Directory to persist data
        """
        try:
            import chromadb
            from chromadb.config import Settings
            
            if persist_directory:
                self.client = chromadb.PersistentClient(path=persist_directory)
            else:
                self.client = chromadb.Client(Settings(anonymized_telemetry=False))
            
            self.collection = self.client.get_or_create_collection(name=collection_name)
            self.is_available = True
            logger.info("ChromaDB vector store initialized")
        except ImportError:
            logger.warning("ChromaDB not installed. Install with: pip install chromadb")
            self.is_available = False
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.is_available = False
    
    def add_documents(self, documents: List[Dict[str, Any]], embeddings: Optional[List[List[float]]] = None):
        """Add documents to ChromaDB"""
        if not self.is_available:
            logger.warning("ChromaDB not available")
            return
        
        try:
            ids = [doc.get('id', str(i)) for i, doc in enumerate(documents)]
            texts = [doc.get('text', '') for doc in documents]
            metadatas = [{k: v for k, v in doc.items() if k not in ['id', 'text']} for doc in documents]
            
            if embeddings:
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas
                )
            else:
                self.collection.add(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas
                )
            
            logger.info(f"Added {len(documents)} documents to ChromaDB")
        except Exception as e:
            logger.error(f"Failed to add documents to ChromaDB: {e}")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search ChromaDB"""
        if not self.is_available:
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    result = {
                        'text': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0.0
                    }
                    formatted_results.append(result)
            
            return formatted_results
        except Exception as e:
            logger.error(f"ChromaDB search failed: {e}")
            return []
    
    def delete(self, ids: List[str]):
        """Delete documents from ChromaDB"""
        if not self.is_available:
            return
        
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from ChromaDB")
        except Exception as e:
            logger.error(f"Failed to delete from ChromaDB: {e}")


def get_vector_store(store_type: str = "chromadb", **kwargs) -> Optional[VectorStore]:
    """
    Get vector store instance
    
    Args:
        store_type: Store type ("chromadb" or "pinecone")
        **kwargs: Store-specific arguments
        
    Returns:
        Vector store instance or None
    """
    if store_type == "chromadb":
        return ChromaDBStore(**kwargs)
    elif store_type == "pinecone":
        # Pinecone implementation would go here
        logger.warning("Pinecone not yet implemented")
        return None
    else:
        logger.error(f"Unknown vector store type: {store_type}")
        return None

