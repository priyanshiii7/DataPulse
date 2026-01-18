from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta
from app.services.anomaly_detector import anomaly_detector

from app.database import get_db
from app.models import Pipeline, HealthCheck, HealthStatus
from app.schemas import DashboardStats, PipelineMetrics
from app.services.cache import cache_service

router = APIRouter()

@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics"""
    cache_key = "metrics:dashboard"
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    total_stmt = select(func.count(Pipeline.id))
    total_result = await db.execute(total_stmt)
    total_pipelines = total_result.scalar()
    
    healthy_stmt = select(func.count(Pipeline.id)).where(
        Pipeline.current_status == HealthStatus.HEALTHY
    )
    healthy_result = await db.execute(healthy_stmt)
    healthy_pipelines = healthy_result.scalar()
    
    degraded_stmt = select(func.count(Pipeline.id)).where(
        Pipeline.current_status == HealthStatus.DEGRADED
    )
    degraded_result = await db.execute(degraded_stmt)
    degraded_pipelines = degraded_result.scalar()
    
    down_stmt = select(func.count(Pipeline.id)).where(
        Pipeline.current_status == HealthStatus.DOWN
    )
    down_result = await db.execute(down_stmt)
    down_pipelines = down_result.scalar()
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    checks_stmt = select(func.count(HealthCheck.id)).where(
        HealthCheck.checked_at >= today
    )
    checks_result = await db.execute(checks_stmt)
    total_checks_today = checks_result.scalar()
    
    avg_stmt = select(func.avg(HealthCheck.response_time_ms)).where(
        HealthCheck.checked_at >= today
    )
    avg_result = await db.execute(avg_stmt)
    avg_response_time = avg_result.scalar() or 0.0
    
    stats = DashboardStats(
        total_pipelines=total_pipelines,
        healthy_pipelines=healthy_pipelines,
        degraded_pipelines=degraded_pipelines,
        down_pipelines=down_pipelines,
        total_checks_today=total_checks_today,
        avg_response_time=round(avg_response_time, 2)
    )
    
    await cache_service.set(cache_key, stats, ttl=30)
    
    return stats

@router.get("/pipeline/{pipeline_id}", response_model=PipelineMetrics)
async def get_pipeline_metrics(
    pipeline_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get pipeline metrics"""
    pipeline_stmt = select(Pipeline).where(Pipeline.id == pipeline_id)
    pipeline_result = await db.execute(pipeline_stmt)
    pipeline = pipeline_result.scalar_one_or_none()
    
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    since = datetime.utcnow() - timedelta(hours=24)
    
    total_stmt = select(func.count(HealthCheck.id)).where(
        HealthCheck.pipeline_id == pipeline_id,
        HealthCheck.checked_at >= since
    )
    total_result = await db.execute(total_stmt)
    total_checks = total_result.scalar()
    
    failed_stmt = select(func.count(HealthCheck.id)).where(
        HealthCheck.pipeline_id == pipeline_id,
        HealthCheck.checked_at >= since,
        HealthCheck.status != HealthStatus.HEALTHY
    )
    failed_result = await db.execute(failed_stmt)
    failed_checks = failed_result.scalar()
    
    avg_stmt = select(func.avg(HealthCheck.response_time_ms)).where(
        HealthCheck.pipeline_id == pipeline_id,
        HealthCheck.checked_at >= since
    )
    avg_result = await db.execute(avg_stmt)
    avg_response_time = avg_result.scalar() or 0.0
    
    uptime = ((total_checks - failed_checks) / total_checks * 100) if total_checks > 0 else 100.0
    
    recent_stmt = (
        select(HealthCheck)
        .where(HealthCheck.pipeline_id == pipeline_id)
        .order_by(desc(HealthCheck.checked_at))
        .limit(20)
    )
    recent_result = await db.execute(recent_stmt)
    last_24h_checks = recent_result.scalars().all()
    
    return PipelineMetrics(
        pipeline_id=pipeline.id,
        pipeline_name=pipeline.name,
        current_status=pipeline.current_status,
        uptime_percentage=round(uptime, 2),
        avg_response_time_ms=round(avg_response_time, 2),
        total_checks=total_checks,
        failed_checks=failed_checks,
        last_24h_checks=last_24h_checks
    )

@router.get("/pipeline/{pipeline_id}/anomalies")
async def get_pipeline_anomalies(
    pipeline_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get anomaly detection results for a pipeline"""
    # Verify pipeline exists
    pipeline_stmt = select(Pipeline).where(Pipeline.id == pipeline_id)
    pipeline_result = await db.execute(pipeline_stmt)
    pipeline = pipeline_result.scalar_one_or_none()
    
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    # Detect anomalies
    response_time_anomaly = await anomaly_detector.detect_response_time_anomaly(
        db, pipeline_id
    )
    
    error_rate_anomaly = await anomaly_detector.detect_error_rate_spike(
        db, pipeline_id
    )
    
    return {
        "pipeline_id": pipeline_id,
        "pipeline_name": pipeline.name,
        "response_time_analysis": response_time_anomaly,
        "error_rate_analysis": error_rate_anomaly,
        "overall_status": "anomaly_detected" if (
            response_time_anomaly["is_anomaly"] or 
            error_rate_anomaly["is_anomaly"]
        ) else "normal"
    }