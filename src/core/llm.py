"""
MiMo LLM Client - Wraps API calls to MiMo-compatible LLM endpoints.
Supports OpenAI-compatible APIs (MiMo, Claude, GPT, etc.)
"""

import os
import json
import logging
import asyncio
from typing import List, Dict, Optional, AsyncIterator
from dataclasses import dataclass

import httpx

logger = logging.getLogger("mimo-marketing.llm")

# Default to MiMo-compatible endpoint
DEFAULT_BASE_URL = os.getenv("LLM_BASE_URL")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "xmtp/mimo-v2.5-pro")
DEFAULT_API_KEY = os.getenv("LLM_API_KEY", "your_api_key_here")


@dataclass
class LLMResponse:
    """Structured LLM response."""
    content: str
    model: str
    tokens_used: int
    finish_reason: str


class LLMClient:
    """
    Async LLM client for MiMo-compatible APIs.
    
    Features:
    - Streaming support
    - Automatic retry with backoff
    - Token counting
    - Structured output parsing
    """
    
    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        api_key: str = DEFAULT_API_KEY,
        max_retries: int = 3,
        timeout: float = 120.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.max_retries = max_retries
        self.timeout = timeout
        self.total_tokens = 0
        
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(timeout),
        )
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format: Optional[dict] = None,
    ) -> LLMResponse:
        """
        Send a chat completion request.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model override
            temperature: Sampling temperature
            max_tokens: Max response tokens
            response_format: Optional JSON mode
            
        Returns:
            LLMResponse with generated content
        """
        payload = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        if response_format:
            payload["response_format"] = response_format
        
        for attempt in range(self.max_retries):
            try:
                resp = await self._client.post("/chat/completions", json=payload)
                resp.raise_for_status()
                data = resp.json()
                
                usage = data.get("usage", {})
                self.total_tokens += usage.get("total_tokens", 0)
                
                choice = data["choices"][0]
                return LLMResponse(
                    content=choice["message"]["content"],
                    model=data.get("model", self.model),
                    tokens_used=usage.get("total_tokens", 0),
                    finish_reason=choice.get("finish_reason", "stop"),
                )
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    wait = 2 ** attempt
                    logger.warning(f"Rate limited, retrying in {wait}s...")
                    await asyncio.sleep(wait)
                else:
                    raise
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"LLM call failed (attempt {attempt+1}): {e}")
                await asyncio.sleep(1)
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        **kwargs,
    ) -> str:
        """Simplified interface - system + user prompt → response text."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        response = await self.chat(messages, **kwargs)
        return response.content
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
