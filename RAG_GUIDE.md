# RAG System Documentation

## Overview

The RAG (Retrieval-Augmented Generation) system enables MyceliumCortex agents to incorporate custom knowledge bases, allowing them to provide informed responses grounded in your own documents and data.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│          User Query / Knowledge Ingestion            │
└──────────────────┬──────────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
    ┌────▼────┐         ┌────▼────────────┐
    │Embeddings│        │Document Ingester│
    │ Provider │        │   (chunking)     │
    └────┬────┘         └────┬─────────────┘
         │                   │
         └─────────┬─────────┘
                   │
            ┌──────▼──────────┐
            │  Vector Store   │
            │  (SQLite/Chroma)│
            └──────┬──────────┘
                   │
         ┌─────────▼──────────┐
         │  RAG System        │
         │  (Retrieval +      │
         │   Generation)      │
         └─────────┬──────────┘
                   │
            ┌──────▼──────┐
            │Knowledge Agents│
            └──────┬──────┘
                   │
            ┌──────▼──────┐
            │   LLM/Output │
            └──────────────┘
```

## Components

### 1. Vector Store (`vector_store.py`)

Stores document embeddings and performs similarity search.

**Available Implementations:**
- `SQLiteVectorStore` - Lightweight, local, no dependencies
- `ChromaVectorStore` - Production-grade, persistent

```python
from src.rag import SQLiteVectorStore, VectorStoreConfig

config = VectorStoreConfig(
    db_path="my_knowledge.db",
    embedding_dim=1536,
    collection_name="documents"
)
vector_store = SQLiteVectorStore(config)
```

### 2. Embeddings Providers (`embeddings.py`)

Generates vector embeddings from text.

**Available Providers:**
- `OpenAIEmbeddings` - Uses OpenAI API (text-embedding-3-small, 3-large)
- `LocalEmbeddings` - Uses sentence-transformers (no API key needed)
- `AnthropicEmbeddings` - Anthropic integration

```python
from src.rag import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(api_key="sk-...", model="text-embedding-3-small")
```

### 3. RAG System (`rag_system.py`)

Core retrieval-augmented generation orchestrator.

**Main Operations:**
- `add_knowledge()` - Ingest documents
- `retrieve_context()` - Find relevant documents
- `generate_with_context()` - LLM response with context
- `delete_knowledge()` - Remove documents
- `list_knowledge()` - Browse knowledge base

```python
from src.rag import RAGSystem

rag = RAGSystem(
    vector_store=vector_store,
    embeddings_provider=embeddings,
    llm_client=anthropic_client  # optional
)

# Add knowledge
await rag.add_knowledge(
    doc_id="doc_1",
    text="Your company's policies...",
    metadata={"source": "handbook", "date": "2026-02-05"}
)

# Retrieve context
context = await rag.retrieve_context(
    query="What's our vacation policy?",
    top_k=3
)

# Generate with context
result = await rag.generate_with_context(
    query="What's our vacation policy?",
    top_k=3,
    use_llm=True
)
```

### 4. Document Ingester (`ingestion.py`)

Utilities for ingesting various document types.

**Supported Formats:**
- Text files (`.txt`) - Auto-chunked
- Markdown (`.md`) - Heading-based chunking
- JSON/JSONL (`.json`, `.jsonl`) - Per-object ingestion
- Directories - Bulk ingestion

```python
from src.rag import DocumentIngester

# Ingest single file
await DocumentIngester.ingest_text_file("policies.txt", rag)

# Ingest markdown with heading-based splitting
await DocumentIngester.ingest_markdown_file("docs/guide.md", rag)

# Ingest JSON documents
await DocumentIngester.ingest_json_documents(
    "products.json",
    rag,
    text_field="description",
    id_field="product_id"
)

# Bulk ingest directory
results = await DocumentIngester.ingest_directory(
    "./knowledge_base",
    rag,
    file_extensions=[".txt", ".md", ".json"],
    recursive=True
)
```

### 5. Knowledge Agent (`knowledge_agents.py`)

Specialized agent with RAG capabilities.

**Actions:**
- `query_knowledge` - Search knowledge base
- `add_knowledge` - Add documents
- `delete_knowledge` - Remove documents
- `list_knowledge` - Browse documents
- `generate_with_knowledge` - RAG-enhanced generation

```python
from src.agents.knowledge_agents import KnowledgeAgent

agent = KnowledgeAgent(config, rag_system)

# Query knowledge base
result = await agent.execute_action("query_knowledge", {
    "query": "vacation policy",
    "top_k": 3,
    "min_similarity": 0.5
})

# Generate with knowledge
result = await agent.execute_action("generate_with_knowledge", {
    "query": "What's our return policy?",
    "system_prompt": "You are a helpful customer service agent.",
    "use_llm": True
})
```

## Quick Start

### 1. Setup

```python
from src.rag import (
    SQLiteVectorStore, VectorStoreConfig,
    OpenAIEmbeddings, RAGSystem, DocumentIngester
)

# Initialize vector store
vector_store = SQLiteVectorStore(
    VectorStoreConfig(db_path="company_knowledge.db")
)

# Initialize embeddings (with API key in env)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Create RAG system
rag = RAGSystem(vector_store, embeddings)
```

### 2. Ingest Knowledge

```python
# Option A: Ingest directory
results = await DocumentIngester.ingest_directory(
    "./company_docs",
    rag,
    recursive=True
)

# Option B: Ingest specific files
await DocumentIngester.ingest_markdown_file("handbook.md", rag)
await DocumentIngester.ingest_text_file("policies.txt", rag)
```

### 3. Query Knowledge

```python
# Search for relevant context
context = await rag.retrieve_context(
    query="What's the refund policy?",
    top_k=5
)

for doc in context:
    print(f"Match: {doc['similarity']:.2f}")
    print(f"Text: {doc['text'][:200]}...")
    print(f"Source: {doc['metadata']['source']}")
```

### 4. Generate with Context

```python
# Get LLM response grounded in knowledge
result = await rag.generate_with_context(
    query="What's our vacation policy?",
    system_prompt="You are an HR assistant. Answer based on provided documents.",
    top_k=3,
    use_llm=True
)

print(f"Query: {result['query']}")
print(f"Context documents: {len(result['retrieved_context'])}")
print(f"Response: {result['generated_response']}")
```

## Integration Patterns

### Pattern 1: Knowledge-Aware Smart Agents

```python
# Enhance smart agents with knowledge
rag = RAGSystem(vector_store, embeddings)
await DocumentIngester.ingest_directory("./product_docs", rag)

knowledge_agent = KnowledgeAgent(config, rag)

# Use in workflow
context = await knowledge_agent.execute_action("query_knowledge", {
    "query": "premium features"
})

response = await knowledge_agent.execute_action("generate_with_knowledge", {
    "query": f"Explain premium features to customer: {user_question}",
    "top_k": 5
})
```

### Pattern 2: Supervisor with Knowledge

```python
# Create supervisor that uses RAG for task context
rag = RAGSystem(vector_store, embeddings)

# Ingest domain knowledge
await DocumentIngester.ingest_directory("./domain_docs", rag)

# Supervisors can access RAG for context-aware routing
supervisor = StrategicSupervisor(config, rag_system=rag)
```

### Pattern 3: Multi-Knowledge-Base System

```python
# Separate knowledge bases for different domains
hr_rag = RAGSystem(
    SQLiteVectorStore(VectorStoreConfig(db_path="hr_kb.db")),
    OpenAIEmbeddings()
)

product_rag = RAGSystem(
    SQLiteVectorStore(VectorStoreConfig(db_path="product_kb.db")),
    OpenAIEmbeddings()
)

# Route to appropriate knowledge base
hr_agent = KnowledgeAgent(hr_config, hr_rag)
product_agent = KnowledgeAgent(product_config, product_rag)
```

## Configuration Options

### Vector Store Config

```python
VectorStoreConfig(
    db_path="knowledge.db",           # SQLite database file
    embedding_dim=1536,                # Dimension of embeddings (1536 for OpenAI)
    collection_name="documents",       # Collection name (for Chroma)
    enable_similarity_search=True      # Enable similarity search
)
```

### Embeddings Providers

**OpenAI:**
```python
OpenAIEmbeddings(
    api_key="sk-...",                  # OpenAI API key
    model="text-embedding-3-small"     # Model choice
)
```

**Local (SentenceTransformers):**
```python
LocalEmbeddings(
    model="all-MiniLM-L6-v2"  # Model from HuggingFace
)
```

### RAG System

```python
RAGSystem(
    vector_store=store,
    embeddings_provider=embeddings,
    llm_client=client  # Optional
)
```

## Performance Considerations

### Chunking Strategy

For **text files** (default):
- Chunk size: 1000 characters
- Overlap: 100 characters
- Customize: `ingest_text_file(..., chunk_size=2000, chunk_overlap=200)`

For **markdown** files:
- Chunks split at heading boundaries (section-based)
- Preserves context around headings
- Customize: `ingest_markdown_file(..., chunk_by_heading=True)`

### Similarity Thresholds

- `min_similarity=0.5` (default) - Most permissive
- `min_similarity=0.7` - Balanced
- `min_similarity=0.85` - High precision

Lower thresholds retrieve more results; adjust based on your use case.

### Embedding Models

| Model | Dimension | Cost | Speed | Accuracy |
|-------|-----------|------|-------|----------|
| text-embedding-3-small | 1536 | Low | Fast | Good |
| text-embedding-3-large | 3072 | Medium | Slower | Excellent |
| all-MiniLM-L6-v2 | 384 | Free | Very Fast | Fair |

## Advanced Usage

### Custom Chunking

```python
def custom_chunker(text: str) -> List[str]:
    # Implement your own chunking logic
    return chunks

# Chunk manually, then add individually
chunks = custom_chunker(large_document)
for i, chunk in enumerate(chunks):
    await rag.add_knowledge(
        doc_id=f"doc_{i}",
        text=chunk,
        metadata={"chunk_index": i}
    )
```

### Metadata-Based Filtering

```python
# Ingest with rich metadata
await rag.add_knowledge(
    doc_id="policy_2024_vacation",
    text="Vacation policy text...",
    metadata={
        "source": "handbook",
        "year": 2024,
        "department": "HR",
        "version": 1.2
    }
)

# Note: Current implementation doesn't filter by metadata
# Future enhancement: metadata-aware retrieval
```

### Hybrid Search (Coming Soon)

```python
# Combine keyword search with semantic search
results = await rag.hybrid_search(
    query="vacation policy",
    semantic_weight=0.7,  # 70% semantic, 30% keyword
    top_k=5
)
```

## Troubleshooting

### Issue: Low Similarity Scores

**Cause:** Query and documents use different language/concepts

**Solution:**
- Use larger embeddings model (text-embedding-3-large)
- Lower min_similarity threshold
- Rephrase query to match document language
- Ingest more diverse documents

### Issue: Slow Ingestion

**Cause:** Large files or many API calls

**Solution:**
- Use LocalEmbeddings instead of OpenAI (no API latency)
- Batch ingest: process directories in parallel
- Larger chunk sizes (fewer embeddings to generate)

### Issue: Out of Memory

**Cause:** Very large documents or embedding dimensions

**Solution:**
- Use SQLiteVectorStore instead of loading all in memory
- Smaller embedding model (all-MiniLM-L6-v2)
- Chunk more aggressively (smaller chunk_size)

## Future Enhancements

- [ ] Metadata-aware retrieval filtering
- [ ] Hybrid keyword + semantic search
- [ ] Multi-modal embeddings (text + images)
- [ ] Document reranking with cross-encoders
- [ ] Sparse-dense search combinations
- [ ] Knowledge base versioning
- [ ] Automated knowledge freshness detection
- [ ] Query expansion and reformulation

## API Reference

See inline docstrings in:
- `src/rag/vector_store.py` - VectorStore interface
- `src/rag/embeddings.py` - Embeddings providers
- `src/rag/rag_system.py` - RAGSystem
- `src/rag/ingestion.py` - DocumentIngester
- `src/agents/knowledge_agents.py` - KnowledgeAgent
