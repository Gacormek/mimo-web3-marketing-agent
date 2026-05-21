"""
Twitter/X API Integration - Post and manage tweets.
Uses Twitter API v2 for posting content.
"""

import os
import logging
from typing import Dict, Optional

import httpx

logger = logging.getLogger("mimo-marketing.twitter")

TWITTER_API_BASE = "https://api.twitter.com/2"


class TwitterClient:
    """
    Twitter API v2 client for posting content.
    
    Capabilities:
    - Post tweets
    - Post threads
    - Get engagement metrics
    - Search tweets
    """
    
    def __init__(self, bearer_token: Optional[str] = None):
        self.bearer_token = bearer_token or os.getenv("TWITTER_BEARER_TOKEN", "")
        self._client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.bearer_token}"},
            timeout=30.0,
        )
    
    async def post_tweet(self, text: str, reply_to: Optional[str] = None) -> Dict:
        """
        Post a single tweet.
        
        Args:
            text: Tweet content (max 280 chars)
            reply_to: Optional tweet ID to reply to
            
        Returns:
            Tweet data with ID
        """
        payload = {"text": text}
        if reply_to:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to}
        
        try:
            resp = await self._client.post(
                f"{TWITTER_API_BASE}/tweets",
                json=payload,
            )
            resp.raise_for_status()
            return resp.json().get("data", {})
        except Exception as e:
            logger.error(f"Tweet post error: {e}")
            return {"error": str(e)}
    
    async def post_thread(self, tweets: list[str]) -> Dict:
        """
        Post a thread of tweets.
        
        Args:
            tweets: List of tweet texts
            
        Returns:
            List of tweet IDs
        """
        tweet_ids = []
        reply_to = None
        
        for text in tweets:
            result = await self.post_tweet(text, reply_to)
            if "error" in result:
                return {"error": result["error"], "posted": len(tweet_ids)}
            tweet_ids.append(result.get("id", ""))
            reply_to = result.get("id")
        
        return {
            "thread_length": len(tweet_ids),
            "tweet_ids": tweet_ids,
            "first_tweet_id": tweet_ids[0] if tweet_ids else None,
        }
    
    async def get_tweet_metrics(self, tweet_id: str) -> Dict:
        """Get engagement metrics for a tweet."""
        try:
            resp = await self._client.get(
                f"{TWITTER_API_BASE}/tweets/{tweet_id}",
                params={"tweet.fields": "public_metrics"},
            )
            resp.raise_for_status()
            data = resp.json().get("data", {})
            return data.get("public_metrics", {})
        except Exception as e:
            logger.error(f"Metrics fetch error: {e}")
            return {}
    
    async def close(self):
        """Close HTTP client."""
        await self._client.aclose()
