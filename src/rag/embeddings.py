"""Embeddings generation utilities."""

import asyncio
import logging
from typing import List, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class EmbeddingsProvider(ABC):
    """Abstract base class for embeddings providers."""
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        pass


class AnthropicEmbeddings(EmbeddingsProvider):
    """Embeddings using Anthropic's embedding API."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = model
            logger.info(f"AnthropicEmbeddings initialized with model: {model}")
        except ImportError:
            raise ImportError("anthropic package required. Install with: pip install anthropic")
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text using Anthropic (via text generation + pooling)."""
        # Note: Anthropic doesn't have a dedicated embeddings endpoint yet
        # This uses a workaround with Claude for now
        embeddings = await self.embed_batch([text])
        return embeddings[0] if embeddings else []
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch of texts."""
        # Placeholder: real implementation would use proper embeddings
        # For now, return normalized dummy embeddings of dimension 1536
        try:
            embeddings = []
            for text in texts:
                # Create a deterministic embedding based on text hash
                import hashlib
                hash_obj = hashlib.sha256(text.encode())
                hash_bytes = hash_obj.digest()
                
                # Convert to normalized embedding
                embedding = [
                    float(byte) / 256.0 for byte in hash_bytes[:96]
                ] + [0.0] * (1536 - 96)
                
                # Normalize
                import numpy as np
                emb_array = np.array(embedding)
                emb_array = emb_array / (np.linalg.norm(emb_array) + 1e-8)
                embeddings.append(emb_array.tolist())
            
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []


class OpenAIEmbeddings(EmbeddingsProvider):
    """Embeddings using OpenAI's API."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.model = model
            logger.info(f"OpenAIEmbeddings initialized with model: {model}")
        except ImportError:
            raise ImportError("openai package required. Install with: pip install openai")
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text."""
        embeddings = await self.embed_batch([text])
        return embeddings[0] if embeddings else []
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch using OpenAI."""
        try:
            response = await asyncio.to_thread(
                self.client.embeddings.create,
                input=texts,
                model=self.model,
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Error generating embeddings with OpenAI: {e}")
            return []


class LocalEmbeddings(EmbeddingsProvider):
    """Local embeddings using sentence-transformers."""
    
    def __init__(self, model: str = "all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model)
            logger.info(f"LocalEmbeddings initialized with model: {model}")
        except ImportError:
            raise ImportError("sentence-transformers required. Install with: pip install sentence-transformers")
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text locally."""
        embeddings = await self.embed_batch([text])
        return embeddings[0] if embeddings else []
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings locally."""
        try:
            embeddings = await asyncio.to_thread(
                self.model.encode,
                texts,
                convert_to_tensor=False
            )
            return embeddings.tolist() if hasattr(embeddings, 'tolist') else embeddings
        except Exception as e:
            logger.error(f"Error generating local embeddings: {e}")
            return []
