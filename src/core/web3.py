"""
Web3 Data Fetcher - On-chain data retrieval and analysis.
Uses Alchemy API for multi-chain support.
"""

import os
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

import httpx

logger = logging.getLogger("mimo-marketing.web3")

ALCHEMY_KEY = os.getenv("ALCHEMY_API_KEY", "")

# Supported chains and their Alchemy network identifiers
CHAIN_MAP = {
    "ethereum": "eth-mainnet",
    "polygon": "polygon-mainnet",
    "arbitrum": "arb-mainnet",
    "optimism": "opt-mainnet",
    "base": "base-mainnet",
    "bsc": "bnb-mainnet",
    "avalanche": "avax-mainnet",
    "zksync": "zksync-mainnet",
    "linea": "linea-mainnet",
}


@dataclass
class TokenMetrics:
    """On-chain token metrics."""
    address: str
    chain: str
    holder_count: int = 0
    transfer_count_24h: int = 0
    unique_senders_24h: int = 0
    unique_receivers_24h: int = 0
    total_supply: str = "0"
    whale_holders: List[Dict] = None
    
    def __post_init__(self):
        if self.whale_holders is None:
            self.whale_holders = []


@dataclass
class ContractInfo:
    """Smart contract information."""
    address: str
    chain: str
    is_verified: bool = False
    deployment_date: Optional[str] = None
    transaction_count: int = 0
    abi: Optional[list] = None


class Web3DataFetcher:
    """
    Fetch on-chain data via Alchemy APIs.
    
    Features:
    - Multi-chain support (9 chains)
    - Token holder analytics
    - Transaction volume tracking
    - Whale activity monitoring
    - Smart contract verification
    """
    
    def __init__(self, api_key: str = ALCHEMY_KEY):
        self.api_key = api_key
        self._client = httpx.AsyncClient(timeout=30.0)
    
    def _get_rpc_url(self, chain: str) -> str:
        """Get Alchemy RPC URL for a chain."""
        network = CHAIN_MAP.get(chain, "eth-mainnet")
        return f"https://{network}.g.alchemy.com/v2/{self.api_key}"
    
    async def get_token_metadata(self, address: str, chain: str = "ethereum") -> Dict:
        """Get ERC-20 token metadata."""
        url = self._get_rpc_url(chain)
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "alchemy_getTokenMetadata",
            "params": [address],
        }
        try:
            resp = await self._client.post(url, json=payload)
            data = resp.json()
            return data.get("result", {})
        except Exception as e:
            logger.error(f"Token metadata error: {e}")
            return {}
    
    async def get_holder_count(self, address: str, chain: str = "ethereum") -> int:
        """
        Estimate holder count using Alchemy's getTokenBalances.
        Note: Exact count requires indexing service; this uses sampling.
        """
        url = self._get_rpc_url(chain)
        # Use alchemy_getAssetTransfers to count unique receivers
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "alchemy_getAssetTransfers",
            "params": [{
                "fromBlock": "0x0",
                "toBlock": "latest",
                "contractAddresses": [address],
                "category": ["erc20"],
                "maxCount": "0x3E8",  # 1000
            }],
        }
        try:
            resp = await self._client.post(url, json=payload)
            data = resp.json()
            transfers = data.get("result", {}).get("transfers", [])
            unique_addresses = set()
            for t in transfers:
                unique_addresses.add(t.get("to", "").lower())
                unique_addresses.add(t.get("from", "").lower())
            unique_addresses.discard("")
            return len(unique_addresses)
        except Exception as e:
            logger.error(f"Holder count error: {e}")
            return 0
    
    async def get_recent_transfers(
        self, address: str, chain: str = "ethereum", limit: int = 100
    ) -> List[Dict]:
        """Get recent ERC-20 transfers for a token."""
        url = self._get_rpc_url(chain)
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "alchemy_getAssetTransfers",
            "params": [{
                "fromBlock": "0x0",
                "toBlock": "latest",
                "contractAddresses": [address],
                "category": ["erc20"],
                "maxCount": hex(limit),
            }],
        }
        try:
            resp = await self._client.post(url, json=payload)
            data = resp.json()
            return data.get("result", {}).get("transfers", [])
        except Exception as e:
            logger.error(f"Transfer fetch error: {e}")
            return []
    
    async def get_token_metrics(
        self, address: str, chain: str = "ethereum"
    ) -> TokenMetrics:
        """Aggregate token metrics for marketing content."""
        metadata = await self.get_token_metadata(address, chain)
        holder_count = await self.get_holder_count(address, chain)
        transfers = await self.get_recent_transfers(address, chain, 500)
        
        unique_senders = set()
        unique_receivers = set()
        for t in transfers:
            if t.get("from"):
                unique_senders.add(t["from"].lower())
            if t.get("to"):
                unique_receivers.add(t["to"].lower())
        
        return TokenMetrics(
            address=address,
            chain=chain,
            holder_count=holder_count,
            transfer_count_24h=len(transfers),
            unique_senders_24h=len(unique_senders),
            unique_receivers_24h=len(unique_receivers),
            total_supply=metadata.get("totalSupply", "0"),
        )
    
    async def get_gas_price(self, chain: str = "ethereum") -> Dict:
        """Get current gas prices."""
        url = self._get_rpc_url(chain)
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_gasPrice",
            "params": [],
        }
        try:
            resp = await self._client.post(url, json=payload)
            data = resp.json()
            gas_wei = int(data.get("result", "0x0"), 16)
            return {
                "chain": chain,
                "gas_wei": gas_wei,
                "gas_gwei": gas_wei / 1e9,
                "gas_eth": gas_wei / 1e18,
            }
        except Exception as e:
            logger.error(f"Gas price error: {e}")
            return {"chain": chain, "gas_wei": 0, "gas_gwei": 0, "gas_eth": 0}
    
    async def close(self):
        """Close HTTP client."""
        await self._client.aclose()
