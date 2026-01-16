import asyncio
import random
import logging
import json
from typing import List, AsyncGenerator
from bs4 import BeautifulSoup
from redis.asyncio import Redis
from src.scout.browser import BrowserSession

logger = logging.getLogger(__name__)

class LinkedInScout:
    BASE_URL = "https://www.linkedin.com/jobs/search"

    def __init__(self):
        self.browser_session = BrowserSession(headless=False)
        # In prod, get redis URL from env
        self.redis = Redis(host='localhost', port=6379, decode_responses=True)

    async def push_to_queue(self, job_data: dict):
        """Pushes raw job data to Redis queue for processing."""
        # Check for duplicates (optional, can be done by a dedup filter later)
        # pushing to 'raw_job_queue'
        await self.redis.lpush("raw_job_queue", json.dumps(job_data))
        logger.info(f"Pushed job {job_data.get('platform_job_id')} to queue")

    async def search_jobs(self, keywords: str, location: str, limit: int = 10) -> AsyncGenerator[dict, None]:
        page = await self.browser_session.get_page()
        
        try:
            url = f"{self.BASE_URL}?keywords={keywords}&location={location}"
            logger.info(f"Navigating to {url}")
            await page.goto(url, wait_until="domcontentloaded")
            
            await asyncio.sleep(random.uniform(2, 5))
            
            jobs_processed = 0
            while jobs_processed < limit:
                # Selectors on LinkedIn change, using generic classes where possible
                job_cards = await page.locator("li .base-card").all()
                
                if not job_cards:
                    logger.warning("No job cards found. Maybe blocked or no results.")
                    break

                for card in job_cards:
                    if jobs_processed >= limit:
                        break
                    
                    try:
                        await card.scroll_into_view_if_needed()
                        await asyncio.sleep(random.uniform(0.5, 1.5))
                        
                        title_el = card.locator(".base-search-card__title")
                        company_el = card.locator(".base-search-card__subtitle")
                        link_el = card.locator("a.base-card__full-link")
                        
                        title = await title_el.inner_text()
                        company = await company_el.inner_text()
                        url = await link_el.get_attribute("href")
                        
                        if url:
                            url = url.split("?")[0]

                        job_data = {
                            "platform": "linkedin",
                            "title": title.strip(),
                            "company": company.strip(),
                            "url": url,
                            "platform_job_id": url.split("-")[-1] if url else None,
                            "status": "DISCOVERED"
                        }
                        
                        # Yield back to caller
                        yield job_data
                        
                        # Push to Redis for the Intelligence Engine
                        await self.push_to_queue(job_data)
                        
                        jobs_processed += 1
                        
                    except Exception as e:
                        logger.error(f"Error extracting card: {e}")
                        continue
                
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
                
        except Exception as e:
            logger.error(f"Search failed: {e}")
        finally:
            await self.browser_session.close()
            await self.redis.aclose()

if __name__ == "__main__":
    # Test run
    async def main():
        scout = LinkedInScout()
        async for job in scout.search_jobs("Software Engineer", "San Francisco", limit=2):
            print(f"Found and queued: {job['title']}")

    asyncio.run(main())
