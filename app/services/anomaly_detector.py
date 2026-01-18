from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import statistics

from app.models import HealthCheck, Pipeline, HealthStatus

class AnomalyDetector:
    def __init__(self, z_threshold: float = 2.5):
        self.z_threshold = z_threshold

    async def detect_response_time_anomaly(
            self,
            db: AsyncSession,
            pipeline_id: int,
            hours_lookback: int = 24
    ) -> dict:
        """
        Detect if current response time is anomalous
        
        Returns:
            {
                "is_anomaly": bool,
                "current_value": float,
                "mean": float,
                "std_dev": float,
                "z_score": float,
                "threshold": float,
                "confidence": str
            }
        
        """

        since = datetime.utcnow() - timedelta(hours=hours_lookback)
        stmt = (
            select(HealthCheck.response_time_ms)
            .where(HealthCheck.pipeline_id == pipeline_id)
            .where(HealthCheck.checked_at >= since)
            .where(HealthCheck.response_time_ms.isnot(None))
            .order_by(HealthCheck.checked_at.desc())
        )


        result = await db.execute(stmt)
        response_times = [row[0] for row in result.fetchall()]

        if len(response_times) < 10:
            return {
                "is_anomaly" : False,
                "current_value" : response_times[0] if response_times else None,
                "mean" : None,
                "std_dev" : None,
                "z_score" : None,
                "threshold" : self.z_threshold,
                "confidence" : "insufficient_data"
            }
        
        current_value = response_times[0]
        historical_values = response_times[1:]

        mean = statistics.mean(historical_values)
        std_dev = statistics.stdev(historical_values)

        if std_dev == 0:
            z_score = 0

        else: 
            z_score = abs((current_value - mean) / std_dev)

        is_anomaly = z_score > self.z_threshold

        if z_score > 3:
            confidence = "very_high"
        elif z_score > 2.5:
            confidence = "high"
        elif z_score > 2:
            confidence = "medium"
        else:
            confidence = "normal"

        return {
            "is_anomaly": is_anomaly,
            "current_value": round(current_value, 2),
            "mean": round(mean, 2),
            "std_dev": round(std_dev, 2),
            "z_score": round(z_score, 2),
            "threshold": self.z_threshold,
            "confidence": confidence,
            "sample_size": len(historical_values)
        }
    
    async def detect_error_rate_spike(
            self, 
            db: AsyncSession,
            pipeline_id: int,
            hours_lookback: int = 24
    ) -> dict:
        since = datetime.utcnow() - timedelta(hours=hours_lookback)

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
        
        if total_checks < 10:
            return {
                "is_anomaly": False,
                "error_rate": 0,
                "confidence": "insufficient_data"
            }
        
        error_rate = (failed_checks / total_checks) * 100
        
        # Simple threshold-based detection
        is_anomaly = error_rate > 20  # More than 20% errors
        
        return {
            "is_anomaly": is_anomaly,
            "error_rate": round(error_rate, 2),
            "failed_checks": failed_checks,
            "total_checks": total_checks,
            "confidence": "high" if error_rate > 20 else "normal"
        }

# Global instance
anomaly_detector = AnomalyDetector()
        
        