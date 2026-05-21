"""
RAG Pipeline - Retrieval-Augmented Generation for grounded content.
Uses ChromaDB for vector storage and semantic search.
"""

import os
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger("mimo-marketing.rag")

try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    logger.warning("ChromaDB not installed - RAG pipeline in mock mode")


@dataclass
class Document:
    """A document chunk for ingestion."""
    content: str
    metadata: Dict[str, str]
    doc_id: Optional[str] = None


@dataclass
class SearchResult:
    """A search result from the vector store."""
    content: str
    score: float
    metadata: Dict[str, str]


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline.
    
    Features:
    - Document ingestion with chunking
    - Semantic search via embeddings
    - Project-scoped collections
    - Context assembly for LLM prompts
    """
    
    def __init__(self, persist_dir: str = "./data/chromadb"):
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)
        
        if HAS_CHROMADB:
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=persist_dir,
                anonymized_telemetry=False,
            ))
        else:
            self.client = None
        
        self._collections: Dict[str, any] = {}
    
    def _get_collection(self, project_id: str):
        """Get or create a project collection."""
        if project_id not in self._collections:
            if self.client:
                self._collections[project_id] = self.client.get_or_create_collection(
                    name=f"project_{project_id}",
                    metadata={"hnsw:space": "cosine"},
                )
            else:
                self._collections[project_id] = []  # Mock mode
        return self._collections[project_id]
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        return chunks
    
    async def ingest(
        self,
        documents: List[Document],
        project_id: str = "default",
    ) -> Dict:
        """
        Ingest documents into the vector store.
        
        Args:
            documents: List of Document objects
            project_id: Project identifier for collection scoping
            
        Returns:
            Ingestion stats
        """
        collection = self._get_collection(project_id)
        total_chunks = 0
        
        for doc in documents:
            chunks = self._chunk_text(doc.content)
            for i, chunk in enumerate(chunks):
                doc_id = f"{doc.doc_id or 'doc'}_chunk_{i}"
                
                if self.client and hasattr(collection, "add"):
                    collection.add(
                        documents=[chunk],
                        metadatas=[{**doc.metadata, "chunk_index": i}],
                        ids=[doc_id],
                    )
                else:
                    collection.append({
                        "id": doc_id,
                        "content": chunk,
                        "metadata": {**doc.metadata, "chunk_index": i},
                    })
                total_chunks += 1
        
        return {
            "project_id": project_id,
            "documents_ingested": len(documents),
            "total_chunks": total_chunks,
        }
    
    async def search(
        self,
        query: str,
        project_id: str = "default",
        top_k: int = 5,
    ) -> List[SearchResult]:
        """
        Semantic search across project documents.
        
        Args:
            query: Search query
            project_id: Project to search in
            top_k: Number of results
            
        Returns:
            List of SearchResult ordered by relevance
        """
        collection = self._get_collection(project_id)
        
        if self.client and hasattr(collection, "query"):
            results = collection.query(
                query_texts=[query],
                n_results=top_k,
            )
            return [
                SearchResult(
                    content=doc,
                    score=1 - dist,
                    metadata=meta,
                )
                for doc, dist, meta in zip(
                    results["documents"][0],
                    results["distances"][0],
                    results["metadatas"][0],
                )
            ]
        else:
            # Mock mode - simple keyword matching
            scored = []
            for item in collection:
                score = sum(
                    1 for word in query.lower().split()
                    if word in item["content"].lower()
                ) / max(len(query.split()), 1)
                if score > 0:
                    scored.append(SearchResult(
                        content=item["content"],
                        score=score,
                        metadata=item["metadata"],
                    ))
            scored.sort(key=lambda x: x.score, reverse=True)
            return scored[:top_k]
    
    async def get_context(
        self,
        query: str,
        project_id: str = "default",
        max_tokens: int = 2000,
    ) -> str:
        """
        Get assembled context string for LLM prompt.
        
        Returns:
            Concatenated relevant document chunks, truncated to max_tokens.
        """
        results = await self.search(query, project_id)
        context_parts = []
        total_words = 0
        
        for result in results:
            words = result.content.split()
            if total_words + len(words) > max_tokens * 0.75:
                break
            context_parts.append(result.content)
            total_words += len(words)
        
        return "\n\n---\n\n".join(context_parts)
