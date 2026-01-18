from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class PipelineType(str, Enum):
    BATCH = "batch"
    STREAMING = "streaming"
    REALTIME = "realtime"

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"

# Pipeline Schemas
class PipelineCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    pipeline_type: PipelineType
    endpoint_url: str  # Changed from HttpUrl to str for flexibility
    check_interval: int = Field(default=60, ge=10, le=3600)
    timeout: int = Field(default=10, ge=5, le=60)
    owner_team: Optional[str] = None
    tags: Optional[List[str]] = []
    
    @field_validator('endpoint_url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format"""
        if not v:
            raise ValueError('URL cannot be empty')
        
        v = v.strip()
        
        # Must start with http:// or https://
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        
        # Basic sanity check
        if len(v) < 10:
            raise ValueError('URL seems too short')
        
        return v

class PipelineUpdate(BaseModel):
    description: Optional[str] = None
    endpoint_url: Optional[str] = None
    check_interval: Optional[int] = Field(default=None, ge=10, le=3600)
    timeout: Optional[int] = Field(default=None, ge=5, le=60)
    owner_team: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None
    
    @field_validator('endpoint_url')
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL format"""
        if v is None:
            return v
        
        v = v.strip()
        
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        
        return v

class PipelineResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    pipeline_type: PipelineType
    endpoint_url: str
    current_status: HealthStatus
    is_active: bool
    owner_team: Optional[str]
    last_check_time: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Health Check Schemas
class HealthCheckResponse(BaseModel):
    id: int
    pipeline_id: int
    status: HealthStatus
    response_time_ms: Optional[float]
    status_code: Optional[int]
    error_message: Optional[str]
    checked_at: datetime
    
    class Config:
        from_attributes = True

# Metrics Schemas
class PipelineMetrics(BaseModel):
    pipeline_id: int
    pipeline_name: str
    current_status: HealthStatus
    uptime_percentage: float
    avg_response_time_ms: float
    total_checks: int
    failed_checks: int
    last_24h_checks: List[HealthCheckResponse]

class DashboardStats(BaseModel):
    total_pipelines: int
    healthy_pipelines: int
    degraded_pipelines: int
    down_pipelines: int
    total_checks_today: int
    avg_response_time: float