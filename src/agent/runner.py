import asyncio
import json
import logging
import os
from dotenv import load_dotenv
from redis.asyncio import Redis
from sqlalchemy import select
from src.database.config import async_session_maker
from src.database.models import Application
from src.agent.filler import FormFiller

load_dotenv()
logger = logging.getLogger(__name__)

class AgentRunner:
    def __init__(self):
        self.redis = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)
        self.filler = FormFiller(headless=False) # Headful for debugging/Vision

    async def run(self):
        logger.info("Agent Runner started. Listening on apply_queue...")
        try:
            while True:
                item = await self.redis.brpop("apply_queue", timeout=5)
                if not item:
                    continue
                
                _, app_id = item
                try:
                    await self.process_application(int(app_id))
                except Exception as e:
                    logger.error(f"Failed to process application {app_id}: {e}", exc_info=True)
        finally:
            await self.filler.stop()

    async def process_application(self, app_id: int):
        logger.info(f"Processing application ID: {app_id}")
        
        async with async_session_maker() as session:
            stmt = select(Application).where(Application.id == app_id)
            result = await session.execute(stmt)
            application = result.scalar_one_or_none()
            
            if not application:
                logger.error(f"Application {app_id} not found")
                return
            
            # Lazy load job to ensure URL is available
            await session.refresh(application, ["job"])
            
            await self.filler.fill_application(application)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    runner = AgentRunner()
    asyncio.run(runner.run())
