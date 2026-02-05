"""Knowledge-enhanced agents with RAG capabilities."""

import logging
from typing import Any, Dict, Optional
from ..core.agent import ExecutionAgent
from ..core.types import AgentConfig
from ..rag.rag_system import RAGSystem

logger = logging.getLogger(__name__)


class KnowledgeAgent(ExecutionAgent):
    """Execution agent enhanced with RAG (Retrieval-Augmented Generation)."""
    
    def __init__(
        self,
        config: AgentConfig,
        rag_system: RAGSystem,
        parent_agent_id: Optional[str] = None,
    ):
        """
        Initialize knowledge agent.
        
        Args:
            config: Agent configuration
            rag_system: RAGSystem instance for knowledge retrieval
            parent_agent_id: Parent agent ID
        """
        super().__init__(config, parent_agent_id)
        self.rag_system = rag_system
        logger.info(f"Initialized KnowledgeAgent: {self.config.name}")
    
    async def execute_action(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute knowledge-aware actions."""
        
        if action == "query_knowledge":
            return await self._query_knowledge(payload)
        elif action == "add_knowledge":
            return await self._add_knowledge(payload)
        elif action == "delete_knowledge":
            return await self._delete_knowledge(payload)
        elif action == "list_knowledge":
            return await self._list_knowledge(payload)
        elif action == "generate_with_knowledge":
            return await self._generate_with_knowledge(payload)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _query_knowledge(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Query knowledge base for relevant context."""
        query = payload.get("query")
        if not query:
            raise ValueError("query required")
        
        top_k = payload.get("top_k", 5)
        min_similarity = payload.get("min_similarity", 0.5)
        
        context = await self.rag_system.retrieve_context(
            query=query,
            top_k=top_k,
            min_similarity=min_similarity,
        )
        
        return {
            "query": query,
            "context": context,
            "context_count": len(context),
        }
    
    async def _add_knowledge(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Add knowledge document."""
        doc_id = payload.get("doc_id")
        text = payload.get("text")
        metadata = payload.get("metadata", {})
        
        if not doc_id or not text:
            raise ValueError("doc_id and text required")
        
        success = await self.rag_system.add_knowledge(
            doc_id=doc_id,
            text=text,
            metadata=metadata,
        )
        
        return {
            "doc_id": doc_id,
            "success": success,
            "message": f"Knowledge document {'added' if success else 'failed to add'}",
        }
    
    async def _delete_knowledge(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Delete knowledge document."""
        doc_id = payload.get("doc_id")
        if not doc_id:
            raise ValueError("doc_id required")
        
        success = await self.rag_system.delete_knowledge(doc_id)
        
        return {
            "doc_id": doc_id,
            "success": success,
            "message": f"Knowledge document {'deleted' if success else 'failed to delete'}",
        }
    
    async def _list_knowledge(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """List knowledge documents."""
        limit = payload.get("limit", 100)
        
        documents = await self.rag_system.list_knowledge(limit=limit)
        
        return {
            "documents": documents,
            "total": len(documents),
        }
    
    async def _generate_with_knowledge(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response using knowledge base context."""
        query = payload.get("query")
        if not query:
            raise ValueError("query required")
        
        system_prompt = payload.get("system_prompt")
        top_k = payload.get("top_k", 5)
        min_similarity = payload.get("min_similarity", 0.5)
        use_llm = payload.get("use_llm", True)
        
        result = await self.rag_system.generate_with_context(
            query=query,
            system_prompt=system_prompt,
            top_k=top_k,
            min_similarity=min_similarity,
            use_llm=use_llm,
        )
        
        return {
            "query": query,
            "retrieved_context": result["retrieved_context"],
            "context_count": len(result["retrieved_context"]),
            "generated_response": result["generated_response"],
            "has_context": len(result["retrieved_context"]) > 0,
        }
