from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from datetime import datetime, timedelta

from app.database import get_db
from app.models import HealthCheck, Pipeline
from app.schemas import HealthCheckResponse

router = APIRouter()

@router.get("/pipeline/{pipeline_id}", response_model=List[HealthCheckResponse])
async def get_pipeline_health_checks(
    pipeline_id: int,
    limit: int = 100,
    hours: int = 24,
    db: AsyncSession = Depends(get_db)
):
    """Get recent health checks for a pipeline"""
    pipeline_stmt = select(Pipeline).where(Pipeline.id == pipeline_id)
    pipeline_result = await db.execute(pipeline_stmt)
    if not pipeline_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    since = datetime.utcnow() - timedelta(hours=hours)
    stmt = (
        select(HealthCheck)
        .where(HealthCheck.pipeline_id == pipeline_id)
        .where(HealthCheck.checked_at >= since)
        .order_by(desc(HealthCheck.checked_at))
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/recent", response_model=List[HealthCheckResponse])
async def get_recent_health_checks(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get most recent health checks"""
    stmt = (
        select(HealthCheck)
        .order_by(desc(HealthCheck.checked_at))
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    return result.scalars().all()