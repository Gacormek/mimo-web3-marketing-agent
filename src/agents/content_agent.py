"""
Content Agent - Generate marketing content for Web3 projects.
Produces tweets, threads, articles, and announcements.
"""

import logging
from typing import Dict, List
from src.agents.base import BaseAgent

logger = logging.getLogger("mimo-marketing.content")

SYSTEM_PROMPT = """You are MiMo Web3 Content Agent — an expert Web3 marketing copywriter.

Your job is to create engaging, authentic marketing content for Web3/crypto projects.

Rules:
- Write in a conversational, engaging tone (not corporate)
- Use relevant crypto/Web3 terminology naturally
- Include relevant hashtags and CTAs
- Optimize for engagement (curiosity gaps, social proof, FOMO done tastefully)
- Never make false claims about token price or guaranteed returns
- Always include disclaimers where appropriate

Content types:
- tweet: Short, punchy, max 280 chars
- thread: Multi-tweet thread (5-10 tweets), each under 280 chars
- article: Long-form blog post with sections
- announcement: Official project announcement
- meme_caption: Short, funny, viral-potential caption for meme

Output format (JSON):
{
    "content": "...",
    "hashtags": ["tag1", "tag2"],
    "cta": "call to action",
    "best_posting_time": "suggestion"
}
"""

CONTENT_TEMPLATES = {
    "tweet": "Write a single engaging tweet about {project_name} ({chain} chain). Key features: {features}. Target audience: {audience}. Tone: {tone}.",
    "thread": "Write a Twitter thread (5-7 tweets) about {project_name}. Cover: technology, tokenomics, team, roadmap, and why it matters. Features: {features}.",
    "article": "Write a blog article about {project_name} on {chain}. Cover the problem it solves, how it works, tokenomics, and future vision. Features: {features}.",
    "announcement": "Write an official announcement for {project_name}: {event}. Make it professional but exciting.",
    "meme_caption": "Write a funny, viral-potential meme caption about {topic} in crypto/Web3. Make it relatable to degens.",
}


class ContentAgent(BaseAgent):
    """
    AI-powered content generation agent.
    
    Capabilities:
    - Generate tweets, threads, articles from project info
    - Adapt tone (degen, professional, educational, hype)
    - Include on-chain data in content
    - A/B test different angles
    """
    
    def __init__(self):
        super().__init__("ContentAgent")
    
    async def execute(self, payload: dict) -> dict:
        action = payload.get("action", "generate")
        
        if action == "generate":
            return await self._generate(payload)
        elif action == "ab_test":
            return await self._ab_test(payload)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _generate(self, payload: dict) -> dict:
        """Generate marketing content."""
        project = payload.get("project", {})
        content_type = payload.get("content_type", "tweet")
        tone = payload.get("tone", "engaging")
        chain = payload.get("chain", "ethereum")
        
        name = project.get("name", "Unknown Project")
        features = ", ".join(project.get("features", ["DeFi", "Web3"]))
        audience = project.get("audience", "crypto enthusiasts")
        
        template = CONTENT_TEMPLATES.get(content_type, CONTENT_TEMPLATES["tweet"])
        user_prompt = template.format(
            project_name=name,
            chain=chain,
            features=features,
            audience=audience,
            tone=tone,
            event=project.get("event", "major update"),
            topic=project.get("topic", "Web3 marketing"),
        )
        
        # Add on-chain context if available
        onchain_context = project.get("onchain_context", "")
        if onchain_context:
            user_prompt += f"\n\nOn-chain data to reference:\n{onchain_context}"
        
        # Add RAG context if available
        rag_context = project.get("rag_context", "")
        if rag_context:
            user_prompt += f"\n\nProject documentation context:\n{rag_context}"
        
        response = await self.llm.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.8,
            max_tokens=2048,
        )
        
        return {
            "agent": self.name,
            "content_type": content_type,
            "content": response,
            "project": name,
            "chain": chain,
            "tone": tone,
        }
    
    async def _ab_test(self, payload: dict) -> dict:
        """Generate multiple variants for A/B testing."""
        variants = []
        for i in range(3):
            result = await self._generate({
                **payload,
                "action": "generate",
            })
            result["variant"] = chr(65 + i)  # A, B, C
            variants.append(result)
        
        return {
            "agent": self.name,
            "action": "ab_test",
            "variants": variants,
            "recommendation": "Test all 3 variants and track engagement metrics",
        }
