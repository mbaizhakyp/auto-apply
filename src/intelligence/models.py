from typing import List, Optional
from pydantic import BaseModel, Field

class JobRequirements(BaseModel):
    required_skills: List[str] = Field(description="List of technical skills explicitly required")
    preferred_skills: List[str] = Field(description="List of nice-to-have skills")
    experience_level: str = Field(description="Junior, Senior, Staff, etc.")
    years_experience: Optional[int] = Field(description="Minimum years of experience required")
    remote_policy: str = Field(description="Remote, Hybrid, On-site")
    sponsorship_available: bool = Field(description="If the job description mentions visa sponsorship")

class FitAnalysis(BaseModel):
    score: int = Field(description="Fit score from 0-100")
    reasoning: str = Field(description="Brief explanation of the score")
    missing_critical_skills: List[str] = Field(description="Skills required but missing from User Profile")
    matching_skills: List[str] = Field(description="Skills present in both Job and User Profile")
    decision: str = Field(description="APPLY or REJECT")

class TailoredContent(BaseModel):
    resume_bullet_points: List[str] = Field(description="Tailored bullet points for the resume")
    cover_letter: str = Field(description="Full text of the tailored cover letter")

class UserProfile(BaseModel):
    full_name: str
    email: str
    phone: str
    linkedin_url: str
    github_url: str
    skills: List[str]
    experience_summary: str
    resume_raw_text: str
    requires_sponsorship: bool = False

