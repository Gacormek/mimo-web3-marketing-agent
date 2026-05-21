"""
Agent Kernel - Lifecycle management for all agents.
Handles spawn, kill, restart, health checks, and inter-agent communication.
"""

import asyncio
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger("mimo-marketing.kernel")


class AgentState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class AgentHealth:
    """Health status for an agent."""
    state: AgentState = AgentState.IDLE
    last_heartbeat: Optional[datetime] = None
    error_count: int = 0
    total_tasks: int = 0
    avg_latency_ms: float = 0.0
    uptime_seconds: float = 0.0


class AgentKernel:
    """
    Central kernel managing agent lifecycle.
    
    Responsibilities:
    - Register and manage agent instances
    - Dispatch tasks to appropriate agents
    - Monitor agent health
    - Handle graceful shutdown
    """
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.health: Dict[str, AgentHealth] = {}
        self._tasks: Dict[str, asyncio.Task] = {}
        logger.info("AgentKernel initialized")
    
    def register(self, name: str, agent: Any) -> None:
        """Register an agent with the kernel."""
        self.agents[name] = agent
        self.health[name] = AgentHealth()
        logger.info(f"Registered agent: {name}")
    
    async def start_all(self) -> None:
        """Start all registered agents."""
        for name, agent in self.agents.items():
            try:
                if hasattr(agent, "start"):
                    await agent.start()
                self.health[name].state = AgentState.RUNNING
                self.health[name].last_heartbeat = datetime.utcnow()
                logger.info(f"Started agent: {name}")
            except Exception as e:
                self.health[name].state = AgentState.ERROR
                self.health[name].error_count += 1
                logger.error(f"Failed to start {name}: {e}")
    
    async def stop_all(self) -> None:
        """Gracefully stop all agents."""
        for name, agent in self.agents.items():
            try:
                if hasattr(agent, "stop"):
                    await agent.stop()
                self.health[name].state = AgentState.STOPPED
                logger.info(f"Stopped agent: {name}")
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")
    
    async def dispatch(self, agent_name: str, payload: dict) -> dict:
        """
        Dispatch a task to a specific agent.
        
        Args:
            agent_name: Name of the target agent
            payload: Task payload with action and parameters
            
        Returns:
            Agent response dict
        """
        if agent_name not in self.agents:
            return {"error": f"Agent '{agent_name}' not found"}
        
        agent = self.agents[agent_name]
        health = self.health[agent_name]
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            result = await agent.execute(payload)
            elapsed = (asyncio.get_event_loop().time() - start_time) * 1000
            
            health.total_tasks += 1
            health.avg_latency_ms = (
                (health.avg_latency_ms * (health.total_tasks - 1) + elapsed)
                / health.total_tasks
            )
            health.last_heartbeat = datetime.utcnow()
            
            return result
            
        except Exception as e:
            health.error_count += 1
            health.state = AgentState.ERROR
            logger.error(f"Agent {agent_name} error: {e}")
            return {"error": str(e)}
    
    def status(self) -> dict:
        """Get status of all agents."""
        return {
            name: {
                "state": h.state.value,
                "tasks": h.total_tasks,
                "errors": h.error_count,
                "avg_latency_ms": round(h.avg_latency_ms, 2),
                "last_heartbeat": h.last_heartbeat.isoformat() if h.last_heartbeat else None,
            }
            for name, h in self.health.items()
        }
