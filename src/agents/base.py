"""
Base Agent - Abstract base class for all marketing agents.
Provides lifecycle hooks, LLM integration, and shared utilities.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional

from src.core.llm import LLMClient

logger = logging.getLogger("mimo-marketing.agents")


class BaseAgent(ABC):
    """
    Abstract base agent with lifecycle management.
    
    All agents inherit from this and implement:
    - start(): Initialize resources
    - stop(): Cleanup resources
    - execute(): Handle dispatched tasks
    """
    
    def __init__(self, name: str, llm: Optional[LLMClient] = None):
        self.name = name
        self.llm = llm or LLMClient()
        self._running = False
        logger.info(f"Agent '{name}' initialized")
    
    async def start(self):
        """Start the agent. Override for custom initialization."""
        self._running = True
        logger.info(f"Agent '{self.name}' started")
    
    async def stop(self):
        """Stop the agent. Override for custom cleanup."""
        self._running = False
        await self.llm.close()
        logger.info(f"Agent '{self.name}' stopped")
    
    @abstractmethod
    async def execute(self, payload: dict) -> dict:
        """
        Execute a task dispatched by the kernel.
        
        Args:
            payload: Task parameters with 'action' key
            
        Returns:
            Response dict
        """
        ...
    
    @property
    def is_running(self) -> bool:
        return self._running
