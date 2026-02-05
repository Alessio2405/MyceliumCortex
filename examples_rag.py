"""RAG system examples and workflows."""

import asyncio
import os
from typing import Optional
from src.rag import (
    SQLiteVectorStore, VectorStoreConfig,
    OpenAIEmbeddings, LocalEmbeddings, RAGSystem,
    DocumentIngester
)
from src.agents.knowledge_agents import KnowledgeAgent
from src.core.types import AgentConfig, AgentLevel


# ============================================================================
# Example 1: Basic RAG Setup with Local Embeddings
# ============================================================================

async def example_basic_rag():
    """Basic RAG setup without external API dependencies."""
    print("\n" + "="*70)
    print("Example 1: Basic RAG Setup (Local Embeddings)")
    print("="*70)
    
    try:
        # Initialize components
        vector_store = SQLiteVectorStore(
            VectorStoreConfig(db_path="basic_rag.db")
        )
        embeddings = LocalEmbeddings(model="all-MiniLM-L6-v2")
        rag = RAGSystem(vector_store, embeddings)
        
        # Add sample documents
        documents = [
            {
                "id": "policy_vacation",
                "text": "Employees are entitled to 20 days of paid vacation per year. "
                       "Vacation days can be carried over to the next year, "
                       "with a maximum of 5 days carryover.",
                "metadata": {"type": "policy", "category": "hr"}
            },
            {
                "id": "policy_sick_leave",
                "text": "Sick leave is 10 days per year for personal illness. "
                       "Medical documentation may be required for absences exceeding 3 consecutive days.",
                "metadata": {"type": "policy", "category": "hr"}
            },
            {
                "id": "policy_remote_work",
                "text": "Remote work is available up to 3 days per week with manager approval. "
                       "Core hours are 10am-3pm in local timezone.",
                "metadata": {"type": "policy", "category": "work"}
            }
        ]
        
        # Ingest documents
        for doc in documents:
            success = await rag.add_knowledge(
                doc_id=doc["id"],
                text=doc["text"],
                metadata=doc["metadata"]
            )
            print(f"  Added {doc['id']}: {success}")
        
        # Query the knowledge base
        queries = [
            "How many vacation days do I get?",
            "What's the remote work policy?",
            "How much sick leave is allowed?"
        ]
        
        for query in queries:
            print(f"\nQuery: {query}")
            context = await rag.retrieve_context(query, top_k=2)
            for doc in context:
                print(f"  - [{doc['similarity']:.2f}] {doc['text'][:60]}...")
    
    except ImportError as e:
        print(f"  Note: {e}")
        print("  Install with: pip install sentence-transformers")


# ============================================================================
# Example 2: Document Ingestion from Files
# ============================================================================

async def example_document_ingestion():
    """Ingest documents from various file formats."""
    print("\n" + "="*70)
    print("Example 2: Document Ingestion")
    print("="*70)
    
    try:
        # Setup RAG
        vector_store = SQLiteVectorStore(
            VectorStoreConfig(db_path="ingestion_rag.db")
        )
        embeddings = LocalEmbeddings()
        rag = RAGSystem(vector_store, embeddings)
        
        # Example: Create sample documents
        sample_text = """
        Company Handbook
        
        # Work Hours
        Standard work hours are 9am-5pm Monday through Friday.
        Flexible hours available with manager approval.
        
        # Code of Conduct
        All employees must follow professional standards.
        Harassment and discrimination are strictly prohibited.
        
        # Benefits
        - Health insurance (company pays 80%)
        - 401k matching up to 4%
        - Gym membership subsidy
        """
        
        # Save sample text to file (for demonstration)
        sample_path = "sample_handbook.txt"
        with open(sample_path, 'w') as f:
            f.write(sample_text)
        
        # Ingest text file
        print("\nIngesting text file...")
        doc_ids = await DocumentIngester.ingest_text_file(
            sample_path, rag,
            chunk_size=200, chunk_overlap=50
        )
        print(f"  Ingested {len(doc_ids)} chunks")
        
        # List ingested documents
        all_docs = await rag.list_knowledge(limit=10)
        print(f"\nTotal documents in knowledge base: {len(all_docs)}")
        
        # Query ingested knowledge
        query = "What benefits does the company offer?"
        context = await rag.retrieve_context(query)
        print(f"\nQuery: {query}")
        for doc in context:
            print(f"  - {doc['text'][:80]}...")
        
        # Cleanup
        if os.path.exists(sample_path):
            os.remove(sample_path)
    
    except Exception as e:
        print(f"  Error: {e}")


# ============================================================================
# Example 3: Knowledge Agent with RAG
# ============================================================================

async def example_knowledge_agent():
    """Use KnowledgeAgent for RAG operations."""
    print("\n" + "="*70)
    print("Example 3: Knowledge Agent")
    print("="*70)
    
    try:
        # Setup RAG
        vector_store = SQLiteVectorStore(
            VectorStoreConfig(db_path="agent_rag.db")
        )
        embeddings = LocalEmbeddings()
        rag = RAGSystem(vector_store, embeddings)
        
        # Create agent config
        config = AgentConfig(
            name="knowledge_assistant",
            level=AgentLevel.EXECUTION,
            description="Assistant with knowledge base access",
            version="1.0",
        )
        
        # Initialize knowledge agent
        agent = KnowledgeAgent(config, rag)
        
        # Add knowledge via agent
        print("\nAdding knowledge via agent...")
        result = await agent.execute_action("add_knowledge", {
            "doc_id": "product_features",
            "text": "Our product includes: real-time collaboration, "
                   "version control, and AI-powered suggestions.",
            "metadata": {"type": "product", "version": "2.0"}
        })
        print(f"  Result: {result}")
        
        # Query knowledge via agent
        print("\nQuerying knowledge via agent...")
        result = await agent.execute_action("query_knowledge", {
            "query": "What features does the product have?",
            "top_k": 3
        })
        print(f"  Found {result['context_count']} matching documents")
        
        # List knowledge
        print("\nListing all knowledge...")
        result = await agent.execute_action("list_knowledge", {
            "limit": 5
        })
        print(f"  Total documents: {result['total']}")
    
    except Exception as e:
        print(f"  Error: {e}")


# ============================================================================
# Example 4: Multi-Domain Knowledge Bases
# ============================================================================

async def example_multi_domain_rag():
    """Maintain separate knowledge bases for different domains."""
    print("\n" + "="*70)
    print("Example 4: Multi-Domain Knowledge Bases")
    print("="*70)
    
    try:
        # Create separate RAG systems for HR and Product
        hr_rag = RAGSystem(
            SQLiteVectorStore(VectorStoreConfig(db_path="hr_knowledge.db")),
            LocalEmbeddings()
        )
        
        product_rag = RAGSystem(
            SQLiteVectorStore(VectorStoreConfig(db_path="product_knowledge.db")),
            LocalEmbeddings()
        )
        
        # Ingest HR knowledge
        print("\nSetting up HR knowledge base...")
        hr_docs = [
            ("hr_benefits", "Health insurance, dental, vision coverage provided."),
            ("hr_pto", "20 days PTO per year, negotiable for senior roles."),
        ]
        for doc_id, text in hr_docs:
            await hr_rag.add_knowledge(doc_id, text, {"domain": "hr"})
        print(f"  Added {len(hr_docs)} HR documents")
        
        # Ingest Product knowledge
        print("\nSetting up Product knowledge base...")
        product_docs = [
            ("prod_features", "AI-powered analytics, real-time sync, offline mode."),
            ("prod_pricing", "Plans: Free ($0), Pro ($29/mo), Enterprise (custom)."),
        ]
        for doc_id, text in product_docs:
            await product_rag.add_knowledge(doc_id, text, {"domain": "product"})
        print(f"  Added {len(product_docs)} Product documents")
        
        # Query each domain
        print("\nQuerying HR knowledge...")
        hr_context = await hr_rag.retrieve_context("What PTO do I get?")
        print(f"  Found {len(hr_context)} HR documents")
        
        print("\nQuerying Product knowledge...")
        prod_context = await product_rag.retrieve_context("What features are available?")
        print(f"  Found {len(prod_context)} Product documents")
    
    except Exception as e:
        print(f"  Error: {e}")


# ============================================================================
# Example 5: Context-Aware Query Handling
# ============================================================================

async def example_context_aware_queries():
    """Handle queries with full context integration."""
    print("\n" + "="*70)
    print("Example 5: Context-Aware Query Handling")
    print("="*70)
    
    try:
        # Setup RAG
        vector_store = SQLiteVectorStore(
            VectorStoreConfig(db_path="context_rag.db")
        )
        embeddings = LocalEmbeddings()
        rag = RAGSystem(vector_store, embeddings)
        
        # Ingest knowledge
        knowledge = [
            ("kb_1", "Python is ideal for data science and web development."),
            ("kb_2", "JavaScript runs in browsers and Node.js servers."),
            ("kb_3", "Rust provides memory safety without garbage collection."),
        ]
        for doc_id, text in knowledge:
            await rag.add_knowledge(doc_id, text)
        
        # Query with varying specificity
        queries = [
            ("What languages are good for web development?", 0.5),
            ("Which language has memory safety?", 0.7),
        ]
        
        for query, threshold in queries:
            print(f"\nQuery: {query}")
            print(f"  Threshold: {threshold}")
            context = await rag.retrieve_context(
                query,
                top_k=5,
                min_similarity=threshold
            )
            print(f"  Results: {len(context)}")
            for doc in context:
                print(f"    [{doc['similarity']:.2f}] {doc['text']}")
    
    except Exception as e:
        print(f"  Error: {e}")


# ============================================================================
# Example 6: Batch Document Processing
# ============================================================================

async def example_batch_processing():
    """Process multiple documents in batch."""
    print("\n" + "="*70)
    print("Example 6: Batch Document Processing")
    print("="*70)
    
    try:
        vector_store = SQLiteVectorStore(
            VectorStoreConfig(db_path="batch_rag.db")
        )
        embeddings = LocalEmbeddings()
        rag = RAGSystem(vector_store, embeddings)
        
        # Simulate processing a batch of documents
        documents = [
            {"id": f"doc_{i}", "text": f"Document {i} content with unique information about topic {i}."}
            for i in range(10)
        ]
        
        print(f"\nProcessing {len(documents)} documents...")
        for doc in documents:
            await rag.add_knowledge(
                doc_id=doc["id"],
                text=doc["text"],
                metadata={"batch": "batch_1", "order": documents.index(doc)}
            )
        
        # Verify ingestion
        all_docs = await rag.list_knowledge(limit=15)
        print(f"  Successfully ingested {len(all_docs)} documents")
        
        # Test retrieval across batch
        query = "Document 5 content"
        context = await rag.retrieve_context(query, top_k=3)
        print(f"\nSearching for 'Document 5 content':")
        print(f"  Top match: {context[0]['id'] if context else 'None'}")
    
    except Exception as e:
        print(f"  Error: {e}")


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Run all RAG examples."""
    print("\n" + "="*70)
    print("MyceliumCortex RAG System Examples")
    print("="*70)
    
    # Run examples
    await example_basic_rag()
    await example_document_ingestion()
    await example_knowledge_agent()
    await example_multi_domain_rag()
    await example_context_aware_queries()
    await example_batch_processing()
    
    print("\n" + "="*70)
    print("Examples completed!")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
