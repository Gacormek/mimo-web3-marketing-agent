"""
Narrative Agent - Detect and track trending Web3 narratives.
Monitors CT trends, DeFi narratives, and suggests content angles.
"""

import logging
from typing import Dict, List

from src.agents.base import BaseAgent

logger = logging.getLogger("mimo-marketing.narrative")

NARRATIVES_DB = {
    "L2_season": {
        "keywords": ["layer 2", "L2", "rollup", "arbitrum", "optimism", "base", "zksync"],
        "description": "Layer 2 scaling solutions gaining traction",
        "marketing_angle": "Lower fees, faster transactions, same security as Ethereum",
    },
    "RWA_tokenization": {
        "keywords": ["RWA", "real world assets", "tokenization", "treasury", "bonds"],
        "description": "Real-world assets being tokenized on-chain",
        "marketing_angle": "TradFi meets DeFi — institutional-grade assets on-chain",
    },
    "AI_crypto": {
        "keywords": ["AI agent", "autonomous agent", "AI trading", "AI DeFi"],
        "description": "AI agents interacting with blockchain protocols",
        "marketing_angle": "AI-powered DeFi — agents that trade, yield farm, and manage portfolios",
    },
    "restaking": {
        "keywords": ["restaking", "eigenlayer", "liquid restaking", "LRT"],
        "description": "Restaking protocols extending Ethereum security",
        "marketing_angle": "Earn yield on yield — restaking maximizes capital efficiency",
    },
    "depin": {
        "keywords": ["DePIN", "decentralized infrastructure", "physical infrastructure"],
        "description": "Decentralized physical infrastructure networks",
        "marketing_angle": "Own the infrastructure — decentralized wireless, compute, storage",
    },
    "meme_season": {
        "keywords": ["meme coin", "memecoin", "PEPE", "DOGE", "WIF", "BONK"],
        "description": "Meme coin cultural movement",
        "marketing_angle": "Culture meets finance — community-driven value creation",
    },
    "gaming_tokens": {
        "keywords": ["GameFi", "play to earn", "gaming token", "NFT game"],
        "description": "Gaming and metaverse token ecosystems",
        "marketing_angle": "Play and earn — gaming economies powered by blockchain",
    },
}


class NarrativeAgent(BaseAgent):
    """
    Web3 narrative tracking and content suggestion agent.
    
    Capabilities:
    - Track trending narratives across CT
    - Match project features to hot narratives
    - Suggest content angles based on trends
    - Narrative scoring and prioritization
    """
    
    def __init__(self):
        super().__init__("NarrativeAgent")
    
    async def execute(self, payload: dict) -> dict:
        action = payload.get("action", "analyze")
        
        if action == "analyze":
            return await self._analyze(payload)
        elif action == "match":
            return await self._match_narrative(payload)
        elif action == "trending":
            return self._get_trending()
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _analyze(self, payload: dict) -> dict:
        """Analyze current narratives and suggest content."""
        chain = payload.get("chain", "ethereum")
        timeframe = payload.get("timeframe", "24h")
        
        # Score narratives based on keyword relevance
        scored_narratives = []
        for name, data in NARRATIVES_DB.items():
            scored_narratives.append({
                "narrative": name,
                "description": data["description"],
                "marketing_angle": data["marketing_angle"],
                "keywords": data["keywords"],
                "relevance_score": len(data["keywords"]) / 10,  # Simplified scoring
            })
        
        scored_narratives.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Generate narrative analysis via LLM
        top_narratives = scored_narratives[:5]
        narrative_summary = "\n".join(
            f"- {n['narrative']}: {n['description']} (angle: {n['marketing_angle']})"
            for n in top_narratives
        )
        
        analysis = await self.llm.generate(
            system_prompt="You are a Web3 market analyst. Analyze these narratives and suggest marketing content angles.",
            user_prompt=f"Current trending narratives on {chain} ({timeframe}):\n{narrative_summary}\n\nSuggest 3-5 specific content ideas that leverage these narratives.",
            temperature=0.7,
        )
        
        return {
            "agent": self.name,
            "chain": chain,
            "timeframe": timeframe,
            "top_narratives": top_narratives,
            "content_suggestions": analysis,
        }
    
    async def _match_narrative(self, payload: dict) -> dict:
        """Match a project to relevant narratives."""
        project_features = payload.get("features", [])
        project_description = payload.get("description", "")
        
        # Find matching narratives
        matches = []
        for name, data in NARRATIVES_DB.items():
            match_score = 0
            for feature in project_features:
                for keyword in data["keywords"]:
                    if keyword.lower() in feature.lower():
                        match_score += 1
            if match_score > 0:
                matches.append({
                    "narrative": name,
                    "match_score": match_score,
                    "marketing_angle": data["marketing_angle"],
                })
        
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "agent": self.name,
            "matches": matches[:5],
            "top_narrative": matches[0] if matches else None,
        }
    
    def _get_trending(self) -> dict:
        """Get current trending narratives."""
        return {
            "agent": self.name,
            "narratives": [
                {"name": name, "description": data["description"]}
                for name, data in NARRATIVES_DB.items()
            ],
            "count": len(NARRATIVES_DB),
        }
