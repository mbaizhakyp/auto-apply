import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from src.intelligence.models import FitAnalysis, TailoredContent, JobRequirements, UserProfile
from src.intelligence.prompts import FIT_ANALYSIS_PROMPT, TAILORING_PROMPT

class IntelligenceEngine:
    def __init__(self, model_provider: str = "openai"):
        self.llm = self._get_llm(model_provider)

    def _get_llm(self, provider: str) -> BaseChatModel:
        if provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found")
            return ChatAnthropic(model="claude-3-5-sonnet-20240620", api_key=api_key)
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found")
            return ChatOpenAI(model="gpt-4o", api_key=api_key)

    async def analyze_fit(self, job_description: str, user_profile: UserProfile) -> FitAnalysis:
        structured_llm = self.llm.with_structured_output(FitAnalysis)
        chain = FIT_ANALYSIS_PROMPT | structured_llm
        
        result = await chain.ainvoke({
            "job_description": job_description,
            "user_profile": user_profile.model_dump_json()
        })
        return result

    async def extract_requirements(self, job_description: str) -> JobRequirements:
        # We can combine this with analyze_fit or keep separate. 
        # For cost efficiency, maybe separate or one large prompt.
        # Let's keep separate for clarity or use a combined model if needed.
        # For now, I'll use a separate call or specific prompt if needed.
        # Actually, let's just use with_structured_output on a simple extraction prompt if needed,
        # but FitAnalysis covers matching/missing skills which is usually enough for decision.
        # If we need structured "JobRequirements" db storage, we can add a method.
        
        structured_llm = self.llm.with_structured_output(JobRequirements)
        prompt = FIT_ANALYSIS_PROMPT # Re-using similar context but asking for requirements
        # Ideally we have a dedicated prompt. Let's make a quick dynamic one or just assume FitAnalysis is enough for flow 1.
        # But the architecture asked for "Extraction".
        # Let's add a simple extraction method.
        pass

    async def tailor_application(self, job_description: str, job_requirements: list[str], user_profile: UserProfile) -> TailoredContent:
        structured_llm = self.llm.with_structured_output(TailoredContent)
        chain = TAILORING_PROMPT | structured_llm
        
        result = await chain.ainvoke({
            "job_description": job_description,
            "job_requirements": ", ".join(job_requirements),
            "resume_text": user_profile.resume_raw_text
        })
        return result
