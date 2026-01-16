from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from src.database.config import get_db
from src.database.models import Job, JobStatus

router = APIRouter()

@router.get("/", response_model=List[dict]) # Relaxed response model for now
async def list_jobs(
    status: Optional[JobStatus] = None,
    limit: int = 50,
    skip: int = 0,
    db: AsyncSession = Depends(get_db)
):
    query = select(Job).order_by(desc(Job.created_at)).offset(skip).limit(limit)
    
    if status is not None:
        query = query.where(Job.status == status)
        
    result = await db.execute(query)
    jobs = result.scalars().all()
    return jobs

@router.get("/{job_id}")
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Job).where(Job.id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
