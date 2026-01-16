import base64
import logging
from typing import Dict, Any, List
from playwright.async_api import Page
from langchain_core.messages import HumanMessage, SystemMessage
from src.intelligence.engine import IntelligenceEngine
from src.agent.models import UIAction

logger = logging.getLogger(__name__)

class VisionEngine:
    """
    Handles the 'Vision' part of the agent: modifying the page for better visibility,
    capturing screenshots, and extracting the accessibility tree.
    """
    def __init__(self, engine: IntelligenceEngine):
        self.llm = engine.llm

    async def get_next_action(self, page: Page, user_context: str) -> UIAction:
        """
        Analyzes the page state and returns the next action to take.
        """
        state = await self.capture_state(page)
        
        # Construct Multimodal Prompt
        system_prompt = """
        You are an autonomous agent filling out a job application form.
        Your goal is to navigate through the form, fill in the user's details, and submit.
        
        Input:
        1. Screenshot of the current page.
        2. Simplified Accessibility Tree (DOM).
        3. User's Profile Context.
        
        Output:
        Structure your response as a UIAction.
        - If you see a field to fill, return 'type' with the selector and value from user context.
        - If you see a dropdown, if it's a standard <select>, return 'select'. If custom, 'click' to open then 'click' option.
        - If you see a file upload for Resume/Cover Letter, return 'upload' with value 'resume' or 'cover_letter'.
        - If you see a button to proceed (Next, Continue, Submit), return 'click'.
        - If the application is finished, return 'done'.
        """
        
        user_message_content = [
            {"type": "text", "text": f"User Context: {user_context}\n\nAccessibility Tree:\n{state['accessibility_tree']}"},
            {
                "type": "image_url", 
                "image_url": {"url": f"data:image/jpeg;base64,{state['screenshot']}"}
            }
        ]
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message_content)
        ]
        
        structured_llm = self.llm.with_structured_output(UIAction)
        action = await structured_llm.ainvoke(messages)
        return action

    async def capture_state(self, page: Page) -> Dict[str, Any]:
        """
        Captures the current state of the page:
        1. Screenshot (base64)
        2. Accessibility Tree (simplified DOM)
        """
        # 1. Clean up page (remove sticky headers/footers if needed, highlight interactive elements)
        # For now, we just screenshot.
        
        # Capture Screenshot
        screenshot_bytes = await page.screenshot(type="jpeg", quality=60, full_page=False)
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
        
        # 2. Extract HTML (Fallback since accessibility tree is missing in this env)
        # Using raw HTML, possibly truncated
        html_content = await page.content()
        # Simple truncation to avoid token limits
        html_content = html_content[:20000] 
        
        return {
            "screenshot": screenshot_b64,
            "accessibility_tree": html_content, # Renaming would break prompt key, keeping name for now but sending HTML
            "url": page.url
        }

    async def highlight_element(self, page: Page, selector: str):
        """Debug helper to highlight an element."""
        try:
            locator = page.locator(selector).first
            await locator.evaluate("el => el.style.border = '3px solid red'")
        except Exception as e:
            logger.warning(f"Failed to highlight {selector}: {e}")

