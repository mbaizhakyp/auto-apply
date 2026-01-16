import logging
import asyncio
from typing import Optional
from playwright.async_api import Page
from src.scout.browser import BrowserSession
from src.analytics.logger import log_event
from src.database.models import Application, Job
from src.agent.hitl import HITLManager

from src.agent.hitl import HITLManager
from src.agent.vision import VisionEngine
from src.intelligence.engine import IntelligenceEngine

logger = logging.getLogger(__name__)

class FormFiller:
    def __init__(self, engine: IntelligenceEngine, headless: bool = False, session_file: Optional[str] = None):
        self.browser_session = BrowserSession(headless=headless, session_file=session_file)
        self.page: Optional[Page] = None
        self.hitl = HITLManager()
        self.vision = VisionEngine(engine)

    async def start(self):
        """Initialize the browser session."""
        self.page = await self.browser_session.get_page()

    async def stop(self):
        """Close the browser session."""
        await self.browser_session.close()

    async def navigate_to_application(self, application: Application):
        """Navigate to the application URL."""
        if not self.page:
            await self.start()
        
        url = application.job.url
        logger.info(f"Navigating to application: {url}")
        
        try:
            # Login check or cookie injection would go here (Phase 3 Week 10)
            await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5) # "Thinking" time
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            raise

    async def fill_application(self, application: Application):
        """
        Orchestrate the form filling process.
        For Phase 3 MVP, this just navigates and simulates basic interaction.
        """
        await self.navigate_to_application(application)
        
        # This is where Vision-to-Action logic comes in.
        # Loop until completion or max steps
        max_steps = 10
        for step in range(max_steps):
            logger.info(f"--- Step {step + 1} / {max_steps} ---")
            
            # Analyze & Act
            action_result = await self.analyze_page(application)
            
            if action_result == "done":
                logger.info("Vision Engine indicates application is complete.")
                break
                
            if action_result == "fail":
                logger.warning("Vision Engine failed to determine next action.")
                break
                
            # Short pause between steps
            await self.browser_session.random_sleep(2, 4)
        
        # HITL Check before "Submitting" (Simulated)
        if await self.hitl.request_approval(application.job_id, {}):
            logger.info(f"APPROVED! Submitting application for job {application.job_id}...")
            # await self.submit()
            log_event("application_submitted", {"job_id": application.job_id})
        else:
            logger.warning(f"REJECTED. Skipping submission for job {application.job_id}.")
        
        logger.info(f"Finished processing application for job {application.job_id}")


    async def analyze_page(self, application: Application) -> str:
        """
        Uses VisionEngine to decide next steps. Returns status string.
        """
        logger.info("Analyzing page structure with Vision Engine...")
        
        # User context (should be richer in production)
        user_context = "User Name: Margulan Baizhakyp. Skills: Python, React." 
        
        try:
            action = await self.vision.get_next_action(self.page, user_context)
            logger.info(f"Vision Decision: {action.action_type} -> {action.selector or 'N/A'}")
            
            if action.action_type == "done":
                return "done"
            if action.action_type == "fail":
                return "fail"
            
            # Execute Action
            if action.action_type == "click" and action.selector:
                await self.page.click(action.selector)
            elif action.action_type == "type" and action.selector:
                await self.page.fill(action.selector, action.text_value or "")
            elif action.action_type == "select" and action.selector:
                await self.page.select_option(action.selector, label=action.text_value)
            elif action.action_type == "upload" and action.selector:
                # Resolve file path based on requested document type
                file_path = application.resume_path if action.text_value == "resume" else None
                if file_path:
                    await self.page.set_input_files(action.selector, file_path)
                    logger.info(f"Uploaded {file_path}")
                else:
                    logger.warning(f"Upload requested for {action.text_value} but no file found")
                    
            return "continue"
                
        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            return "fail"

    async def click_easy_apply(self):
        """
        Attempt to find and click an 'Easy Apply' button.
        """
        # Very naive implementation for demonstration
        try:
            button = self.page.get_by_text("Easy Apply", exact=False)
            if await button.count() > 0:
                await button.first.click()
                logger.info("Clicked Easy Apply")
            else:
                logger.info("Easy Apply button not found")
        except Exception as e:
            logger.warning(f"Failed to click Easy Apply: {e}")

