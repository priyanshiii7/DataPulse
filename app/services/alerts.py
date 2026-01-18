import httpx
from app.models import Pipeline, HealthCheck
from app.config import get_settings

settings = get_settings()

class AlertService:
    async def send_alert(self, pipeline: Pipeline, health_check: HealthCheck):
        """Send alert notification"""
        message = self._format_message(pipeline, health_check)
        
        if settings.SLACK_WEBHOOK_URL:
            await self._send_slack(message)
    
    def _format_message(self, pipeline: Pipeline, health_check: HealthCheck) -> str:
        """Format alert message"""
        return f"""
🚨 Pipeline Alert: {pipeline.name}
Status: {health_check.status.value.upper()}
Error: {health_check.error_message or 'N/A'}
Time: {health_check.checked_at.strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
    
    async def _send_slack(self, message: str):
        """Send to Slack"""
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    settings.SLACK_WEBHOOK_URL,
                    json={"text": message}
                )
        except Exception as e:
            print(f"Slack alert failed: {e}")

alert_service = AlertService()