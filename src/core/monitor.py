"""
Metrics Collector - Track agent performance and content generation stats.
"""

import time
import logging
from typing import Dict, List
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger("mimo-marketing.monitor")


@dataclass
class MetricEntry:
    """Single metric data point."""
    timestamp: float
    name: str
    value: float = 1.0


class MetricsCollector:
    """
    Collect and aggregate metrics for the agent system.
    
    Tracks:
    - Content generation counts by type
    - Agent latency and throughput
    - Token consumption
    - Error rates
    """
    
    def __init__(self):
        self._entries: List[MetricEntry] = []
        self._counters: Dict[str, int] = {}
        self._start_time = time.time()
    
    def record(self, name: str, value: float = 1.0):
        """Record a metric event."""
        entry = MetricEntry(
            timestamp=time.time(),
            name=name,
            value=value,
        )
        self._entries.append(entry)
        self._counters[name] = self._counters.get(name, 0) + value
    
    def summary(self) -> Dict:
        """Get metrics summary."""
        uptime = time.time() - self._start_time
        return {
            "uptime_seconds": round(uptime, 1),
            "total_events": len(self._entries),
            "counters": self._counters,
            "events_per_minute": round(
                len(self._entries) / max(uptime / 60, 1), 2
            ),
        }
