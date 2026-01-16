import os
import random
import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from fake_useragent import UserAgent

class BrowserSession:
    def __init__(self, headless: bool = False):
        self.headless = headless
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

        # Create a context with random fingerprint
        user_agent = self.ua.random
        
        self.context = await self.browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True,
            java_script_enabled=True,
            locale="en-US",
            timezone_id="America/New_York",  # Should ideally match proxy
        )
        
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

    async def close(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
