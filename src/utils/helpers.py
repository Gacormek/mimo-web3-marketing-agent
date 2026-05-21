"""
Utility functions for MiMo Web3 Marketing Agent.
"""

import hashlib
import json
import re
from typing import Any, Dict


def truncate_text(text: str, max_length: int = 280) -> str:
    """Truncate text to fit tweet length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def extract_hashtags(text: str) -> list[str]:
    """Extract hashtags from text."""
    return re.findall(r"#(\w+)", text)


def extract_mentions(text: str) -> list[str]:
    """Extract @mentions from text."""
    return re.findall(r"@(\w+)", text)


def content_hash(content: str) -> str:
    """Generate a hash for content deduplication."""
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def safe_json_parse(text: str) -> Dict[str, Any]:
    """Safely parse JSON from LLM output, handling markdown code blocks."""
    # Strip markdown code blocks
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove first and last lines (``` markers)
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find JSON object in the text
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {"raw_text": text}


def format_number(n: int) -> str:
    """Format large numbers for display."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)
