from datetime import datetime, timezone
import enum
from typing import Optional, List
from sqlalchemy import Column, String, Integer, DateTime, JSON, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.config import Base

class JobStatus(str, enum.Enum):
    DISCOVERED = "DISCOVERED"
    TAILORED = "TAILORED"
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"
    INTERVIEW = "INTERVIEW"

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    platform_job_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    platform: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    company: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String)
    
    # Raw Content
    description_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Analysis
    fit_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fit_reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus), default=JobStatus.DISCOVERED, index=True
    )
    
    requires_sponsorship: Mapped[bool] = mapped_column(default=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )

    applications: Mapped[List["Application"]] = relationship(
        "Application", back_populates="job", cascade="all, delete-orphan"
    )

class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    
    # Artifacts
    resume_path: Mapped[str] = mapped_column(String)
    cover_letter_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # State
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    screenshot_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    logs: Mapped[List[dict]] = mapped_column(JSON, default=list)

    job: Mapped["Job"] = relationship("Job", back_populates="applications")
