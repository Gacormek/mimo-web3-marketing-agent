"""
RAG Agent - Document ingestion and retrieval for grounded content.
Manages the RAG pipeline for project documentation.
"""

import logging
from typing import Dict, List

from src.agents.base import BaseAgent
from src.core.rag import RAGPipeline, Document

logger = logging.getLogger("mimo-marketing.rag")


class RAGAgent(BaseAgent):
    """
    RAG pipeline management agent.
    
    Capabilities:
    - Ingest project documentation
    - Semantic search across docs
    - Context assembly for content generation
    - Multi-project document isolation
    """
    
    def __init__(self):
        super().__init__("RAGAgent")
        self.pipeline = RAGPipeline()
    
    async def execute(self, payload: dict) -> dict:
        action = payload.get("action", "ingest")
        
        if action == "ingest":
            return await self._ingest(payload)
        elif action == "search":
            return await self._search(payload)
        elif action == "context":
            return await self._get_context(payload)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _ingest(self, payload: dict) -> dict:
        """Ingest documents into the RAG pipeline."""
        documents_raw = payload.get("documents", [])
        project_id = payload.get("project_id", "default")
        
        documents = []
        for doc in documents_raw:
            documents.append(Document(
                content=doc.get("content", ""),
                metadata=doc.get("metadata", {}),
                doc_id=doc.get("id"),
            ))
        
        result = await self.pipeline.ingest(documents, project_id)
        
        return {
            "agent": self.name,
            **result,
        }
    
    async def _search(self, payload: dict) -> dict:
        """Search project documents."""
        query = payload.get("query", "")
        project_id = payload.get("project_id", "default")
        top_k = payload.get("top_k", 5)
        
        results = await self.pipeline.search(query, project_id, top_k)
        
        return {
            "agent": self.name,
            "query": query,
            "results": [
                {
                    "content": r.content[:200] + "..." if len(r.content) > 200 else r.content,
                    "score": round(r.score, 4),
                    "metadata": r.metadata,
                }
                for r in results
            ],
            "count": len(results),
        }
    
    async def _get_context(self, payload: dict) -> dict:
        """Get assembled context for LLM prompt."""
        query = payload.get("query", "")
        project_id = payload.get("project_id", "default")
        max_tokens = payload.get("max_tokens", 2000)
        
        context = await self.pipeline.get_context(query, project_id, max_tokens)
        
        return {
            "agent": self.name,
            "query": query,
            "context": context,
            "word_count": len(context.split()),
        }
