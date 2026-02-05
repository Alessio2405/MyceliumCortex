"""Integration examples: RAG system with existing smart agents."""

import asyncio
from src.rag import (
    SQLiteVectorStore, VectorStoreConfig,
    LocalEmbeddings, OpenAIEmbeddings,
    RAGSystem, DocumentIngester
)
from src.agents.knowledge_agents import KnowledgeAgent
from src.core.types import AgentConfig, AgentLevel


# ============================================================================
# Example 1: RAG-Enhanced Customer Service Agent
# ============================================================================

async def example_customer_service():
    """Use RAG to provide accurate customer service responses."""
    print("\n" + "="*70)
    print("Example 1: RAG-Enhanced Customer Service")
    print("="*70)
    
    try:
        # Setup RAG with customer knowledge base
        rag = RAGSystem(
            SQLiteVectorStore(VectorStoreConfig(db_path="customer_service.db")),
            LocalEmbeddings()
        )
        
        # Ingest company policies and FAQs
        company_knowledge = {
            "return_policy": """
            Returns are accepted within 30 days of purchase.
            Items must be unused and in original packaging.
            A 10% restocking fee applies to discounted items.
            Electronics must be returned within 14 days with all accessories.
            """,
            "shipping_policy": """
            Standard shipping: 5-7 business days ($9.99)
            Express shipping: 2-3 business days ($24.99)
            Free shipping on orders over $50
            International shipping available to 180+ countries
            """,
            "warranty": """
            Electronics: 2-year manufacturer warranty
            Accessories: 1-year limited warranty
            Coverage excludes water damage and physical damage
            Extended warranty available for additional cost
            """
        }
        
        for doc_id, text in company_knowledge.items():
            await rag.add_knowledge(doc_id, text, {"category": "policy"})
        
        # Create customer service agent
        config = AgentConfig(
            name="customer_service_agent",
            level=AgentLevel.EXECUTION,
            description="Customer service with knowledge base",
            version="1.0"
        )
        agent = KnowledgeAgent(config, rag)
        
        # Customer queries
        queries = [
            "Can I return my headphones if they don't work?",
            "How long does shipping take?",
            "What warranty comes with the product?"
        ]
        
        for query in queries:
            print(f"\nCustomer: {query}")
            
            # Generate knowledge-grounded response
            result = await agent.execute_action("generate_with_knowledge", {
                "query": query,
                "system_prompt": "You are a helpful customer service representative. "
                               "Answer based on company policies.",
                "top_k": 2,
                "use_llm": True
            })
            
            if result['generated_response']:
                print(f"Agent: {result['generated_response'][:200]}...")
            else:
                print(f"Agent: Found {result['context_count']} relevant policy documents")
    
    except Exception as e:
        print(f"  Error: {e}")


# ============================================================================
# Example 2: RAG + Booking Agent (Enhanced)
# ============================================================================

async def example_rag_booking():
    """Use RAG to enhance booking with restaurant information."""
    print("\n" + "="*70)
    print("Example 2: RAG-Enhanced Booking Agent")
    print("="*70)
    
    try:
        # Setup RAG with restaurant information
        rag = RAGSystem(
            SQLiteVectorStore(VectorStoreConfig(db_path="restaurant_info.db")),
            LocalEmbeddings()
        )
        
        # Add restaurant information
        restaurants = [
            {
                "id": "rest_italian",
                "text": "Mario's Italian Kitchen - Authentic Italian cuisine, "
                       "open daily 11am-10pm, specializes in pasta and wood-fired pizza. "
                       "Average price: $25-40. Accepts reservations. Good for groups.",
                "metadata": {"cuisine": "Italian", "price": "$$"}
            },
            {
                "id": "rest_japanese",
                "text": "Sakura Sushi - Premium Japanese restaurant, "
                       "closed Mondays, open Tue-Sun 5pm-11pm. Omakase available. "
                       "Average price: $60-100. Reservation required for groups.",
                "metadata": {"cuisine": "Japanese", "price": "$$$"}
            },
        ]
        
        for rest in restaurants:
            await rag.add_knowledge(rest["id"], rest["text"], rest["metadata"])
        
        # Create booking agent with RAG
        config = AgentConfig(
            name="smart_booking_agent",
            level=AgentLevel.EXECUTION,
            description="Booking agent with restaurant knowledge"
        )
        agent = KnowledgeAgent(config, rag)
        
        # Booking request
        booking_query = "I want to book a nice dinner for 4 people. Something Italian would be nice."
        print(f"\nUser: {booking_query}")
        
        # Retrieve relevant restaurants
        context = await agent.execute_action("query_knowledge", {
            "query": booking_query,
            "top_k": 3
        })
        
        print(f"Found {context['context_count']} matching restaurants:")
        for doc in context['context']:
            print(f"  - {doc['text'][:100]}...")
        
        # Generate booking recommendation
        result = await agent.execute_action("generate_with_knowledge", {
            "query": booking_query,
            "system_prompt": "You are a helpful booking assistant. "
                           "Recommend restaurants based on available information.",
            "use_llm": True
        })
        
        if result['generated_response']:
            print(f"\nRecommendation: {result['generated_response'][:200]}...")
    
    except Exception as e:
        print(f"  Error: {e}")


# ============================================================================
# Example 3: Multi-Agent System with Shared Knowledge
# ============================================================================

async def example_multi_agent_knowledge():
    """Multiple agents sharing the same knowledge base."""
    print("\n" + "="*70)
    print("Example 3: Multi-Agent System with Shared Knowledge")
    print("="*70)
    
    try:
        # Create shared knowledge base
        shared_rag = RAGSystem(
            SQLiteVectorStore(VectorStoreConfig(db_path="shared_knowledge.db")),
            LocalEmbeddings()
        )
        
        # Populate with company information
        company_info = [
            ("company_mission", "Our mission is to empower users with AI technology."),
            ("company_values", "We value innovation, transparency, and user privacy."),
            ("team_size", "We are a team of 50 engineers and 30 support staff."),
            ("product_features", "Our product includes AI chat, automation, and analytics."),
        ]
        
        for doc_id, text in company_info:
            await shared_rag.add_knowledge(doc_id, text, {"type": "company_info"})
        
        # Create multiple agents using the same knowledge base
        agents_config = [
            ("sales_agent", "Sales representative who explains product features"),
            ("hr_agent", "HR agent answering company questions"),
            ("support_agent", "Support agent helping with product use")
        ]
        
        agents = {}
        for agent_name, description in agents_config:
            config = AgentConfig(
                name=agent_name,
                level=AgentLevel.EXECUTION,
                description=description
            )
            agents[agent_name] = KnowledgeAgent(config, shared_rag)
        
        # Each agent uses the shared knowledge
        queries = [
            ("sales_agent", "What features does your product have?"),
            ("hr_agent", "What does your company value?"),
            ("support_agent", "How many people work at this company?")
        ]
        
        for agent_name, query in queries:
            print(f"\n{agent_name.upper()}")
            print(f"Question: {query}")
            
            context = await agents[agent_name].execute_action("query_knowledge", {
                "query": query,
                "top_k": 2
            })
            
            print(f"Found {context['context_count']} relevant documents from shared knowledge")
            for doc in context['context']:
                print(f"  - {doc['text'][:80]}...")
    
    except Exception as e:
        print(f"  Error: {e}")


# ============================================================================
# Example 4: Dynamic Knowledge Updates
# ============================================================================

async def example_dynamic_knowledge():
    """Update knowledge base based on agent conversations."""
    print("\n" + "="*70)
    print("Example 4: Dynamic Knowledge Updates")
    print("="*70)
    
    try:
        rag = RAGSystem(
            SQLiteVectorStore(VectorStoreConfig(db_path="dynamic_kb.db")),
            LocalEmbeddings()
        )
        
        config = AgentConfig(
            name="learning_agent",
            level=AgentLevel.EXECUTION,
            description="Agent that learns from conversations"
        )
        agent = KnowledgeAgent(config, rag)
        
        # Initial knowledge
        print("\nInitial knowledge base:")
        initial_docs = {
            "fact_1": "Python is a programming language",
            "fact_2": "JavaScript runs in browsers"
        }
        
        for doc_id, text in initial_docs.items():
            await agent.execute_action("add_knowledge", {
                "doc_id": doc_id,
                "text": text,
                "metadata": {"source": "initial", "version": 1}
            })
        
        # List initial knowledge
        result = await agent.execute_action("list_knowledge", {"limit": 10})
        print(f"  Documents: {result['total']}")
        
        # During conversation, add new facts
        print("\nLearning new facts during conversation...")
        new_facts = [
            ("fact_3", "Python excels at data science and machine learning"),
            ("fact_4", "JavaScript has async/await for asynchronous programming"),
        ]
        
        for doc_id, text in new_facts:
            await agent.execute_action("add_knowledge", {
                "doc_id": doc_id,
                "text": text,
                "metadata": {"source": "conversation", "version": 2}
            })
        
        # List updated knowledge
        result = await agent.execute_action("list_knowledge", {"limit": 10})
        print(f"  Documents after learning: {result['total']}")
        
        # Query updated knowledge
        print("\nQuerying updated knowledge:")
        context = await agent.execute_action("query_knowledge", {
            "query": "What can Python do?",
            "top_k": 2
        })
        
        print(f"  Found {context['context_count']} relevant documents")
        for doc in context['context']:
            print(f"    - {doc['text'][:70]}...")
    
    except Exception as e:
        print(f"  Error: {e}")


# ============================================================================
# Example 5: Knowledge Base Maintenance
# ============================================================================

async def example_kb_maintenance():
    """Best practices for knowledge base management."""
    print("\n" + "="*70)
    print("Example 5: Knowledge Base Maintenance")
    print("="*70)
    
    try:
        rag = RAGSystem(
            SQLiteVectorStore(VectorStoreConfig(db_path="kb_maintenance.db")),
            LocalEmbeddings()
        )
        
        # Add versioned documents
        print("\nAdding versioned documents...")
        versions = [
            ("policy_v1", "Old vacation policy: 15 days per year", {"version": 1, "status": "deprecated"}),
            ("policy_v2", "Current vacation policy: 20 days per year", {"version": 2, "status": "active"}),
            ("faq_current", "Top 10 FAQs about benefits", {"type": "faq", "status": "active"}),
        ]
        
        for doc_id, text, metadata in versions:
            await rag.add_knowledge(doc_id, text, metadata)
        
        # List all documents
        result = await rag.list_knowledge(limit=100)
        print(f"Total documents: {len(result)}")
        
        # Query and show metadata
        print("\nQuerying with metadata:")
        context = await rag.retrieve_context("vacation policy", top_k=2)
        for doc in context:
            print(f"  ID: {doc['id']}")
            print(f"  Similarity: {doc['similarity']:.2f}")
            print(f"  Metadata: {doc['metadata']}")
            print(f"  Text: {doc['text'][:60]}...")
            print()
        
        # Cleanup old version
        print("Removing deprecated document...")
        await rag.delete_knowledge("policy_v1")
        
        result = await rag.list_knowledge(limit=100)
        print(f"Documents after cleanup: {len(result)}")
    
    except Exception as e:
        print(f"  Error: {e}")


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Run all integration examples."""
    print("\n" + "="*70)
    print("RAG Integration Examples with Smart Agents")
    print("="*70)
    
    await example_customer_service()
    await example_rag_booking()
    await example_multi_agent_knowledge()
    await example_dynamic_knowledge()
    await example_kb_maintenance()
    
    print("\n" + "="*70)
    print("Integration examples completed!")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
