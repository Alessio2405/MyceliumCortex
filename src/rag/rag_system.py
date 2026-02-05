"""RAG (Retrieval-Augmented Generation) system for knowledge integration."""

import logging
from typing import Any, Dict, List, Optional, Tuple
import asyncio

logger = logging.getLogger(__name__)


class RAGSystem:
    """Retrieval-Augmented Generation system for agent knowledge."""
    
    def __init__(
        self,
        vector_store: Any,
        embeddings_provider: Any,
        llm_client: Optional[Any] = None,
    ):
        """
        Initialize RAG system.
        
        Args:
            vector_store: Vector store instance (SQLiteVectorStore, ChromaVectorStore, etc.)
            embeddings_provider: Embeddings provider (AnthropicEmbeddings, OpenAIEmbeddings, etc.)
            llm_client: Optional LLM client for context-aware generation
        """
        self.vector_store = vector_store
        self.embeddings = embeddings_provider
        self.llm_client = llm_client
    
    async def add_knowledge(
        self,
        doc_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Add knowledge document to the system.
        
        Args:
            doc_id: Unique document ID
            text: Document text content
            metadata: Optional metadata (source, date, category, etc.)
        
        Returns:
            True if successful
        """
        try:
            # Generate embedding
            embedding = await self.embeddings.embed_text(text)
            if not embedding:
                logger.error(f"Failed to generate embedding for {doc_id}")
                return False
            
            # Store in vector database
            return await self.vector_store.add_document(
                doc_id=doc_id,
                text=text,
                embedding=embedding,
                metadata=metadata or {},
            )
        except Exception as e:
            logger.error(f"Error adding knowledge {doc_id}: {e}")
            return False
    
    async def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: Query text
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold
        
        Returns:
            List of relevant documents with similarity scores
        """
        try:
            # Generate query embedding
            query_embedding = await self.embeddings.embed_text(query)
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return []
            
            # Search vector store
            results = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k,
                min_similarity=min_similarity,
            )
            
            logger.info(f"Retrieved {len(results)} documents for query")
            return results
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    async def generate_with_context(
        self,
        query: str,
        system_prompt: Optional[str] = None,
        top_k: int = 5,
        min_similarity: float = 0.5,
        use_llm: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate response using RAG (retrieve context + generate).
        
        Args:
            query: User query
            system_prompt: Optional system prompt for generation
            top_k: Number of context documents to retrieve
            min_similarity: Minimum similarity threshold
            use_llm: Whether to use LLM for generation (requires llm_client)
        
        Returns:
            Dict with retrieved_context and generated_response
        """
        # Retrieve relevant context
        context_docs = await self.retrieve_context(
            query=query,
            top_k=top_k,
            min_similarity=min_similarity,
        )
        
        result = {
            "query": query,
            "retrieved_context": context_docs,
            "generated_response": None,
            "context_summary": None,
        }
        
        if not context_docs:
            logger.info("No relevant context found for query")
            return result
        
        # Build context summary
        context_text = "\n\n".join([
            f"[Source: {doc.get('metadata', {}).get('source', 'Unknown')}]\n{doc['text']}"
            for doc in context_docs
        ])
        
        result["context_summary"] = context_text
        
        # Generate response if LLM available
        if use_llm and self.llm_client:
            try:
                prompt = f"""Use the following context to answer the question.

Context:
{context_text}

Question: {query}

Answer:"""
                
                if hasattr(self.llm_client, 'messages'):
                    # Anthropic API
                    response = await asyncio.to_thread(
                        self.llm_client.messages.create,
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=1024,
                        system=system_prompt or "You are a helpful assistant with access to knowledge documents.",
                        messages=[{"role": "user", "content": prompt}],
                    )
                    result["generated_response"] = response.content[0].text
                else:
                    logger.warning("LLM client format not recognized")
            except Exception as e:
                logger.error(f"Error generating response: {e}")
        
        return result
    
    async def delete_knowledge(self, doc_id: str) -> bool:
        """Delete a knowledge document."""
        return await self.vector_store.delete_document(doc_id)
    
    async def list_knowledge(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all knowledge documents."""
        return await self.vector_store.list_documents(limit=limit)
    
    async def get_knowledge(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific knowledge document."""
        return await self.vector_store.get_document(doc_id)
