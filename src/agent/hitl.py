import asyncio
import logging
import os
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

class HITLManager:
    def __init__(self):
        self.redis = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)

    async def request_approval(self, job_id: int, context: dict) -> bool:
        """
        Request approval for a job application.
        Returns True if approved, False if rejected.
        """
        key_pending = f"approval:{job_id}:pending"
        key_status = f"approval:{job_id}:status"
        
        # 1. Announce pending approval
        await self.redis.set(key_pending, "true")
        logger.info(f"HITL: Requesting approval for Job {job_id}. Waiting...")
        
        # 2. Wait for status change
        try:
            while True:
                status = await self.redis.get(key_status)
                if status == "APPROVED":
                    logger.info(f"HITL: Job {job_id} APPROVED.")
                    await self.redis.delete(key_pending, key_status)
                    return True
                elif status == "REJECTED":
                    logger.info(f"HITL: Job {job_id} REJECTED.")
                    await self.redis.delete(key_pending, key_status)
                    return False
                
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("HITL: Wait cancelled.")
            return False
            
    async def approve_job(self, job_id: int):
        await self.redis.set(f"approval:{job_id}:status", "APPROVED")
        
    async def reject_job(self, job_id: int):
        await self.redis.set(f"approval:{job_id}:status", "REJECTED")
