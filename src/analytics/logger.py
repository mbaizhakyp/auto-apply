import json
import logging
import os
from datetime import datetime
from typing import Any, Dict

ANALYTICS_FILE = "data/logs/analytics.jsonl"

logger = logging.getLogger(__name__)

def log_event(event_type: str, data: Dict[str, Any]):
    """Log an analytics event to a JSONL file."""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        "data": data
    }
    
    try:
        with open(ANALYTICS_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        logger.error(f"Failed to write analytics event: {e}")

def get_stats() -> Dict[str, int]:
    """Calculate basic stats from the analytics file."""
    stats = {
        "jobs_discovered": 0,
        "jobs_analyzed": 0,
        "applications_generated": 0,
        "applications_submitted": 0,
        "applications_rejected": 0
    }
    
    if not os.path.exists(ANALYTICS_FILE):
        return stats
        
    try:
        with open(ANALYTICS_FILE, "r") as f:
            for line in f:
                if not line.strip(): continue
                entry = json.loads(line)
                evt = entry.get("event")
                
                if evt == "job_discovered": stats["jobs_discovered"] += 1
                elif evt == "job_analyzed": stats["jobs_analyzed"] += 1
                elif evt == "application_generated": stats["applications_generated"] += 1
                elif evt == "application_submitted": stats["applications_submitted"] += 1
                elif evt == "job_rejected": stats["applications_rejected"] += 1
                
    except Exception as e:
        logger.error(f"Failed to read analytics stats: {e}")
        
    return stats
