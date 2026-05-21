"""
Analytics Agent - On-chain data analysis for marketing insights.
Fetches blockchain data and generates marketing-ready metrics.
"""

import logging
from typing import Dict
from src.agents.base import BaseAgent
from src.core.web3 import Web3DataFetcher

logger = logging.getLogger("mimo-marketing.analytics")

ANALYSIS_PROMPT = """You are MiMo Analytics Agent — an expert at interpreting on-chain data for marketing purposes.

Given the following on-chain metrics, create a marketing-friendly summary:
- Highlight impressive numbers (holder growth, transaction volume)
- Identify trends (increasing activity, whale accumulation)
- Suggest marketing angles based on the data
- Make it digestible for non-technical audiences

Output a JSON object with:
{
    "summary": "one-paragraph marketing summary",
    "key_metrics": {"metric": "value"},
    "marketing_angles": ["angle1", "angle2"],
    "suggested_content_topics": ["topic1", "topic2"]
}
"""


class AnalyticsAgent(BaseAgent):
    """
    On-chain analytics agent for marketing insights.
    
    Capabilities:
    - Fetch token metrics (holders, transfers, supply)
    - Analyze whale activity patterns
    - Generate marketing-friendly summaries
    - Track competitor metrics
    """
    
    def __init__(self):
        super().__init__("AnalyticsAgent")
        self.web3 = Web3DataFetcher()
    
    async def execute(self, payload: dict) -> dict:
        action = payload.get("action", "metrics")
        
        if action == "metrics":
            return await self._get_metrics(payload)
        elif action == "compare":
            return await self._compare_tokens(payload)
        elif action == "whale_alert":
            return await self._whale_alert(payload)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _get_metrics(self, payload: dict) -> dict:
        """Get token metrics and generate marketing summary."""
        address = payload.get("address", "")
        chain = payload.get("chain", "ethereum")
        
        if not address:
            return {"error": "Token address required"}
        
        # Fetch on-chain data
        metrics = await self.web3.get_token_metrics(address, chain)
        metadata = await self.web3.get_token_metadata(address, chain)
        
        # Generate marketing summary via LLM
        data_summary = f"""
Token: {metadata.get('name', 'Unknown')} ({metadata.get('symbol', '???')})
Chain: {chain}
Holders (sampled): {metrics.holder_count}
Recent Transfers: {metrics.transfer_count_24h}
Unique Senders (24h): {metrics.unique_senders_24h}
Unique Receivers (24h): {metrics.unique_receivers_24h}
Total Supply: {metrics.total_supply}
"""
        
        marketing_summary = await self.llm.generate(
            system_prompt=ANALYSIS_PROMPT,
            user_prompt=f"Analyze these on-chain metrics:\n{data_summary}",
            temperature=0.5,
        )
        
        return {
            "agent": self.name,
            "address": address,
            "chain": chain,
            "raw_metrics": {
                "holders": metrics.holder_count,
                "transfers_24h": metrics.transfer_count_24h,
                "unique_senders": metrics.unique_senders_24h,
                "unique_receivers": metrics.unique_receivers_24h,
                "total_supply": metrics.total_supply,
            },
            "token_info": metadata,
            "marketing_analysis": marketing_summary,
        }
    
    async def _compare_tokens(self, payload: dict) -> dict:
        """Compare multiple tokens for competitive analysis."""
        tokens = payload.get("tokens", [])
        chain = payload.get("chain", "ethereum")
        
        results = []
        for addr in tokens[:5]:  # Max 5 tokens
            metrics = await self.web3.get_token_metrics(addr, chain)
            metadata = await self.web3.get_token_metadata(addr, chain)
            results.append({
                "address": addr,
                "name": metadata.get("name", "Unknown"),
                "symbol": metadata.get("symbol", "???"),
                "holders": metrics.holder_count,
                "transfers_24h": metrics.transfer_count_24h,
            })
        
        return {
            "agent": self.name,
            "comparison": results,
            "chain": chain,
        }
    
    async def _whale_alert(self, payload: dict) -> dict:
        """Detect whale activity for marketing alerts."""
        address = payload.get("address", "")
        chain = payload.get("chain", "ethereum")
        threshold = payload.get("threshold_usd", 10000)
        
        transfers = await self.web3.get_recent_transfers(address, chain, 200)
        
        whales = []
        for t in transfers:
            value = float(t.get("value", 0))
            if value >= threshold:
                whales.append({
                    "from": t.get("from", ""),
                    "to": t.get("to", ""),
                    "value": value,
                    "hash": t.get("hash", ""),
                })
        
        return {
            "agent": self.name,
            "whale_transfers": whales,
            "count": len(whales),
            "threshold_usd": threshold,
        }
    
    async def stop(self):
        await self.web3.close()
        await super().stop()
