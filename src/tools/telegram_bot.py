"""
Telegram Bot Integration - Community management via Telegram.
"""

import os
import logging
from typing import Optional

import httpx

logger = logging.getLogger("mimo-marketing.telegram")


class TelegramBot:
    """
    Telegram bot for Web3 community management.
    
    Capabilities:
    - Answer FAQ using RAG
    - Post announcements to channels
    - Handle DMs for project info
    - Auto-moderate with Web3 context
    """
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self._client = httpx.AsyncClient(timeout=30.0)
        self._base_url = f"https://api.telegram.org/bot{self.token}"
    
    async def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: str = "Markdown",
    ) -> dict:
        """Send a message to a Telegram chat."""
        try:
            resp = await self._client.post(
                f"{self._base_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": parse_mode,
                },
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
            return {"error": str(e)}
    
    async def send_to_channel(self, channel: str, text: str) -> dict:
        """Send a message to a Telegram channel."""
        return await self.send_message(channel, text)
    
    async def close(self):
        """Close HTTP client."""
        await self._client.aclose()
