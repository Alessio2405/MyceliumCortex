"""Vector store abstraction for RAG systems."""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
import sqlite3
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class VectorStoreConfig:
    """Configuration for vector stores."""
    
    def __init__(
        self,
        db_path: str = "rag_vectors.db",
        embedding_dim: int = 1536,  # OpenAI/Anthropic embedding dimension
        collection_name: str = "documents",
        enable_similarity_search: bool = True,
    ):
        self.db_path = db_path
        self.embedding_dim = embedding_dim
        self.collection_name = collection_name
        self.enable_similarity_search = enable_similarity_search


class VectorStore(ABC):
    """Abstract base class for vector stores."""
    
    @abstractmethod
    async def add_document(
        self,
        doc_id: str,
        text: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Add a document with its embedding."""
        pass

    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        min_similarity: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        pass

    @abstractmethod
    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document."""
        pass

    @abstractmethod
    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        pass

    @abstractmethod
    async def list_documents(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all documents."""
        pass


class SQLiteVectorStore(VectorStore):
    """SQLite-based vector store with similarity search."""
    
    def __init__(self, config: VectorStoreConfig):
        self.config = config
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.config.db_path)
        cursor = conn.cursor()
        
        # Create documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                embedding BLOB NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON documents(created_at)
        """)
        
        conn.commit()
        conn.close()
    
    async def add_document(
        self,
        doc_id: str,
        text: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Add document with embedding to vector store."""
        try:
            conn = sqlite3.connect(self.config.db_path)
            cursor = conn.cursor()
            
            # Convert embedding to bytes
            embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
            metadata_str = json.dumps(metadata or {})
            
            cursor.execute("""
                INSERT OR REPLACE INTO documents 
                (id, text, embedding, metadata, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (doc_id, text, embedding_bytes, metadata_str))
            
            conn.commit()
            conn.close()
            logger.info(f"Added document {doc_id} to vector store")
            return True
        except Exception as e:
            logger.error(f"Error adding document {doc_id}: {e}")
            return False
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        min_similarity: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """Search for similar documents using cosine similarity."""
        try:
            conn = sqlite3.connect(self.config.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, text, embedding, metadata FROM documents")
            rows = cursor.fetchall()
            conn.close()
            
            query_vec = np.array(query_embedding, dtype=np.float32)
            results = []
            
            for doc_id, text, embedding_bytes, metadata_str in rows:
                # Convert bytes back to embedding
                doc_vec = np.frombuffer(embedding_bytes, dtype=np.float32)
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_vec, doc_vec)
                
                if similarity >= min_similarity:
                    results.append({
                        "id": doc_id,
                        "text": text,
                        "similarity": float(similarity),
                        "metadata": json.loads(metadata_str or "{}"),
                    })
            
            # Sort by similarity and return top_k
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:top_k]
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document."""
        try:
            conn = sqlite3.connect(self.config.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            conn.commit()
            conn.close()
            logger.info(f"Deleted document {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False
    
    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        try:
            conn = sqlite3.connect(self.config.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT text, metadata, created_at FROM documents WHERE id = ?",
                (doc_id,)
            )
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "id": doc_id,
                    "text": row[0],
                    "metadata": json.loads(row[1] or "{}"),
                    "created_at": row[2],
                }
            return None
        except Exception as e:
            logger.error(f"Error getting document {doc_id}: {e}")
            return None
    
    async def list_documents(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all documents."""
        try:
            conn = sqlite3.connect(self.config.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, text, metadata, created_at FROM documents ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "id": row[0],
                    "text": row[1],
                    "metadata": json.loads(row[2] or "{}"),
                    "created_at": row[3],
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []
    
    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)


class ChromaVectorStore(VectorStore):
    """Chroma vector store wrapper for production use."""
    
    def __init__(self, config: VectorStoreConfig):
        self.config = config
        try:
            import chromadb
            self.client = chromadb.Client()
            self.collection = self.client.get_or_create_collection(
                name=config.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"ChromaVectorStore initialized with collection: {config.collection_name}")
        except ImportError:
            raise ImportError("chromadb not installed. Install with: pip install chromadb")
    
    async def add_document(
        self,
        doc_id: str,
        text: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Add document to Chroma."""
        try:
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata or {}]
            )
            logger.info(f"Added document {doc_id} to Chroma")
            return True
        except Exception as e:
            logger.error(f"Error adding to Chroma: {e}")
            return False
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        min_similarity: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """Search in Chroma."""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            output = []
            for i, doc_id in enumerate(results["ids"][0]):
                similarity = results["distances"][0][i]
                if similarity >= min_similarity:
                    output.append({
                        "id": doc_id,
                        "text": results["documents"][0][i],
                        "similarity": similarity,
                        "metadata": results["metadatas"][0][i],
                    })
            return output
        except Exception as e:
            logger.error(f"Error searching Chroma: {e}")
            return []
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete from Chroma."""
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            logger.error(f"Error deleting from Chroma: {e}")
            return False
    
    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document from Chroma."""
        try:
            result = self.collection.get(ids=[doc_id])
            if result["ids"]:
                return {
                    "id": doc_id,
                    "text": result["documents"][0],
                    "metadata": result["metadatas"][0],
                }
            return None
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return None
    
    async def list_documents(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List documents from Chroma."""
        try:
            result = self.collection.get(limit=limit)
            return [
                {
                    "id": doc_id,
                    "text": result["documents"][i],
                    "metadata": result["metadatas"][i],
                }
                for i, doc_id in enumerate(result["ids"])
            ]
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []
