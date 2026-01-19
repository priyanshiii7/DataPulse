import asyncio
import httpx
from datetime import datetime
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import Pipeline, HealthCheck, HealthStatus
from app.config import get_settings
from app.services.alerts import alert_service

settings = get_settings()

class HealthCheckWorker:
    def __init__(self):
        self.running = False
    
    async def run(self):
        """Main worker loop"""
        self.running = True
        print(" Health check worker started")
        
        while self.running:
            try:
                await self.check_all_pipelines()
                await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL)
            except Exception as e:
                print(f"Worker error: {e}")
                await asyncio.sleep(10)
    
    async def check_all_pipelines(self):
        """Check all active pipelines"""
        async with AsyncSessionLocal() as db:
            stmt = select(Pipeline).where(Pipeline.is_active == True)
            result = await db.execute(stmt)
            pipelines = result.scalars().all()
            
            if not pipelines:
                return
            
            print(f"⏰ Checking {len(pipelines)} pipelines...")
            
            tasks = [
                self.check_pipeline(pipeline, db)
                for pipeline in pipelines
            ]
            
            sem = asyncio.Semaphore(settings.MAX_CONCURRENT_CHECKS)
            async def bounded_check(task):
                async with sem:
                    return await task
            
            await asyncio.gather(*[bounded_check(task) for task in tasks])
    
    async def check_pipeline(self, pipeline: Pipeline, db):
        """Check single pipeline"""
        start_time = datetime.utcnow()
        
        try:
            async with httpx.AsyncClient(timeout=pipeline.timeout) as client:
                response = await client.get(str(pipeline.endpoint_url))
                
                response_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                if response.status_code == 200:
                    status = HealthStatus.HEALTHY
                elif 200 <= response.status_code < 300:
                    status = HealthStatus.HEALTHY
                elif 400 <= response.status_code < 500:
                    status = HealthStatus.DEGRADED
                else:
                    status = HealthStatus.DOWN
                
                health_check = HealthCheck(
                    pipeline_id=pipeline.id,
                    status=status,
                    response_time_ms=response_time_ms,
                    status_code=response.status_code,
                    checked_at=datetime.utcnow()
                )
                
                db.add(health_check)
                
                old_status = pipeline.current_status
                pipeline.current_status = status
                pipeline.last_check_time = datetime.utcnow()
                
                await db.commit()
                
                if old_status != status and status != HealthStatus.HEALTHY:
                    await alert_service.send_alert(pipeline, health_check)
                
                print(f"  {pipeline.name}: {status.value} ({response_time_ms:.0f}ms)")
                
        except Exception as e:
            health_check = HealthCheck(
                pipeline_id=pipeline.id,
                status=HealthStatus.DOWN,
                error_message=str(e),
                checked_at=datetime.utcnow()
            )
            
            db.add(health_check)
            pipeline.current_status = HealthStatus.DOWN
            pipeline.last_check_time = datetime.utcnow()
            
            await db.commit()
            
            print(f"{pipeline.name}: DOWN - {str(e)}")