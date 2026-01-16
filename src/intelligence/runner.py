import asyncio
import json
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.analytics.logger import log_event
from src.database.config import async_session_maker
from src.database.models import Job, Application, JobStatus
from src.intelligence.engine import IntelligenceEngine
from src.intelligence.graph import ApplicationWorkflow
from src.intelligence.models import UserProfile
from src.generator.renderer import PDFGenerator

logger = logging.getLogger(__name__)

class JobProcessor:
    def __init__(self):
        self.redis = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)
        self.engine = IntelligenceEngine(model_provider="openai") # Or env var
        self.workflow = ApplicationWorkflow(self.engine)
        self.pdf_generator = PDFGenerator()
        
        # Mock User Profile for V1 - typically loaded from DB
        self.user_profile = UserProfile(
            full_name="Margulan Baizhakyp",
            email="margulan@example.com",
            phone="+1-555-0199",
            linkedin_url="linkedin.com/in/margulan",
            github_url="github.com/margulan",
            skills=["Python", "FastAPI", "React", "AWS", "Docker"],
            experience_summary="Senior Software Engineer with 5 years of experience...",
            resume_raw_text="Experienced in building scalable web applications..."
        )

    async def run(self):
        logger.info("Worker started. Listening on raw_job_queue...")
        while True:
            # Blocking pop
            item = await self.redis.brpop("raw_job_queue", timeout=5)
            if not item:
                continue
            
            _, data_str = item
            try:
                job_data = json.loads(data_str)
                await self.process_job(job_data)
            except Exception as e:
                logger.error(f"Failed to process job: {e}", exc_info=True)

    async def process_job(self, job_data: dict):
        logger.info(f"Processing job: {job_data.get('title')}")
        
        async with async_session_maker() as session:
            # 1. Save Discovered Job to DB
            job = Job(
                platform_job_id=str(job_data.get("platform_job_id")),
                platform=job_data.get("platform"),
                title=job_data.get("title"),
                company=job_data.get("company"),
                url=job_data.get("url"),
                status=JobStatus.DISCOVERED,
                # In real scenario, we'd fetch full description here if missing
                # For V1 we assume scout scraped it or we fetch it now.
                # Let's assume description is just title for MVP testing if missing
                description_text=job_data.get("description", job_data.get("title")) 
            )
            session.add(job)
            await session.commit()
            
            # 2. Run Intelligence Workflow
            state = {
                "job": job,
                "user_profile": self.user_profile
            }
            
            result = await self.workflow.workflow.ainvoke(state)
            
            decision = result["decision"]
            job.fit_score = result["fit_analysis"].score
            job.fit_reasoning = result["fit_analysis"].reasoning
            
            if decision == "APPLY":
                job.status = JobStatus.TAILORED
                tailored_content = result["tailored_content"]
                
                # 3. Generate PDF
                output_dir = "data/artifacts"
                os.makedirs(output_dir, exist_ok=True)
                filename = f"{job.id}_resume.pdf"
                output_path = os.path.join(output_dir, filename)
                
                self.pdf_generator.generate_resume(
                    self.user_profile,
                    tailored_content,
                    job.title,
                    output_path
                )
                
                # 4. Create Application Record
                app = Application(
                    job_id=job.id,
                    resume_path=output_path,
                    cover_letter_path=None # Or save text
                )
                session.add(app)
                logger.info(f"Generated application for {job.title} (Score: {job.fit_score})")
                await session.commit()
                
                log_event("application_generated", {"job_id": job.id, "score": job.fit_score})
                
                # 5. Push to Apply Queue
                await self.redis.lpush("apply_queue", app.id)
                logger.info(f"Pushed Application {app.id} to apply_queue")

            else:
                job.status = JobStatus.REJECTED
                logger.info(f"Rejected job {job.title} (Score: {job.fit_score})")
                log_event("job_rejected", {"job_id": job.id, "score": job.fit_score})
                await session.commit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    processor = JobProcessor()
    asyncio.run(processor.run())
