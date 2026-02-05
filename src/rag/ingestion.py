"""Document ingestion utilities for RAG systems."""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import json
from .rag_system import RAGSystem

logger = logging.getLogger(__name__)


class DocumentIngester:
    """Utilities for ingesting various document types."""
    
    @staticmethod
    async def ingest_text_file(
        file_path: str,
        rag_system: RAGSystem,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
    ) -> List[str]:
        """
        Ingest a text file by chunking it.
        
        Args:
            file_path: Path to text file
            rag_system: RAGSystem instance
            chunk_size: Characters per chunk
            chunk_overlap: Overlap between chunks
        
        Returns:
            List of document IDs
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            doc_ids = []
            chunks = DocumentIngester._chunk_text(
                content,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            
            for i, chunk in enumerate(chunks):
                doc_id = f"{Path(file_path).stem}_chunk_{i}"
                metadata = {
                    "source": file_path,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "type": "text",
                }
                
                success = await rag_system.add_knowledge(
                    doc_id=doc_id,
                    text=chunk,
                    metadata=metadata,
                )
                if success:
                    doc_ids.append(doc_id)
            
            logger.info(f"Ingested {len(doc_ids)} chunks from {file_path}")
            return doc_ids
        except Exception as e:
            logger.error(f"Error ingesting text file: {e}")
            return []
    
    @staticmethod
    async def ingest_json_documents(
        file_path: str,
        rag_system: RAGSystem,
        text_field: str = "text",
        id_field: str = "id",
    ) -> List[str]:
        """
        Ingest JSON documents (JSONL or JSON array).
        
        Args:
            file_path: Path to JSON file
            rag_system: RAGSystem instance
            text_field: Field name containing document text
            id_field: Field name containing document ID
        
        Returns:
            List of document IDs
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return []
        
        try:
            doc_ids = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try parsing as JSONL first
            documents = []
            for line in content.strip().split('\n'):
                if line.strip():
                    try:
                        documents.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            
            # If no JSONL, try JSON array
            if not documents:
                try:
                    documents = json.loads(content)
                    if not isinstance(documents, list):
                        documents = [documents]
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON format: {file_path}")
                    return []
            
            for doc in documents:
                if text_field not in doc:
                    logger.warning(f"Document missing text field '{text_field}'")
                    continue
                
                doc_id = doc.get(id_field, f"doc_{len(doc_ids)}")
                text = doc[text_field]
                
                # Prepare metadata from remaining fields
                metadata = {k: v for k, v in doc.items() if k not in [text_field, id_field]}
                metadata["source"] = file_path
                metadata["type"] = "json"
                
                success = await rag_system.add_knowledge(
                    doc_id=doc_id,
                    text=text,
                    metadata=metadata,
                )
                if success:
                    doc_ids.append(doc_id)
            
            logger.info(f"Ingested {len(doc_ids)} documents from {file_path}")
            return doc_ids
        except Exception as e:
            logger.error(f"Error ingesting JSON file: {e}")
            return []
    
    @staticmethod
    async def ingest_markdown_file(
        file_path: str,
        rag_system: RAGSystem,
        chunk_by_heading: bool = True,
    ) -> List[str]:
        """
        Ingest Markdown file (with optional heading-based chunking).
        
        Args:
            file_path: Path to markdown file
            rag_system: RAGSystem instance
            chunk_by_heading: Split chunks at heading boundaries
        
        Returns:
            List of document IDs
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            doc_ids = []
            
            if chunk_by_heading:
                chunks = DocumentIngester._chunk_markdown_by_heading(content)
            else:
                chunks = DocumentIngester._chunk_text(content, chunk_size=1000, chunk_overlap=100)
            
            for i, (heading, chunk_text) in enumerate(chunks):
                doc_id = f"{Path(file_path).stem}_section_{i}"
                metadata = {
                    "source": file_path,
                    "heading": heading,
                    "section_index": i,
                    "type": "markdown",
                }
                
                success = await rag_system.add_knowledge(
                    doc_id=doc_id,
                    text=chunk_text,
                    metadata=metadata,
                )
                if success:
                    doc_ids.append(doc_id)
            
            logger.info(f"Ingested {len(doc_ids)} sections from {file_path}")
            return doc_ids
        except Exception as e:
            logger.error(f"Error ingesting markdown file: {e}")
            return []
    
    @staticmethod
    async def ingest_directory(
        directory_path: str,
        rag_system: RAGSystem,
        file_extensions: List[str] = None,
        recursive: bool = True,
    ) -> Dict[str, List[str]]:
        """
        Ingest all documents in a directory.
        
        Args:
            directory_path: Path to directory
            rag_system: RAGSystem instance
            file_extensions: List of extensions to include (e.g., ['.txt', '.md', '.json'])
            recursive: Whether to search subdirectories
        
        Returns:
            Dict mapping file paths to list of document IDs
        """
        if not os.path.isdir(directory_path):
            logger.error(f"Directory not found: {directory_path}")
            return {}
        
        if file_extensions is None:
            file_extensions = ['.txt', '.md', '.json', '.jsonl']
        
        results = {}
        
        try:
            path_obj = Path(directory_path)
            pattern = '**/*' if recursive else '*'
            
            for file_path in path_obj.glob(pattern):
                if not file_path.is_file():
                    continue
                
                if file_path.suffix.lower() not in file_extensions:
                    continue
                
                file_str = str(file_path)
                logger.info(f"Ingesting {file_str}")
                
                if file_path.suffix.lower() == '.md':
                    doc_ids = await DocumentIngester.ingest_markdown_file(file_str, rag_system)
                elif file_path.suffix.lower() in ['.json', '.jsonl']:
                    doc_ids = await DocumentIngester.ingest_json_documents(file_str, rag_system)
                else:
                    doc_ids = await DocumentIngester.ingest_text_file(file_str, rag_system)
                
                results[file_str] = doc_ids
            
            logger.info(f"Ingested {sum(len(v) for v in results.values())} documents from directory")
            return results
        except Exception as e:
            logger.error(f"Error ingesting directory: {e}")
            return {}
    
    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 100) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - chunk_overlap
        
        return chunks
    
    @staticmethod
    def _chunk_markdown_by_heading(content: str) -> List[Tuple[str, str]]:
        """Split markdown by headings."""
        sections = []
        current_heading = "Introduction"
        current_content = []
        
        for line in content.split('\n'):
            if line.startswith('#'):
                # Save previous section
                if current_content:
                    text = '\n'.join(current_content).strip()
                    if text:
                        sections.append((current_heading, text))
                
                # Start new section
                current_heading = line.lstrip('#').strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Don't forget last section
        if current_content:
            text = '\n'.join(current_content).strip()
            if text:
                sections.append((current_heading, text))
        
        return sections if sections else [("Document", content)]
