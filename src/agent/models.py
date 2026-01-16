from typing import Optional, Literal
from pydantic import BaseModel, Field

class UIAction(BaseModel):
    action_type: Literal["click", "type", "select", "upload", "scroll", "wait", "done", "fail"] = Field(description="The type of action to perform")
    selector: Optional[str] = Field(description="CSS selector or Playwright selector to interact with")
    text_value: Optional[str] = Field(description="Text to type if action_type is 'type'")
    reasoning: str = Field(description="Reasoning for this action based on the visual state")
