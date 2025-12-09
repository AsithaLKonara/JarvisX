"""
Document Storage
Manages document storage and indexing for RAG
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class DocumentStore:
    """Store and manage documents for RAG"""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize document store
        
        Args:
            storage_dir: Directory for document storage
        """
        if storage_dir is None:
            from cli.utils import get_project_root
            storage_dir = get_project_root() / "data" / "documents"
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "index.json"
        self.index: Dict[str, Dict] = {}
        self._load_index()
    
    def _load_index(self):
        """Load document index"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    self.index = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load document index: {e}")
    
    def _save_index(self):
        """Save document index"""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save document index: {e}")
    
    def add_document(self, doc_id: str, text: str, metadata: Optional[Dict] = None) -> bool:
        """
        Add document to store
        
        Args:
            doc_id: Document ID
            text: Document text
            metadata: Optional metadata
            
        Returns:
            True if successful
        """
        try:
            # Save document
            doc_file = self.storage_dir / f"{doc_id}.txt"
            doc_file.write_text(text, encoding='utf-8')
            
            # Update index
            self.index[doc_id] = {
                "id": doc_id,
                "text": text[:100] + "..." if len(text) > 100 else text,  # Preview
                "metadata": metadata or {},
                "created_at": datetime.now().isoformat(),
                "file_path": str(doc_file)
            }
            
            self._save_index()
            logger.info(f"Document added: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return False
    
    def get_document(self, doc_id: str) -> Optional[str]:
        """Get document text by ID"""
        if doc_id not in self.index:
            return None
        
        doc_file = Path(self.index[doc_id]['file_path'])
        if doc_file.exists():
            return doc_file.read_text(encoding='utf-8')
        return None
    
    def list_documents(self) -> List[Dict]:
        """List all documents"""
        return list(self.index.values())
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document"""
        if doc_id not in self.index:
            return False
        
        try:
            doc_file = Path(self.index[doc_id]['file_path'])
            if doc_file.exists():
                doc_file.unlink()
            del self.index[doc_id]
            self._save_index()
            return True
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False

