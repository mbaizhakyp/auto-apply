import os
import random
import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from fake_useragent import UserAgent

import logging

logger = logging.getLogger(__name__)

class BrowserSession:
    def __init__(self, headless: bool = False, session_file: Optional[str] = None):
        self.headless = headless
        self.session_file = session_file
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.playwright = None
        self.ua = UserAgent()

    async def start(self):
        self.playwright = await async_playwright().start()
        
        args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-infobars",
            "--window-position=0,0",
            "--ignore-certifcate-errors",
            "--ignore-certificate-errors-spki-list",
            "--disable-accelerated-2d-canvas",
            "--no-zygote",
            "--disable-dev-shm-usage",
        ]

        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=args,
            slow_mo=random.randint(20, 100)  # Human-like typing/action speed
        )

        # Create a context with random fingerprint or loaded state
        user_agent = self.ua.random
        
        context_args = {
            "user_agent": user_agent,
            "viewport": {"width": 1920, "height": 1080},
            "ignore_https_errors": True,
            "java_script_enabled": True,
            "locale": "en-US",
            "timezone_id": "America/New_York",
        }
        
        if self.session_file and os.path.exists(self.session_file):
            logger.info(f"Loading browser session from {self.session_file}")
            context_args["storage_state"] = self.session_file
        
        self.context = await self.browser.new_context(**context_args)
        
        # Anti-detect injections
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

    async def get_page(self) -> Page:
        if not self.context:
            await self.start()
        return await self.context.new_page()

    async def save_state(self):
        """Save the current session state (cookies, local storage) to file."""
        if self.context and self.session_file:
            await self.context.storage_state(path=self.session_file)
            logger.info(f"Saved browser session to {self.session_file}")

    async def random_sleep(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Sleep for a random amount of time to simulate human thinking."""
        sleep_time = random.uniform(min_seconds, max_seconds)
        logger.debug(f"Sleeping for {sleep_time:.2f}s")
        await asyncio.sleep(sleep_time)

    async def close(self):
        try:
            if self.context and self.session_file:
                # Auto-save on close
                await self.save_state()
                
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.error(f"Error closing browser session: {e}")
