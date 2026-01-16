from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from src.database.config import get_db
from src.database.models import Application, Job
from src.agent.hitl import HITLManager

router = APIRouter()
hitl = HITLManager()

@router.get("/", response_model=List[dict])
async def list_applications(
    limit: int = 50,
    skip: int = 0,
    db: AsyncSession = Depends(get_db)
):
    query = select(Application).order_by(desc(Application.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    apps = result.scalars().all()
    return apps

@router.post("/{job_id}/approve")
async def approve_application(job_id: int):
    """
    Approves the landing application for the given job.
    Triggers the agent to proceed.
    """
    success = await hitl.approve_job(job_id)
    if not success:
         # Maybe it wasn't pending?
         return {"status": "ignored", "detail": "Job not pending approval"}
    return {"status": "approved", "job_id": job_id}

@router.post("/{job_id}/reject")
async def reject_application(job_id: int):
    """
    Rejects the application.
    """
    success = await hitl.reject_job(job_id)
    if not success:
         return {"status": "ignored", "detail": "Job not pending approval"}
    return {"status": "rejected", "job_id": job_id}
