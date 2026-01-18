"""
DATAPULSE - ALL CODE IN ONE FILE
Copy each section to the corresponding file
"""

# ============================================================================
# FILE: app/api/pipelines.py
# ============================================================================
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import json

from app.database import get_db
from app.models import Pipeline
from app.schemas import PipelineCreate, PipelineUpdate, PipelineResponse
from app.services.cache import cache_service

router = APIRouter()

@router.post("/", response_model=PipelineResponse, status_code=status.HTTP_201_CREATED)
async def create_pipeline(
    pipeline: PipelineCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new pipeline"""
    stmt = select(Pipeline).where(Pipeline.name == pipeline.name)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pipeline with name '{pipeline.name}' already exists"
        )
    
    db_pipeline = Pipeline(
        **pipeline.model_dump(exclude={'tags'}),
        tags=json.dumps(pipeline.tags) if pipeline.tags else None
    )
    db.add(db_pipeline)
    await db.commit()
    await db.refresh(db_pipeline)
    
    await cache_service.delete("pipelines:all")
    
    return db_pipeline

@router.get("/", response_model=List[PipelineResponse])
async def list_pipelines(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """List all pipelines"""
    cache_key = f"pipelines:list:{skip}:{limit}:{active_only}"
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    stmt = select(Pipeline)
    if active_only:
        stmt = stmt.where(Pipeline.is_active == True)
    stmt = stmt.offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    pipelines = result.scalars().all()
    
    pipeline_list = [PipelineResponse.model_validate(p) for p in pipelines]
    await cache_service.set(cache_key, pipeline_list)
    
    return pipelines

@router.get("/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(
    pipeline_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get pipeline by ID"""
    cache_key = f"pipeline:{pipeline_id}"
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    stmt = select(Pipeline).where(Pipeline.id == pipeline_id)
    result = await db.execute(stmt)
    pipeline = result.scalar_one_or_none()
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline {pipeline_id} not found"
        )
    
    await cache_service.set(cache_key, PipelineResponse.model_validate(pipeline))
    return pipeline

@router.patch("/{pipeline_id}", response_model=PipelineResponse)
async def update_pipeline(
    pipeline_id: int,
    pipeline_update: PipelineUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update pipeline"""
    stmt = select(Pipeline).where(Pipeline.id == pipeline_id)
    result = await db.execute(stmt)
    pipeline = result.scalar_one_or_none()
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline {pipeline_id} not found"
        )
    
    update_data = pipeline_update.model_dump(exclude_unset=True, exclude={'tags'})
    for field, value in update_data.items():
        setattr(pipeline, field, value)
    
    if pipeline_update.tags is not None:
        pipeline.tags = json.dumps(pipeline_update.tags)
    
    await db.commit()
    await db.refresh(pipeline)
    
    await cache_service.delete(f"pipeline:{pipeline_id}")
    await cache_service.delete("pipelines:all")
    
    return pipeline

@router.delete("/{pipeline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pipeline(
    pipeline_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete pipeline"""
    stmt = select(Pipeline).where(Pipeline.id == pipeline_id)
    result = await db.execute(stmt)
    pipeline = result.scalar_one_or_none()
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline {pipeline_id} not found"
        )
    
    await db.delete(pipeline)
    await db.commit()
    
    await cache_service.delete(f"pipeline:{pipeline_id}")
    await cache_service.delete("pipelines:all")