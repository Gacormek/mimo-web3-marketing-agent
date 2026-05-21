"""
Social Agent - Campaign management and social media scheduling.
Handles post scheduling, campaign creation, and performance tracking.
"""

import logging
from typing import Dict, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from src.agents.base import BaseAgent

logger = logging.getLogger("mimo-marketing.social")


@dataclass
class ScheduledPost:
    """A scheduled social media post."""
    content: str
    platform: str
    scheduled_time: str
    status: str = "pending"
    post_id: str = ""
    engagement: Dict = field(default_factory=dict)


@dataclass
class Campaign:
    """A marketing campaign with multiple posts."""
    name: str
    posts: List[ScheduledPost]
    start_date: str
    end_date: str
    status: str = "draft"
    metrics: Dict = field(default_factory=dict)


class SocialAgent(BaseAgent):
    """
    Social media campaign management agent.
    
    Capabilities:
    - Schedule posts across platforms
    - Create multi-post campaigns
    - Track engagement metrics
    - Optimize posting times
    - Generate campaign reports
    """
    
    def __init__(self):
        super().__init__("SocialAgent")
        self._campaigns: Dict[str, Campaign] = {}
        self._post_queue: List[ScheduledPost] = []
    
    async def execute(self, payload: dict) -> dict:
        action = payload.get("action", "campaign")
        
        if action == "campaign":
            return await self._create_campaign(payload)
        elif action == "schedule":
            return await self._schedule_post(payload)
        elif action == "queue":
            return self._get_queue()
        elif action == "report":
            return self._generate_report(payload)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _create_campaign(self, payload: dict) -> dict:
        """Create a new marketing campaign."""
        config = payload.get("config", {})
        
        name = config.get("name", f"Campaign_{len(self._campaigns) + 1}")
        platform = config.get("platform", "twitter")
        frequency = config.get("frequency", "daily")
        duration_days = config.get("duration_days", 7)
        content_ideas = config.get("content_ideas", [])
        
        # Generate campaign schedule via LLM
        schedule_prompt = f"""Create a {duration_days}-day {frequency} marketing campaign for a Web3 project.
Platform: {platform}
Content ideas: {', '.join(content_ideas) if content_ideas else 'general Web3 marketing'}

Generate a JSON schedule with:
{{
    "campaign_name": "{name}",
    "posts": [
        {{"day": 1, "time": "10:00 UTC", "content_type": "tweet", "topic": "...", "notes": "..."}},
        ...
    ]
}}
Each post should build momentum. Start with awareness, move to education, then conversion."""
        
        schedule_response = await self.llm.generate(
            system_prompt="You are a Web3 social media strategist. Create detailed campaign schedules.",
            user_prompt=schedule_prompt,
            temperature=0.6,
        )
        
        start = datetime.utcnow()
        end = start + timedelta(days=duration_days)
        
        campaign = Campaign(
            name=name,
            posts=[],
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            status="active",
        )
        self._campaigns[name] = campaign
        
        return {
            "agent": self.name,
            "campaign": name,
            "platform": platform,
            "duration_days": duration_days,
            "frequency": frequency,
            "schedule": schedule_response,
            "status": "created",
        }
    
    async def _schedule_post(self, payload: dict) -> dict:
        """Schedule a single post."""
        content = payload.get("content", "")
        platform = payload.get("platform", "twitter")
        scheduled_time = payload.get("scheduled_time", datetime.utcnow().isoformat())
        
        post = ScheduledPost(
            content=content,
            platform=platform,
            scheduled_time=scheduled_time,
        )
        self._post_queue.append(post)
        
        return {
            "agent": self.name,
            "action": "scheduled",
            "platform": platform,
            "scheduled_time": scheduled_time,
            "queue_position": len(self._post_queue),
        }
    
    def _get_queue(self) -> dict:
        """Get current post queue."""
        return {
            "agent": self.name,
            "queue": [
                {
                    "content": p.content[:100] + "..." if len(p.content) > 100 else p.content,
                    "platform": p.platform,
                    "scheduled_time": p.scheduled_time,
                    "status": p.status,
                }
                for p in self._post_queue
            ],
            "total": len(self._post_queue),
        }
    
    def _generate_report(self, payload: dict) -> dict:
        """Generate campaign performance report."""
        campaign_name = payload.get("campaign", "")
        
        if campaign_name in self._campaigns:
            campaign = self._campaigns[campaign_name]
            return {
                "agent": self.name,
                "campaign": campaign_name,
                "status": campaign.status,
                "posts_count": len(campaign.posts),
                "start_date": campaign.start_date,
                "end_date": campaign.end_date,
                "metrics": campaign.metrics,
            }
        
        return {
            "agent": self.name,
            "campaigns": list(self._campaigns.keys()),
            "total": len(self._campaigns),
        }
