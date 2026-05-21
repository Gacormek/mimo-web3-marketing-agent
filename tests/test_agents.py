"""
Tests for MiMo Web3 Marketing Agent.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from src.agents.content_agent import ContentAgent
from src.agents.analytics_agent import AnalyticsAgent
from src.agents.narrative_agent import NarrativeAgent
from src.agents.social_agent import SocialAgent
from src.agents.rag_agent import RAGAgent
from src.core.kernel import AgentKernel


@pytest.fixture
def mock_llm():
    """Mock LLM client."""
    llm = AsyncMock()
    llm.generate = AsyncMock(return_value='{"content": "Test content", "hashtags": ["#web3"]}')
    llm.chat = AsyncMock(return_value=MagicMock(
        content="Test response",
        tokens_used=100,
        finish_reason="stop",
    ))
    llm.close = AsyncMock()
    return llm


@pytest.mark.asyncio
async def test_content_agent_generate(mock_llm):
    """Test content generation."""
    agent = ContentAgent()
    agent.llm = mock_llm
    
    result = await agent.execute({
        "action": "generate",
        "project": {"name": "TestProject", "features": ["DeFi", "NFT"]},
        "content_type": "tweet",
        "tone": "engaging",
        "chain": "ethereum",
    })
    
    assert "agent" in result
    assert result["agent"] == "ContentAgent"
    assert result["content_type"] == "tweet"
    mock_llm.generate.assert_called_once()


@pytest.mark.asyncio
async def test_narrative_agent_trending():
    """Test narrative trending."""
    agent = NarrativeAgent()
    
    result = await agent.execute({"action": "trending"})
    
    assert "narratives" in result
    assert result["count"] > 0
    assert all("name" in n for n in result["narratives"])


@pytest.mark.asyncio
async def test_narrative_agent_match():
    """Test narrative matching."""
    agent = NarrativeAgent()
    
    result = await agent.execute({
        "action": "match",
        "features": ["Layer 2 scaling", "rollup technology"],
        "description": "An L2 scaling solution",
    })
    
    assert "matches" in result
    if result["matches"]:
        assert result["matches"][0]["match_score"] > 0


@pytest.mark.asyncio
async def test_social_agent_campaign(mock_llm):
    """Test campaign creation."""
    agent = SocialAgent()
    agent.llm = mock_llm
    
    result = await agent.execute({
        "action": "campaign",
        "config": {
            "name": "Test Campaign",
            "platform": "twitter",
            "frequency": "daily",
            "duration_days": 7,
        },
    })
    
    assert result["campaign"] == "Test Campaign"
    assert result["status"] == "created"


@pytest.mark.asyncio
async def test_kernel_dispatch():
    """Test kernel task dispatch."""
    kernel = AgentKernel()
    
    mock_agent = AsyncMock()
    mock_agent.execute = AsyncMock(return_value={"result": "ok"})
    mock_agent.start = AsyncMock()
    mock_agent.stop = AsyncMock()
    
    kernel.register("test", mock_agent)
    await kernel.start_all()
    
    result = await kernel.dispatch("test", {"action": "test"})
    assert result == {"result": "ok"}
    
    status = kernel.status()
    assert "test" in status
    assert status["test"]["state"] == "running"


@pytest.mark.asyncio
async def test_kernel_unknown_agent():
    """Test kernel with unknown agent."""
    kernel = AgentKernel()
    result = await kernel.dispatch("nonexistent", {"action": "test"})
    assert "error" in result
