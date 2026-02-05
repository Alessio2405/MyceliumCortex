# RAG Quick Reference

## 30-Second Setup

```python
from src.rag import SQLiteVectorStore, LocalEmbeddings, RAGSystem, DocumentIngester

# Create RAG system
rag = RAGSystem(
    SQLiteVectorStore(),
    LocalEmbeddings()  # No API key needed
)

# Add your knowledge base
await DocumentIngester.ingest_directory("./docs", rag)

# Query and generate
result = await rag.generate_with_context(
    query="Your question here",
    use_llm=True
)
```

## Core Components

| Component | Purpose | Location |
|-----------|---------|----------|
| `VectorStore` | Store + search embeddings | `src/storage/vector_store.py` |
| `EmbeddingsProvider` | Generate embeddings from text | `src/rag/embeddings.py` |
| `RAGSystem` | Orchestrator (retrieve + generate) | `src/rag/rag_system.py` |
| `DocumentIngester` | Bulk ingest various formats | `src/rag/ingestion.py` |
| `KnowledgeAgent` | Agent with RAG capabilities | `src/agents/knowledge_agents.py` |

## Embeddings Options

| Provider | No API Key | Local | Cost |
|----------|-----------|-------|------|
| `LocalEmbeddings` | ✅ | ✅ | Free |
| `OpenAIEmbeddings` | ❌ | ❌ | Low |
| `AnthropicEmbeddings` | ❌ | ❌ | Low |

```python
# Free option (no API key)
embeddings = LocalEmbeddings(model="all-MiniLM-L6-v2")

# Production option (requires API key)
embeddings = OpenAIEmbeddings(api_key="sk-...", model="text-embedding-3-small")
```

## Common Operations

### Initialize RAG
```python
from src.rag import SQLiteVectorStore, LocalEmbeddings, RAGSystem, VectorStoreConfig

rag = RAGSystem(
    vector_store=SQLiteVectorStore(VectorStoreConfig(db_path="knowledge.db")),
    embeddings_provider=LocalEmbeddings(),
)
```

### Add Documents
```python
# Single document
await rag.add_knowledge(
    doc_id="unique_id",
    text="Document content...",
    metadata={"source": "file.txt", "category": "policy"}
)

# Batch from directory
from src.rag import DocumentIngester
results = await DocumentIngester.ingest_directory("./docs", rag)

# From specific formats
await DocumentIngester.ingest_text_file("README.txt", rag)
await DocumentIngester.ingest_markdown_file("guide.md", rag)
await DocumentIngester.ingest_json_documents("data.json", rag, text_field="content")
```

### Search Knowledge Base
```python
# Retrieve relevant documents
docs = await rag.retrieve_context(
    query="What's the vacation policy?",
    top_k=3,           # Return top 3 matches
    min_similarity=0.5  # Minimum match score (0-1)
)

# Access results
for doc in docs:
    print(doc['id'])              # Document ID
    print(doc['text'])            # Document text
    print(doc['similarity'])      # Match score (0-1)
    print(doc['metadata'])        # Metadata dict
```

### Generate with Context
```python
# Retrieve context + generate LLM response
result = await rag.generate_with_context(
    query="What's our refund policy?",
    system_prompt="You are a helpful customer service agent.",
    top_k=5,                      # Retrieve top 5 docs
    min_similarity=0.5,           # Minimum match score
    use_llm=True                  # Generate LLM response
)

# Access result
print(result['query'])                    # Original query
print(result['retrieved_context'])        # List of matched docs
print(result['generated_response'])       # LLM-generated response
print(result['context_summary'])          # Combined context text
```

### List & Manage
```python
# List documents
docs = await rag.list_knowledge(limit=100)

# Get specific document
doc = await rag.get_knowledge("doc_id")

# Delete document
await rag.delete_knowledge("doc_id")
```

## Using KnowledgeAgent

```python
from src.agents.knowledge_agents import KnowledgeAgent
from src.core.types import AgentConfig, AgentLevel

# Create agent
config = AgentConfig(
    name="knowledge_bot",
    level=AgentLevel.EXECUTION,
    description="Agent with knowledge base"
)
agent = KnowledgeAgent(config, rag)

# Query knowledge
result = await agent.execute_action("query_knowledge", {
    "query": "vacation policy",
    "top_k": 3
})
print(f"Found {result['context_count']} documents")

# Generate with knowledge
result = await agent.execute_action("generate_with_knowledge", {
    "query": "What's our PTO policy?",
    "use_llm": True
})
print(result['generated_response'])

# Add knowledge
await agent.execute_action("add_knowledge", {
    "doc_id": "policy_123",
    "text": "New company policy...",
    "metadata": {"type": "policy"}
})

# Delete knowledge
await agent.execute_action("delete_knowledge", {
    "doc_id": "policy_123"
})

# List all
result = await agent.execute_action("list_knowledge", {"limit": 50})
print(f"Total documents: {result['total']}")
```

## Document Format Support

### Text Files (.txt)
```python
# Auto-chunked into ~1000 char chunks
await DocumentIngester.ingest_text_file(
    "handbook.txt", rag,
    chunk_size=1000,      # Characters per chunk
    chunk_overlap=100     # Overlap between chunks
)
```

### Markdown Files (.md)
```python
# Split by heading boundaries (smart chunking)
await DocumentIngester.ingest_markdown_file(
    "guide.md", rag,
    chunk_by_heading=True  # Split at ## headings
)
```

### JSON/JSONL (.json, .jsonl)
```python
# Each JSON object is a document
await DocumentIngester.ingest_json_documents(
    "data.json", rag,
    text_field="description",  # Field containing document text
    id_field="product_id"      # Field for document ID
)

# JSONL format (one JSON per line) also supported
# {"id": "1", "text": "content"}
# {"id": "2", "text": "content"}
```

### Directories
```python
# Recursively ingest all documents
results = await DocumentIngester.ingest_directory(
    "./knowledge_base", rag,
    file_extensions=[".txt", ".md", ".json"],
    recursive=True
)

for file_path, doc_ids in results.items():
    print(f"{file_path}: {len(doc_ids)} documents")
```

## Performance Tips

### Embedding Models

| Model | Size | Speed | Quality | Recommended For |
|-------|------|-------|---------|-----------------|
| all-MiniLM-L6-v2 | Small | ⚡⚡⚡ | Fair | Testing, prototyping |
| text-embedding-3-small | Medium | ⚡⚡ | Good | Production (balanced) |
| text-embedding-3-large | Large | ⚡ | Excellent | High-accuracy needs |

### Chunking Strategy

- **Smaller chunks** (500 chars): More specific results, more documents to process
- **Larger chunks** (2000 chars): Faster processing, broader context
- **Overlap**: Higher overlap preserves context but increases processing

### Similarity Threshold

- `0.3-0.5` — Retrieve lots, filter later
- `0.5-0.7` — Balanced (recommended)
- `0.7-0.9` — High precision, may miss some results
- `0.9+` — Only exact matches

## Troubleshooting

### "ModuleNotFoundError: No module named 'sentence_transformers'"
```bash
# Install local embeddings support
pip install sentence-transformers
```

### "Low similarity scores"
- Use larger model: `text-embedding-3-large`
- Lower threshold: `min_similarity=0.3`
- Rephrase query to match document language

### "Slow ingestion"
- Use LocalEmbeddings (no API latency)
- Increase chunk_size (fewer embeddings)
- Ingest in parallel (batch multiple directories)

### "Out of memory"
- Use SQLiteVectorStore (disk-backed)
- Smaller embedding model
- More aggressive chunking

## Example Workflows

### Multi-Domain Knowledge Bases
```python
# Separate RAG for HR and Product
hr_rag = RAGSystem(
    SQLiteVectorStore(VectorStoreConfig(db_path="hr.db")),
    LocalEmbeddings()
)
product_rag = RAGSystem(
    SQLiteVectorStore(VectorStoreConfig(db_path="product.db")),
    LocalEmbeddings()
)

await DocumentIngester.ingest_directory("./hr_docs", hr_rag)
await DocumentIngester.ingest_directory("./product_docs", product_rag)
```

### Knowledge + Smart Agents
```python
# Combine RAG with existing smart agents
rag = RAGSystem(...)
await DocumentIngester.ingest_directory("./docs", rag)

# Use in booking workflow
result = await rag.generate_with_context(
    query=f"What are the benefits? {user_question}",
    top_k=3
)
```

### Custom Metadata Tagging
```python
# Tag documents for categorization
await rag.add_knowledge(
    doc_id="policy_2024_vacation",
    text="Vacation policy...",
    metadata={
        "year": 2024,
        "category": "HR",
        "department": "HR",
        "version": 1.2,
        "source": "handbook.pdf"
    }
)
# Future: support metadata filtering
```

## API Summary

### RAGSystem
- `add_knowledge(doc_id, text, metadata)` — Add document
- `retrieve_context(query, top_k, min_similarity)` — Search
- `generate_with_context(query, ...)` — Retrieve + generate
- `delete_knowledge(doc_id)` — Remove document
- `list_knowledge(limit)` — List all documents
- `get_knowledge(doc_id)` — Get specific document

### DocumentIngester
- `ingest_text_file(path, rag, chunk_size, chunk_overlap)`
- `ingest_markdown_file(path, rag, chunk_by_heading)`
- `ingest_json_documents(path, rag, text_field, id_field)`
- `ingest_directory(path, rag, file_extensions, recursive)`

### KnowledgeAgent (Actions)
- `query_knowledge` — Search knowledge base
- `add_knowledge` — Add documents
- `delete_knowledge` — Remove documents
- `list_knowledge` — List documents
- `generate_with_knowledge` — RAG-enhanced generation

## See Also
- [RAG_GUIDE.md](RAG_GUIDE.md) — Comprehensive documentation
- [examples_rag.py](examples_rag.py) — Working code examples
