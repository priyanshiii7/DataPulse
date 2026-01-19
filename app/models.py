from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class PipelineType(str, enum.Enum):
    BATCH = "batch"
    STREAMING = "streaming"
    REALTIME = "realtime"

class HealthStatus(str, enum.Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"

class Pipeline(Base):
    __tablename__ = "pipelines"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    pipeline_type = Column(Enum(PipelineType), nullable=False)
    
    # Health check configuration
    endpoint_url = Column(String(500), nullable=False)
    check_interval = Column(Integer, default=60)  # seconds
    timeout = Column(Integer, default=10)
    
    # Metadata
    owner_team = Column(String(100))
    tags = Column(Text)  # JSON string
    
    # Status
    is_active = Column(Boolean, default=True)
    current_status = Column(Enum(HealthStatus), default=HealthStatus.UNKNOWN)
    last_check_time = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    health_checks = relationship("HealthCheck", back_populates="pipeline", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="pipeline", cascade="all, delete-orphan")
    owner = relationship("User", back_populates="pipelines")


class HealthCheck(Base):
    __tablename__ = "health_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"), nullable=False, index=True)
    
    # Check results
    status = Column(Enum(HealthStatus), nullable=False)
    response_time_ms = Column(Float)
    status_code = Column(Integer)
    error_message = Column(Text)
    
    # Metrics
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    throughput = Column(Float)
    
    # Timestamp
    checked_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    pipeline = relationship("Pipeline", back_populates="health_checks")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"), nullable=False, index=True)
    
    # Alert details
    severity = Column(String(20))  # critical, warning, info
    message = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    
    # Timestamps
    triggered_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime)
    
    # Relationships
    pipeline = relationship("Pipeline", back_populates="alerts")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    company_name = Column(String, nullable=False)
    api_key = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    pipelines = relationship("Pipeline", back_populates="owner")


